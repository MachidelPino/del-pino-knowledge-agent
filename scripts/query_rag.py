"""Ask one question to the DEL PINO RAG agent from PowerShell."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import ConfigurationError  # noqa: E402
from src.rag_chain import (  # noqa: E402
    RAGError,
    answer_question,
    create_rag_runtime,
)


def main() -> int:
    """Load the saved index and answer one user question."""

    try:
        print("Cargando DEL PINO Knowledge Agent...")
        runtime = create_rag_runtime()

        question = input("Pregunta: ").strip()

        if not question:
            raise RAGError("La pregunta no puede estar vacía.")

        result = answer_question(question, runtime)

        print("\nRespuesta:")
        print(result.answer)

        if result.sources:
            print("\nFuentes:")

            for source in result.sources:
                print(f"- {source.source} — página {source.page}")

        print(
            "\nDiagnóstico interno: "
            f"fallback={'sí' if result.is_fallback else 'no'}"
        )

        return 0

    except (ConfigurationError, RAGError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nConsulta interrumpida.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
