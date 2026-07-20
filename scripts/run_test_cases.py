"""Run the documented CSV test cases against the RAG pipeline."""

from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import ConfigurationError  # noqa: E402
from src.rag_chain import (  # noqa: E402
    RAGError,
    RAGResult,
    answer_question,
    create_rag_runtime,
)


TEST_CASES_PATH = PROJECT_ROOT / "tests" / "casos_de_prueba.csv"
REQUEST_DELAY_SECONDS = 4.2

REQUIRED_COLUMNS = {
    "id",
    "tipo",
    "pregunta",
    "documento_esperado",
    "seccion_esperada",
    "pagina_esperada",
    "comportamiento_esperado",
}


def _load_test_cases() -> list[dict[str, str]]:
    """Load and validate the real CSV structure."""

    if not TEST_CASES_PATH.is_file():
        raise RAGError(
            f"No existe el archivo de casos de prueba: {TEST_CASES_PATH}"
        )

    with TEST_CASES_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise RAGError("El CSV no contiene encabezados.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise RAGError(
                "Faltan columnas obligatorias en el CSV: "
                + ", ".join(sorted(missing_columns))
            )

        return [dict(row) for row in reader]


def _structural_status(
    case_type: str,
    result: RAGResult,
) -> str:
    """Perform only the structural checks allowed in this block."""

    if case_type == "fallback":
        return "OK" if result.is_fallback else "REVISAR"

    if case_type in {"respondible", "ambiguo"}:
        if not result.is_fallback and result.sources:
            return "OK"

        return "REVISAR"

    return "TIPO DESCONOCIDO"


def _category_name(case_type: str) -> str:
    """Map the CSV category name to the requested report name."""

    if case_type == "ambiguo":
        return "fronterizo"

    return case_type


def main() -> int:
    """Execute every CSV case and print a reviewable report."""

    try:
        cases = _load_test_cases()
        runtime = create_rag_runtime()

        totals: Counter[str] = Counter()
        structural_results: Counter[str] = Counter()
        errors = 0

        print(f"Casos cargados: {len(cases)}")

        for position, case in enumerate(cases, start=1):
            case_id = case["id"].strip()
            case_type = case["tipo"].strip().lower()
            question = case["pregunta"].strip()
            expected = case["comportamiento_esperado"].strip()

            category = _category_name(case_type)
            totals[category] += 1

            print("\n" + "=" * 88)
            print(
                f"CASO {position}/{len(cases)} — "
                f"{case_id} — {category}"
            )
            print("=" * 88)
            print(f"Pregunta: {question}")
            print(f"Esperado: {expected}")

            try:
                result = answer_question(question, runtime)
            except RAGError as exc:
                errors += 1
                structural_results["ERROR"] += 1
                print(f"ERROR: {exc}")
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            status = _structural_status(case_type, result)
            structural_results[status] += 1

            print(f"Fallback: {'sí' if result.is_fallback else 'no'}")
            print(f"Control estructural: {status}")
            print("Respuesta:")
            print(result.answer)

            if result.sources:
                print("Fuentes:")

                for source in result.sources:
                    print(
                        f"- {source.source} — página {source.page}"
                    )
            else:
                print("Fuentes: ninguna")

            time.sleep(REQUEST_DELAY_SECONDS)

        print("\n" + "=" * 88)
        print("RESUMEN FINAL DEL CSV")
        print("=" * 88)

        print(f"Total de casos: {len(cases)}")
        print(f"Respondibles: {totals['respondible']}")
        print(f"Fallback: {totals['fallback']}")
        print(f"Fronterizos: {totals['fronterizo']}")
        print(f"Controles estructurales OK: {structural_results['OK']}")
        print(
            "Controles estructurales para revisar: "
            f"{structural_results['REVISAR']}"
        )
        print(f"Errores de ejecución: {errors}")

        print(
            "\nLos casos respondibles y fronterizos requieren "
            "revisión manual del contenido. No se utilizó otro LLM "
            "como juez."
        )

        return 1 if errors else 0

    except (ConfigurationError, RAGError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
