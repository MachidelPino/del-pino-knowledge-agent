"""Calibrate retrieval relevance with every documented CSV test case."""

from __future__ import annotations

import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings


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


TEST_CASES_PATH = PROJECT_ROOT / "tests" / "casos_de_prueba.csv"
REQUEST_DELAY_SECONDS = 0.5

REQUIRED_COLUMNS = {
    "id",
    "tipo",
    "pregunta",
}


def load_test_cases() -> list[dict[str, str]]:
    """Load and validate the CSV test cases."""

    if not TEST_CASES_PATH.is_file():
        raise VectorStoreError(
            f"No existe el archivo de casos de prueba: {TEST_CASES_PATH}"
        )

    with TEST_CASES_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise VectorStoreError("El CSV no contiene encabezados.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise VectorStoreError(
                "Faltan columnas obligatorias en el CSV: "
                + ", ".join(sorted(missing_columns))
            )

        cases = [dict(row) for row in reader]

    if not cases:
        raise VectorStoreError("El CSV no contiene casos de prueba.")

    return cases


def human_page(page: object) -> int | str:
    """Convert an internal zero-based page into a human page number."""

    if isinstance(page, int):
        return page + 1

    return "desconocida"


def print_category_summary(
    category: str,
    scores: list[float],
) -> None:
    """Print the score range for one category."""

    if not scores:
        print(f"{category}: sin casos")
        return

    print(
        f"{category}: "
        f"casos={len(scores)} | "
        f"mínimo={min(scores):.4f} | "
        f"máximo={max(scores):.4f} | "
        f"promedio={sum(scores) / len(scores):.4f}"
    )


def main() -> int:
    """Run retrieval calibration over the complete CSV."""

    try:
        validate_embedding_config()

        cases = load_test_cases()
        index, documents, _manifest = load_vector_index()
        embeddings: GoogleGenerativeAIEmbeddings = create_embedding_model()

        scores_by_type: dict[str, list[float]] = defaultdict(list)

        print(f"Casos cargados: {len(cases)}")

        for position, case in enumerate(cases, start=1):
            case_id = case["id"].strip()
            case_type = case["tipo"].strip().lower()
            question = case["pregunta"].strip()

            results = semantic_search(
                query=question,
                index=index,
                documents=documents,
                embeddings=embeddings,
                k=RETRIEVAL_K,
            )

            print("\n" + "=" * 88)
            print(
                f"CASO {position}/{len(cases)} — "
                f"{case_id} — {case_type}"
            )
            print("=" * 88)
            print(f"Pregunta: {question}")

            if not results:
                print("Sin resultados.")
                scores_by_type[case_type].append(-1.0)
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            highest_score = results[0].score
            scores_by_type[case_type].append(highest_score)

            for result_position, result in enumerate(results, start=1):
                metadata = result.document.metadata
                source = metadata.get("source", "desconocido")
                page = human_page(metadata.get("page"))

                print(
                    f"{result_position}. "
                    f"score={result.score:.4f} | "
                    f"{source} | página {page}"
                )

            time.sleep(REQUEST_DELAY_SECONDS)

        respondible_scores = scores_by_type.get("respondible", [])
        fallback_scores = scores_by_type.get("fallback", [])
        ambiguous_scores = scores_by_type.get("ambiguo", [])

        print("\n" + "=" * 88)
        print("RESUMEN DE CALIBRACIÓN COMPLETA")
        print("=" * 88)

        print_category_summary("Respondibles", respondible_scores)
        print_category_summary("Fallback", fallback_scores)
        print_category_summary("Fronterizos/ambiguos", ambiguous_scores)

        if respondible_scores and fallback_scores:
            lowest_answerable = min(respondible_scores)

            if ambiguous_scores:
                lowest_answerable = min(
                    lowest_answerable,
                    min(ambiguous_scores),
                )

            highest_fallback = max(fallback_scores)

            print(
                "\nMenor score de casos que deben llegar a Gemini: "
                f"{lowest_answerable:.4f}"
            )
            print(
                "Mayor score de casos clasificados como fallback: "
                f"{highest_fallback:.4f}"
            )

            if highest_fallback < lowest_answerable:
                midpoint = (
                    highest_fallback + lowest_answerable
                ) / 2

                print(
                    "Existe separación numérica en el CSV completo."
                )
                print(
                    "Punto medio orientativo: "
                    f"{midpoint:.4f}"
                )
            else:
                print(
                    "Los grupos se superponen. No debe utilizarse "
                    "un umbral agresivo."
                )

        print(
            "\nMétrica: similitud coseno. "
            "Los valores más altos indican mayor similitud."
        )

        return 0

    except (ConfigurationError, VectorStoreError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nCalibración interrumpida.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
