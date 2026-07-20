"""Run manual semantic retrieval tests against the saved FAISS index."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import (  # noqa: E402
    RETRIEVAL_K,
    ConfigurationError,
    validate_embedding_config,
)
from src.vector_store import (  # noqa: E402
    VectorStoreError,
    create_embedding_model,
    load_vector_index,
    semantic_search,
)


TEST_QUERIES = (
    "¿Qué medios de pago acepta DEL PINO?",
    "¿Cómo se determina el costo del envío?",
    "¿Qué medidas necesito para pedir una cortina a medida?",
    "¿Qué hay que hacer si un producto llega dañado?",
    "¿Se puede confirmar una fecha exacta de entrega?",
)


def _abbreviate(text: str, limit: int = 280) -> str:
    """Return a compact fragment preview."""

    compact = " ".join(text.split())

    if len(compact) <= limit:
        return compact

    return compact[: limit - 1].rstrip() + "…"


def main() -> int:
    """Load the saved index and execute the manual queries."""

    try:
        validate_embedding_config()

        print("Cargando índice FAISS existente...")

        index, documents, manifest = load_vector_index()
        embeddings = create_embedding_model()

        print(
            f"Índice cargado: {index.ntotal} vectores, "
            f"modelo={manifest.get('embedding_model')}."
        )

        for query_number, query in enumerate(TEST_QUERIES, start=1):
            print("\n" + "=" * 80)
            print(f"CONSULTA {query_number}: {query}")
            print("=" * 80)

            results = semantic_search(
                query=query,
                index=index,
                documents=documents,
                embeddings=embeddings,
                k=RETRIEVAL_K,
            )

            for position, result in enumerate(results, start=1):
                source = result.document.metadata.get(
                    "source",
                    "desconocido",
                )

                internal_page = result.document.metadata.get("page")

                if isinstance(internal_page, int):
                    human_page: int | str = internal_page + 1
                else:
                    human_page = "desconocida"

                print(f"\nPosición: {position}")
                print(f"Archivo: {source}")
                print(f"Página humana: {human_page}")
                print(
                    "Fragmento: "
                    f"{_abbreviate(result.document.page_content)}"
                )

        print("\nPruebas manuales finalizadas.")

        return 0

    except (ConfigurationError, VectorStoreError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.", file=sys.stderr)
        return 130

    except Exception as exc:
        print(
            f"\nERROR INESPERADO durante la recuperación: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())