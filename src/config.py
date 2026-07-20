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


def validate_embedding_config() -> tuple[str, str]:
    """Validate and return the embedding API key and model."""

    return get_google_api_key(), get_embedding_model()