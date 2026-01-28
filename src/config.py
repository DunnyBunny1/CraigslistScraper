"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Application settings for our program. Will automatically fetch from our `.env` file or `os.environ`
    """

    # Search params to filter craigslist listings - they must be within a given `search_distance_miles` radiys of the
    # given coordinates (lat and lon), and meet the category of items defined by search_path
    search_lat: float = 37.789
    search_lon: float = -122.394
    search_distance_miles: int = 15
    search_path: str = "san-francisco-ca/bia"  # filters for bikes in the SF bay area

    # TODO: Look into remote config to allow for backfills on unsuccessful runs
    check_interval_minutes: int = 15  # should match the interval of how often the cloud function that invokes this program runs

    # LLM config
    anthropic_api_key: str
    # llm_models: List[str] = ["claude-haiku-4-5", "claude-sonnet-4-5"]

    # twilio config
    twilio_account_sid: str
    twilio_auth_token: str
    # service identifier for our twilio SMS messaging service
    twilio_messaging_service_sid: str
    twilio_to_number: str  # phone number we are sending the twilio message ot

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env", env_file_encoding="utf-8"
    )
