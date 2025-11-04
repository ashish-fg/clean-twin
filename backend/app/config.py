from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
