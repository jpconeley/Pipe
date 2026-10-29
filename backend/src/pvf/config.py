from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="PVF_", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+psycopg://pvf:pvf@localhost:5432/pvf"
    web_url: str = "http://localhost:3000"

    # Freight estimate assumptions for the matching engine's delivered-price
    # ranking. These are placeholder lane-rate assumptions, not quoted rates.
    freight_rate_per_mile: float = 2.25
    freight_min_per_load: float = 350.0
    truck_capacity_tons: float = 20.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
