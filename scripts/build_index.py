"""Build and persist the DEL PINO FAISS document index."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import (  # noqa: E402
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    FAISS_INDEX_DIR,
    ConfigurationError,
    get_embedding_model,
    validate_embedding_config,
)
from src.document_loader import (  # noqa: E402
    DocumentLoadError,
    load_pdf_documents,
    split_documents,
)
from src.vector_store import (  # noqa: E402
    VectorStoreError,
    build_vector_index,
    create_embedding_model,
    save_vector_index,
)


def _preview_text(text: str, limit: int = 160) -> str:
    """Return a compact one-line content preview."""

    compact = " ".join(text.split())

    if len(compact) <= limit:
        return compact

    return compact[: limit - 1].rstrip() + "…"


def main() -> int:
    """Run the complete indexing pipeline."""

    try:
        validate_embedding_config()
        embedding_model_name = get_embedding_model()

        print("Cargando documentos PDF...")
        page_documents, load_summary = load_pdf_documents()

        print(
            "Carga completada: "
            f"{load_summary.pdf_count} PDF, "
            f"{load_summary.total_pages} páginas totales, "
            f"{load_summary.loaded_pages} páginas con texto."
        )

        if load_summary.skipped_empty_pages:
            print(
                "Advertencia: "
                f"{load_summary.skipped_empty_pages} páginas vacías "
                "fueron omitidas."
            )

        print(
            "Fragmentando documentos con "
            f"chunk_size={CHUNK_SIZE} y "
            f"chunk_overlap={CHUNK_OVERLAP}..."
        )

        chunks = split_documents(page_documents)

        print(f"Fragmentación completada: {len(chunks)} chunks.")

        print("\nMuestras de metadata y contenido:")

        for sample_number, chunk in enumerate(chunks[:3], start=1):
            source = chunk.metadata.get("source", "desconocido")
            page = chunk.metadata.get("page", "desconocida")
            chunk_id = chunk.metadata.get("chunk_id", "sin-id")

            print(
                f"{sample_number}. "
                f"archivo={source} | "
                f"página_interna={page} | "
                f"chunk_id={chunk_id}"
            )
            print(f"   {_preview_text(chunk.page_content)}")

        print(
            f"\nGenerando embeddings con '{embedding_model_name}'..."
        )

        embeddings = create_embedding_model()
        index, vector_dimension = build_vector_index(
            chunks,
            embeddings,
        )

        print(
            "Embeddings generados: "
            f"{index.ntotal} vectores de dimensión {vector_dimension}."
        )

        print(f"Guardando índice en: {FAISS_INDEX_DIR}")

        save_vector_index(
            index=index,
            documents=chunks,
            vector_dimension=vector_dimension,
        )

        print("\n=== RESUMEN FINAL ===")
        print(f"PDF cargados: {load_summary.pdf_count}")
        print(f"Páginas totales: {load_summary.total_pages}")
        print(f"Páginas con texto: {load_summary.loaded_pages}")
        print(f"Chunks generados: {len(chunks)}")
        print(f"Directorio del índice: {FAISS_INDEX_DIR}")
        print("Índice FAISS generado correctamente.")

        return 0

    except (
        ConfigurationError,
        DocumentLoadError,
        VectorStoreError,
    ) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.", file=sys.stderr)
        return 130

    except Exception as exc:
        print(
            "\nERROR INESPERADO durante la construcción del índice: "
            f"{exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())