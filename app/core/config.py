import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "RAG Service"
    ENV: str = os.getenv("ENV", "development")
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite") # sqlite or postgresql

    # Postgres details (only if DB_TYPE is postgresql)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "rag_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

    @property
    def DATABASE_URL(self):
        """Construct the database URL based on the DB_TYPE."""
        if self.DB_TYPE == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # Default to SQLite local file
        return "sqlite:///./rag_service.db"
    
# Instantiate settings (singleton)
settings = Settings()