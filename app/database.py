# psycopg2 allows python applications to communicate with PostgreSQL databases
# however we do not directly import psycopg2 here as SQLAlchemy uses it internally

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# 1. Create the engine that interfaces with our Postgres container
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 2. Setup the Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. Define the database dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()