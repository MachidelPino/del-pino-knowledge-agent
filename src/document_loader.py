"""PDF loading and text chunking utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENTS_DIR,
    EXPECTED_PDF_FILES,
)


class DocumentLoadError(RuntimeError):
    """Raised when source documents cannot be loaded correctly."""


@dataclass(frozen=True)
class DocumentLoadSummary:
    """Summary of the PDF loading process."""

    pdf_count: int
    total_pages: int
    loaded_pages: int
    skipped_empty_pages: int


def _normalize_text(text: str) -> str:
    """Normalize extraction noise without aggressively altering content."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.strip() for line in normalized.splitlines())
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()


def _validate_documents_directory(documents_dir: Path) -> list[Path]:
    """Validate the document directory and return its PDF files."""

    if not documents_dir.exists():
        raise DocumentLoadError(
            f"No existe la carpeta de documentos: {documents_dir}"
        )

    if not documents_dir.is_dir():
        raise DocumentLoadError(
            f"La ruta de documentos no es una carpeta: {documents_dir}"
        )

    missing_files = [
        filename
        for filename in EXPECTED_PDF_FILES
        if not (documents_dir / filename).is_file()
    ]

    if missing_files:
        formatted = ", ".join(missing_files)
        raise DocumentLoadError(
            f"Faltan documentos obligatorios en data/documents: {formatted}"
        )

    pdf_files = sorted(
        path for path in documents_dir.glob("*.pdf") if path.is_file()
    )

    if not pdf_files:
        raise DocumentLoadError(
            f"No se encontraron archivos PDF en: {documents_dir}"
        )

    return pdf_files


def load_pdf_documents(
    documents_dir: Path = DOCUMENTS_DIR,
) -> tuple[list[Document], DocumentLoadSummary]:
    """Load every PDF page as an independent LangChain document."""

    pdf_files = _validate_documents_directory(documents_dir)

    documents: list[Document] = []
    total_pages = 0
    skipped_empty_pages = 0
    empty_pdf_files: list[str] = []

    for pdf_path in pdf_files:
        try:
            reader = PdfReader(str(pdf_path))
        except (PdfReadError, OSError, ValueError) as exc:
            raise DocumentLoadError(
                f"No se pudo abrir el PDF '{pdf_path.name}': {exc}"
            ) from exc

        if reader.is_encrypted:
            try:
                decryption_result = reader.decrypt("")
            except Exception as exc:
                raise DocumentLoadError(
                    f"El PDF '{pdf_path.name}' está cifrado "
                    "y no pudo abrirse."
                ) from exc

            if not decryption_result:
                raise DocumentLoadError(
                    f"El PDF '{pdf_path.name}' requiere contraseña."
                )

        total_pages += len(reader.pages)
        loaded_pages_for_file = 0

        for page_index, page in enumerate(reader.pages):
            try:
                extracted_text = page.extract_text() or ""
            except Exception as exc:
                raise DocumentLoadError(
                    f"Falló la extracción de '{pdf_path.name}', "
                    f"página interna {page_index}: {exc}"
                ) from exc

            normalized_text = _normalize_text(extracted_text)

            if not normalized_text:
                skipped_empty_pages += 1
                continue

            documents.append(
                Document(
                    page_content=normalized_text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_index,
                    },
                )
            )

            loaded_pages_for_file += 1

        if loaded_pages_for_file == 0:
            empty_pdf_files.append(pdf_path.name)

    if empty_pdf_files:
        formatted = ", ".join(empty_pdf_files)
        raise DocumentLoadError(
            "Estos PDF no contienen texto extraíble: "
            f"{formatted}"
        )

    if not documents:
        raise DocumentLoadError(
            "La extracción finalizó sin obtener texto de ningún PDF."
        )

    summary = DocumentLoadSummary(
        pdf_count=len(pdf_files),
        total_pages=total_pages,
        loaded_pages=len(documents),
        skipped_empty_pages=skipped_empty_pages,
    )

    return documents, summary


def split_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Split page documents while preserving their original metadata."""

    if not documents:
        raise DocumentLoadError(
            "No se recibieron documentos para fragmentar."
        )

    if chunk_size <= 0:
        raise DocumentLoadError(
            "CHUNK_SIZE debe ser mayor que cero."
        )

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise DocumentLoadError(
            "CHUNK_OVERLAP debe ser mayor o igual a cero "
            "y menor que CHUNK_SIZE."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_documents(documents)
    chunks: list[Document] = []

    for chunk_index, chunk in enumerate(raw_chunks):
        content = chunk.page_content.strip()

        if not content:
            raise DocumentLoadError(
                f"Se generó un fragmento vacío en la posición {chunk_index}."
            )

        metadata = dict(chunk.metadata)
        metadata["chunk_id"] = f"chunk-{chunk_index:04d}"

        chunks.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    if not chunks:
        raise DocumentLoadError(
            "La fragmentación no generó ningún chunk."
        )

    return chunks