"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = "change-me-in-production"

    DATABASE_URL: str = "sqlite:///./hospital_workforce.db"

    MODEL_DIR: str = "../ml/saved_models"
    DEFAULT_MODEL: str = "gru"
    FORECAST_HORIZON: int = 24
    LOOKBACK_WINDOW: int = 168

    ORTOOLS_MAX_SOLVE_TIME: int = 30
    W1_SHORTAGE: float = 10.0
    W2_IMBALANCE: float = 2.0
    W3_OVERTIME: float = 3.0
    W4_PREF_VIOLATIONS: float = 1.0

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
