from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Base directory (repo root)
    BASE_DIR: Path = Path(__file__).resolve().parents[1]

    # Default data directory; can be overridden by env var in Docker
    DATA_DIR: Path = BASE_DIR / "data"

    # Name of the jokes file (detect csv/tsv)
    JOKES_CSV_FILENAME: str = "jokes.csv"
    JOKES_TSV_FILENAME: str = "jokes.tsv"

    # Control whether the jokes file is linked/visible from the UI
    DOWNLOADABLE_JOKES: bool = False

    # Server port (used when running via Python or in Docker)
    PORT: int = 6262

    # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
