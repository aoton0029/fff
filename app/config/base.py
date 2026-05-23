import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration for the application."""
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(hours=8)
    SESSION_PROTECTION: str = "strong"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB per file

    @staticmethod
    def _build_db_uri() -> str:
        server = os.environ.get("DB_SERVER", "")
        database = os.environ.get("DB_DATABASE", "")
        username = os.environ.get("DB_USERNAME", "")
        password = os.environ.get("DB_PASSWORD", "")
        return (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}"
            "?driver=ODBC+Driver+18+for+SQL+Server"
        )