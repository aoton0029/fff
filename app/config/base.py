import os
from dotenv import load_dotenv

class Config:
    """Base configuration for the application."""
    DEBUG: bool = False
    TESTING: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

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