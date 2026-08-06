# Database connection and session management.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings


# Creates the connection between Python and PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    echo=False
)


# Creates a new database session when requested.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# FastAPI dependency.
# Opens a database session for a request,
# then closes it automatically.
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()