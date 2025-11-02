from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# If using SQLite, SQLAlchemy needs a special argument for threads
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Create the database engine
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Session factory for FastAPI dependencies
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """Dependency to get a database session in API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()