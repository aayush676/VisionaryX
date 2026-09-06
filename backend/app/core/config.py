from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    port: int = 8000
    # Comma-separated list of allowed browser origins.
    frontend_origin: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins.

        `localhost` and `127.0.0.1` are *distinct* origins to a browser, so an
        app opened at one while only the other is allowlisted gets its
        preflight rejected. Accept both spellings of every configured origin so
        the app works whichever address the user actually opens.
        """
        origins: list[str] = []
        for origin in (o.strip() for o in self.frontend_origin.split(",")):
            if not origin:
                continue
            origins.append(origin)
            if "localhost" in origin:
                origins.append(origin.replace("localhost", "127.0.0.1"))
            elif "127.0.0.1" in origin:
                origins.append(origin.replace("127.0.0.1", "localhost"))
        return list(dict.fromkeys(origins))

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "visionaryx"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    email_backend: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@visionaryx.app"

    llm_provider: str = ""
    llm_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
