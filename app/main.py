from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

app = FastAPI(title="ARGUS - Unified Security Monitoring Platform")

@app.get("/health")
def health_check(db: Session = Depends(get_db)): # before running this session, create a database session
    # Simple query to verify database connection works over the wire
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}