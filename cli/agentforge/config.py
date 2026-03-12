"""Configuration loader for AgentForge CLI."""

import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


CONFIG_DIR = Path.home() / ".agentforge"
CONFIG_FILE = CONFIG_DIR / "config.toml"

_config: dict | None = None


def get_config() -> dict:
    """Load config from ~/.agentforge/config.toml or env vars."""
    global _config
    if _config is not None:
        return _config

    config = {
        "api_url": os.environ.get("AGENTFORGE_API_URL", "http://localhost:8000"),
        "api_key": os.environ.get("AGENTFORGE_API_KEY", ""),
    }

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            file_config = tomllib.load(f)
            config["api_url"] = file_config.get("api_url", config["api_url"])
            config["api_key"] = file_config.get("api_key", config["api_key"])

    _config = config
    return config


def get_api_url() -> str:
    return get_config()["api_url"]


def get_api_key() -> str:
    return get_config()["api_key"]


def ensure_config():
    """Create config directory and file if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            '# AgentForge CLI Configuration\n'
            'api_url = "http://localhost:8000"\n'
            'api_key = ""\n'
        )
