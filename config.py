"""Application configuration."""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Application settings for our program. Will automatically fetch from our `.env` file or `os.environ`
    """
    # Program config
    check_interval_minutes: int = 15  # should match the interval of how often the cloud function that invokes this program runs

    # LLM config
    anthropic_api_key: str
    llm_models: List[str] = ["claude-haiku-4-5", "claude-sonnet-4-5"]

    # TODO: Add SMS twilio config

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8"
    )
