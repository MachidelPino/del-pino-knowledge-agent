"""Streamlit interface for the DEL PINO Knowledge Agent."""

from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from src.config import ConfigurationError
from src.rag_chain import (
    RAGError,
    RAGResult,
    RAGRuntime,
    RAGSource,
    answer_question,
    create_rag_runtime,
)


APP_TITLE = "DEL PINO Knowledge Agent"

APP_DESCRIPTION = (
    "Agente interno de conocimiento para consultar políticas comerciales "
    "y operativas de DEL PINO home & deco."
)

DOCUMENTATION_NOTICE = (
    "Las respuestas se generan exclusivamente a partir de la "
    "documentación disponible."
)

GENERIC_QUERY_ERROR = (
    "No fue posible procesar la consulta. "
    "Revisá la configuración e intentá nuevamente."
)

LOGGER = logging.getLogger(__name__)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(
    scope="session",
    show_spinner=False,
)
def get_rag_runtime() -> RAGRuntime:
    """Load and cache the RAG runtime for the current session."""

    return create_rag_runtime()


def _deduplicate_sources(
    sources: tuple[RAGSource, ...],
) -> list[tuple[str, int]]:
    """Return safe, unique source-page pairs in their original order."""

    unique_sources: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()

    for source in sources:
        filename = Path(source.source).name
        key = (filename, source.page)

        if key in seen:
            continue

        seen.add(key)
        unique_sources.append(key)

    return unique_sources


def _render_sources(sources: tuple[RAGSource, ...]) -> None:
    """Render human-readable sources without internal metadata."""

    unique_sources = _deduplicate_sources(sources)

    if not unique_sources:
        return

    st.markdown("#### Fuentes consultadas")

    for filename, page in unique_sources:
        st.markdown(f"- `{filename}` — página {page}")


def _render_result(result: RAGResult) -> None:
    """Render a RAG response and its sources."""

    st.divider()
    st.subheader("Respuesta")

    if result.is_fallback:
        st.warning(result.answer)
        return

    st.markdown(result.answer)
    _render_sources(result.sources)


def _render_examples() -> None:
    """Show a compact list of example questions."""

    with st.expander("Preguntas de ejemplo"):
        st.markdown(
            """
- ¿Qué medios de pago acepta DEL PINO?
- ¿Cómo se determina el costo del envío?
- ¿Qué medidas necesito para una cortina a medida?
- ¿Qué hay que hacer si un producto llega dañado?
            """
        )


def _load_runtime_or_stop() -> RAGRuntime:
    """Initialize the application runtime or stop with a safe message."""

    try:
        with st.spinner("Cargando la documentación..."):
            return get_rag_runtime()

    except ConfigurationError:
        LOGGER.exception(
            "La aplicación no pudo iniciarse por una configuración faltante."
        )
        st.error(
            "La aplicación no está configurada correctamente. "
            "Revisá las variables de entorno requeridas."
        )
        st.stop()

    except RAGError:
        LOGGER.exception(
            "La aplicación no pudo cargar el pipeline RAG."
        )
        st.error(
            "No fue posible iniciar el agente. "
            "Revisá la configuración y el índice documental."
        )
        st.stop()

    except Exception:
        LOGGER.exception(
            "Ocurrió un error inesperado al iniciar la aplicación."
        )
        st.error(
            "Ocurrió un error inesperado al iniciar la aplicación."
        )
        st.stop()


def _process_question(
    question: str,
    runtime: RAGRuntime,
) -> RAGResult | None:
    """Process one submitted question with safe UI error handling."""

    normalized_question = question.strip()

    if not normalized_question:
        st.warning("Escribí una pregunta antes de consultar.")
        return None

    try:
        with st.spinner("Consultando la documentación..."):
            return answer_question(
                question=normalized_question,
                runtime=runtime,
            )

    except ConfigurationError:
        LOGGER.exception(
            "La consulta falló por una configuración faltante."
        )
        st.error(GENERIC_QUERY_ERROR)

    except RAGError:
        LOGGER.exception(
            "El pipeline RAG no pudo procesar la consulta."
        )
        st.error(
            "No fue posible procesar la consulta. "
            "Revisá la conexión o la disponibilidad de Gemini "
            "e intentá nuevamente."
        )

    except Exception:
        LOGGER.exception(
            "Ocurrió un error inesperado durante la consulta."
        )
        st.error(GENERIC_QUERY_ERROR)

    return None


def main() -> None:
    """Render and run the Streamlit application."""

    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)
    st.caption(DOCUMENTATION_NOTICE)

    _render_examples()

    runtime = _load_runtime_or_stop()

    with st.form(
        key="question_form",
        clear_on_submit=False,
        enter_to_submit=True,
    ):
        question = st.text_input(
            label="Escribí tu pregunta",
            placeholder=(
                "¿Qué medidas necesito para pedir "
                "una cortina a medida?"
            ),
            max_chars=1000,
        )

        submitted = st.form_submit_button(
            label="Consultar",
            type="primary",
        )

    if submitted:
        result = _process_question(
            question=question,
            runtime=runtime,
        )

        if result is not None:
            _render_result(result)

    st.divider()
    st.caption(
        "Este prototipo no consulta stock, estados de pedidos "
        "ni información comercial en tiempo real."
    )


if __name__ == "__main__":
    main()