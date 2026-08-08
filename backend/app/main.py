# Main FastAPI application

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.routers import scans,finding, fim, port_scanner, osint

app = FastAPI(
    title="Argus Security Platform",
    version="1.0.0"
)

app.include_router(scans.router)
app.include_router(finding.router)
app.include_router(fim.router)
app.include_router(port_scanner.router)
app.include_router(osint.router)


@app.get("/")
def root():
    return {
        "message": "Argus API is running"
    }


@app.get("/database-test")
def database_test(
    db: Session = Depends(get_db)
):
    # If this endpoint works,
    # FastAPI successfully connected to PostgreSQL.

    return {
        "message": "Database connection successful"
    }