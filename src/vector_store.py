"""FAISS vector index creation, persistence, loading, and search."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import (
    FAISS_INDEX_DIR,
    RETRIEVAL_K,
    get_embedding_model,
    get_google_api_key,
)


INDEX_FILENAME = "index.faiss"
DOCUMENTS_FILENAME = "documents.json"
MANIFEST_FILENAME = "manifest.json"


class VectorStoreError(RuntimeError):
    """Raised when vector index operations fail."""


@dataclass(frozen=True)
class SearchResult:
    """A retrieved document and its cosine similarity score."""

    document: Document
    score: float


def create_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """Create the configured Gemini embedding model."""

    api_key = get_google_api_key()
    model_name = get_embedding_model()

    try:
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=api_key,
        )
    except Exception as exc:
        raise VectorStoreError(
            "No se pudo inicializar el modelo de embeddings de Gemini: "
            f"{exc}"
        ) from exc


def _validate_embedding_matrix(
    matrix: np.ndarray,
    expected_rows: int,
) -> None:
    """Validate shape and values returned by the embedding API."""

    if matrix.ndim != 2:
        raise VectorStoreError(
            "La API de embeddings devolvió una matriz con formato inválido."
        )

    if matrix.shape[0] != expected_rows:
        raise VectorStoreError(
            "La cantidad de embeddings no coincide con "
            "la cantidad de chunks."
        )

    if matrix.shape[1] == 0:
        raise VectorStoreError(
            "Los embeddings no tienen dimensiones."
        )

    if not np.isfinite(matrix).all():
        raise VectorStoreError(
            "Los embeddings contienen valores no numéricos o infinitos."
        )

    norms = np.linalg.norm(matrix, axis=1)

    if np.any(norms == 0):
        raise VectorStoreError(
            "La API devolvió al menos un embedding con norma cero."
        )


def build_vector_index(
    chunks: list[Document],
    embeddings: GoogleGenerativeAIEmbeddings,
) -> tuple[faiss.Index, int]:
    """Embed all chunks and build a cosine-similarity FAISS index."""

    if not chunks:
        raise VectorStoreError(
            "No hay chunks disponibles para construir el índice."
        )

    texts = [chunk.page_content for chunk in chunks]

    try:
        raw_vectors = embeddings.embed_documents(texts)
    except Exception as exc:
        raise VectorStoreError(
            "Falló la generación de embeddings con Gemini. "
            "Revisá la API key, el modelo y la cuota disponible. "
            f"Detalle: {exc}"
        ) from exc

    matrix = np.asarray(raw_vectors, dtype=np.float32)
    _validate_embedding_matrix(matrix, expected_rows=len(chunks))

    faiss.normalize_L2(matrix)

    vector_dimension = int(matrix.shape[1])
    index = faiss.IndexFlatIP(vector_dimension)
    index.add(matrix)

    if index.ntotal != len(chunks):
        raise VectorStoreError(
            "FAISS no almacenó la cantidad esperada de vectores."
        )

    return index, vector_dimension


def save_vector_index(
    index: faiss.Index,
    documents: list[Document],
    vector_dimension: int,
    index_dir: Path = FAISS_INDEX_DIR,
) -> None:
    """Persist the FAISS index, documents, metadata, and manifest."""

    if index.ntotal != len(documents):
        raise VectorStoreError(
            "No se puede guardar el índice: la cantidad de vectores "
            "no coincide con la cantidad de documentos."
        )

    index_path = index_dir / INDEX_FILENAME
    documents_path = index_dir / DOCUMENTS_FILENAME
    manifest_path = index_dir / MANIFEST_FILENAME

    document_payload = [
        {
            "page_content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]

    manifest: dict[str, Any] = {
        "format_version": 1,
        "embedding_model": get_embedding_model(),
        "vector_dimension": vector_dimension,
        "document_count": len(documents),
        "similarity_metric": "cosine_similarity",
        "created_at_utc": datetime.now(UTC).isoformat(),
    }

    try:
        index_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(index, str(index_path))

        documents_path.write_text(
            json.dumps(
                document_payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        manifest_path.write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        raise VectorStoreError(
            f"No se pudo guardar el índice en '{index_dir}': {exc}"
        ) from exc

    required_files = (
        index_path,
        documents_path,
        manifest_path,
    )

    missing_files = [
        path.name for path in required_files if not path.is_file()
    ]

    if missing_files:
        raise VectorStoreError(
            "El índice quedó incompleto. Faltan: "
            + ", ".join(missing_files)
        )


def load_vector_index(
    index_dir: Path = FAISS_INDEX_DIR,
) -> tuple[faiss.Index, list[Document], dict[str, Any]]:
    """Load an existing local FAISS index and its document records."""

    index_path = index_dir / INDEX_FILENAME
    documents_path = index_dir / DOCUMENTS_FILENAME
    manifest_path = index_dir / MANIFEST_FILENAME

    missing_files = [
        path.name
        for path in (index_path, documents_path, manifest_path)
        if not path.is_file()
    ]

    if missing_files:
        raise VectorStoreError(
            "No existe un índice FAISS completo. Faltan: "
            + ", ".join(missing_files)
        )

    try:
        index = faiss.read_index(str(index_path))

        raw_documents = json.loads(
            documents_path.read_text(encoding="utf-8")
        )

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        raise VectorStoreError(
            f"No se pudo cargar el índice local: {exc}"
        ) from exc

    if not isinstance(raw_documents, list):
        raise VectorStoreError(
            "documents.json no contiene una lista válida."
        )

    documents: list[Document] = []

    for position, item in enumerate(raw_documents):
        if not isinstance(item, dict):
            raise VectorStoreError(
                f"Registro inválido en documents.json: posición {position}."
            )

        page_content = item.get("page_content")
        metadata = item.get("metadata")

        if not isinstance(page_content, str) or not page_content.strip():
            raise VectorStoreError(
                f"Contenido inválido en documents.json: posición {position}."
            )

        if not isinstance(metadata, dict):
            raise VectorStoreError(
                f"Metadata inválida en documents.json: posición {position}."
            )

        documents.append(
            Document(
                page_content=page_content,
                metadata=metadata,
            )
        )

    configured_model = get_embedding_model()
    stored_model = manifest.get("embedding_model")

    if stored_model != configured_model:
        raise VectorStoreError(
            "El índice fue generado con un modelo de embeddings distinto. "
            f"Índice: '{stored_model}'. Configuración actual: "
            f"'{configured_model}'."
        )

    expected_dimension = manifest.get("vector_dimension")

    if expected_dimension != index.d:
        raise VectorStoreError(
            "La dimensión registrada en manifest.json "
            "no coincide con el índice FAISS."
        )

    if index.ntotal != len(documents):
        raise VectorStoreError(
            "La cantidad de vectores del índice no coincide "
            "con documents.json."
        )

    return index, documents, manifest


def semantic_search(
    query: str,
    index: faiss.Index,
    documents: list[Document],
    embeddings: GoogleGenerativeAIEmbeddings,
    k: int = RETRIEVAL_K,
) -> list[SearchResult]:
    """Retrieve the most similar documents for a query."""

    normalized_query = query.strip()

    if not normalized_query:
        raise VectorStoreError(
            "La consulta de búsqueda no puede estar vacía."
        )

    if k <= 0:
        raise VectorStoreError(
            "La cantidad de resultados debe ser mayor que cero."
        )

    if index.ntotal == 0 or not documents:
        raise VectorStoreError(
            "El índice cargado no contiene documentos."
        )

    try:
        raw_query_vector = embeddings.embed_query(normalized_query)
    except Exception as exc:
        raise VectorStoreError(
            "Falló la generación del embedding de consulta. "
            f"Detalle: {exc}"
        ) from exc

    query_matrix = np.asarray(
        [raw_query_vector],
        dtype=np.float32,
    )

    _validate_embedding_matrix(query_matrix, expected_rows=1)

    if query_matrix.shape[1] != index.d:
        raise VectorStoreError(
            "El embedding de la consulta tiene una dimensión distinta "
            "a la utilizada para construir el índice."
        )

    faiss.normalize_L2(query_matrix)

    result_count = min(k, len(documents))
    scores, positions = index.search(query_matrix, result_count)

    results: list[SearchResult] = []

    for score, position in zip(scores[0], positions[0], strict=True):
        if position < 0:
            continue

        results.append(
            SearchResult(
                document=documents[int(position)],
                score=float(score),
            )
        )

    return results