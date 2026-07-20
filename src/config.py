"""Configuration for the DEL PINO Knowledge Agent."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE)

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
FAISS_INDEX_DIR = PROJECT_ROOT / "storage" / "faiss_index"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
RETRIEVAL_K = 4
CHAT_TEMPERATURE = 0.0

EXPECTED_PDF_FILES = (
    "01_guia_comercial_y_preguntas_frecuentes.pdf",
    "02_guia_de_envios_y_entregas.pdf",
    "03_pedidos_personalizados_cambios_y_garantias.pdf",
)


class ConfigurationError(RuntimeError):
    """Raised when required application configuration is missing."""


def get_google_api_key() -> str:
    """Return the configured Google API key without displaying it."""

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not api_key:
        raise ConfigurationError(
            "Falta GOOGLE_API_KEY. Agregala al archivo .env local."
        )

    return api_key


def get_embedding_model() -> str:
    """Return the configured Gemini embedding model."""

    model = os.getenv("GEMINI_EMBEDDING_MODEL", "").strip()

    if not model:
        raise ConfigurationError(
            "Falta GEMINI_EMBEDDING_MODEL. "
            "Agregalo al archivo .env local."
        )

    return model


def get_chat_model() -> str:
    """Return the configured Gemini chat model."""

    model = os.getenv("GEMINI_CHAT_MODEL", "").strip()

    if not model:
        raise ConfigurationError(
            "Falta GEMINI_CHAT_MODEL. "
            "Agregalo al archivo .env local."
        )

    return model


def get_relevance_threshold() -> float | None:
    """Return the optional minimum cosine-similarity threshold."""

    raw_value = os.getenv("RAG_RELEVANCE_THRESHOLD", "").strip()

    if not raw_value:
        return None

    try:
        threshold = float(raw_value)
    except ValueError as exc:
        raise ConfigurationError(
            "RAG_RELEVANCE_THRESHOLD debe ser un número "
            "entre -1 y 1, o quedar vacío."
        ) from exc

    if not -1.0 <= threshold <= 1.0:
        raise ConfigurationError(
            "RAG_RELEVANCE_THRESHOLD debe estar entre -1 y 1."
        )

    return threshold


def validate_embedding_config() -> tuple[str, str]:
    """Validate and return embedding configuration."""

    return get_google_api_key(), get_embedding_model()


def validate_rag_config() -> tuple[str, str, str, float | None]:
    """Validate and return all configuration required by the RAG pipeline."""

    return (
        get_google_api_key(),
        get_embedding_model(),
        get_chat_model(),
        get_relevance_threshold(),
    )
