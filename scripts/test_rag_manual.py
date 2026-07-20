"""Run the minimum manual RAG behavior test suite."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
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


REQUEST_DELAY_SECONDS = 4.2


@dataclass(frozen=True)
class ManualTestCase:
    """A manually reviewed RAG behavior case."""

    case_id: str
    case_type: str
    question: str


TEST_CASES = (
    ManualTestCase(
        "R01",
        "respondible",
        "¿Qué medios de pago acepta DEL PINO?",
    ),
    ManualTestCase(
        "R02",
        "respondible",
        "¿Cómo se determina el costo del envío?",
    ),
    ManualTestCase(
        "R03",
        "respondible",
        "¿Qué medidas necesito para pedir una cortina a medida?",
    ),
    ManualTestCase(
        "R04",
        "respondible",
        "¿Qué hay que hacer si un producto llega dañado?",
    ),
    ManualTestCase(
        "R05",
        "respondible",
        "¿Se puede confirmar una fecha exacta de entrega?",
    ),
    ManualTestCase(
        "R06",
        "respondible",
        "¿Cómo se paga un pedido personalizado?",
    ),
    ManualTestCase(
        "F01",
        "fallback",
        "¿Cuánto cuesta hoy una cortina de tres metros?",
    ),
    ManualTestCase(
        "F02",
        "fallback",
        "¿Hay stock de cortinas beige?",
    ),
    ManualTestCase(
        "F03",
        "fallback",
        "¿Qué descuento me pueden hacer?",
    ),
    ManualTestCase(
        "F04",
        "fallback",
        "¿Cuál es el costo de envío a mi domicilio?",
    ),
    ManualTestCase(
        "F05",
        "fallback",
        "¿Dónde está exactamente el pedido 1234?",
    ),
    ManualTestCase(
        "F06",
        "fallback",
        "¿Quién fundó DEL PINO y en qué año?",
    ),
    ManualTestCase(
        "A01",
        "fronterizo",
        "¿Qué medidas necesito para una cortina a medida y cuánto cuesta?",
    ),
    ManualTestCase(
        "A02",
        "fronterizo",
        "¿Aceptan transferencia y qué descuento hacen pagando así?",
    ),
    ManualTestCase(
        "A03",
        "fronterizo",
        "¿Realizan envíos a todo el país y puede llegar este viernes?",
    ),
    ManualTestCase(
        "A04",
        "fronterizo",
        "¿Qué hago si llegó dañado y me pueden devolver el dinero hoy?",
    ),
)


def structural_status(
    case: ManualTestCase,
    result: RAGResult,
) -> str:
    """Check only the expected structural behavior."""

    if case.case_type == "fallback":
        if result.is_fallback and not result.sources:
            return "OK"

        return "REVISAR"

    if case.case_type in {"respondible", "fronterizo"}:
        if not result.is_fallback and result.sources:
            return "OK"

        return "REVISAR"

    return "TIPO DESCONOCIDO"


def main() -> int:
    """Execute all manual cases using a single loaded runtime."""

    try:
        print("Cargando DEL PINO Knowledge Agent...")
        runtime = create_rag_runtime()

        passed = 0
        review_required = 0
        errors = 0

        for position, case in enumerate(TEST_CASES, start=1):
            print("\n" + "=" * 88)
            print(
                f"CASO {position}/{len(TEST_CASES)} — "
                f"{case.case_id} — {case.case_type}"
            )
            print("=" * 88)
            print(f"Pregunta: {case.question}")

            try:
                result = answer_question(case.question, runtime)
            except RAGError as exc:
                errors += 1
                print(f"ERROR: {exc}")
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            status = structural_status(case, result)

            if status == "OK":
                passed += 1
            else:
                review_required += 1

            print(f"Fallback: {'sí' if result.is_fallback else 'no'}")
            print(f"Control estructural: {status}")

            print("\nRespuesta:")
            print(result.answer)

            if result.sources:
                print("\nFuentes:")

                for source in result.sources:
                    print(
                        f"- {source.source} — página {source.page}"
                    )
            else:
                print("\nFuentes: ninguna")

            time.sleep(REQUEST_DELAY_SECONDS)

        print("\n" + "=" * 88)
        print("RESUMEN DE PRUEBAS MANUALES")
        print("=" * 88)
        print(f"Total: {len(TEST_CASES)}")
        print(f"Controles estructurales OK: {passed}")
        print(f"Casos para revisar: {review_required}")
        print(f"Errores de ejecución: {errors}")

        print(
            "\nEl control estructural no evalúa la exactitud semántica. "
            "Las respuestas deben revisarse manualmente."
        )

        return 1 if errors else 0

    except (ConfigurationError, RAGError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nPruebas interrumpidas.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
