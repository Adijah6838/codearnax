from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "CODEARENA X"
    ENV: str = "development"

    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_PATH: Path = Path(__file__).resolve().parent.parent / "codearnax.db"

    EXECUTION_ROOT: Path = Path(__file__).resolve().parent.parent.parent / "execution"
    EXECUTION_TIMEOUT_SECONDS: int = 5
    EXECUTION_MEMORY_MB: int = 256


settings = Settings()