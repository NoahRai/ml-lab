from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded only from the service environment."""

    app_name: str = "ML Lab ML Service"
    environment: str = "development"
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ML_", extra="ignore")


settings = Settings()
