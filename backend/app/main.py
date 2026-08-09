# Main FastAPI application

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.routers import scans,finding, fim, port_scanner, osint, log_analyzer, dashboard, clerk_webhook
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Argus Security Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://argus-security-platform.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(scans.router)
app.include_router(finding.router)
app.include_router(fim.router)
app.include_router(port_scanner.router)
app.include_router(osint.router)
app.include_router(log_analyzer.router)
app.include_router(dashboard.router)
app.include_router(clerk_webhook.router)


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