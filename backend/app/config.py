"""Application configuration constants."""

import os

# LLM model used across all agent execution and tool services
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
