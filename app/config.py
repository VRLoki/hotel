"""
Hotel Intel — Configuration module.

Loads settings from environment variables / .env file and exposes
them as a typed Settings object.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from app directory
load_dotenv(Path(__file__).parent / ".env")


class Settings:
    """Central configuration loaded from environment."""

    # ── LLM ──────────────────────────────────
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # ── Hotel ────────────────────────────────
    HOTEL_NAME: str = os.getenv("HOTEL_NAME", "Eden Rock - St Barths")
    CURRENCY: str = os.getenv("HOTEL_CURRENCY", "€")

    # ── Data ─────────────────────────────────
    MOCK_DATA_DIR: Path = Path(os.getenv(
        "MOCK_DATA_DIR",
        str(Path(__file__).parent.parent / "mock-data"),
    ))

    # ── Delivery ─────────────────────────────
    DEFAULT_OUTPUT: str = os.getenv("DEFAULT_OUTPUT", "console")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")


settings = Settings()
