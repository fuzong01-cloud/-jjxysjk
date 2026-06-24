from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "头雁学员信息管理系统"
    app_secret_key: str = "development-only-change-me"
    database_url: str = f"sqlite:///{(BASE_DIR / 'data' / 'touyan.db').as_posix()}"
    admin_username: str = "admin"
    admin_password: str = "ChangeMe123!"
    upload_dir: Path = BASE_DIR / "uploads"
    backup_dir: Path = BASE_DIR / "backups"
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

