from fastapi import FastAPI, Depends
from pip._internal.network import session
from sqlalchemy import text,select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Asset
from app.api.routes import scan
from app.api.routes import subdomain
from app.api.routes import assets
from app.api.routes import scan, subdomain, assets, integrity

app = FastAPI(title="ARGUS - Unified Security Monitoring Platform")
# 2. Register the scanner router with an optional prefix to keep things organized
app.include_router(scan.router, prefix="/api/v1")
app.include_router(subdomain.router, prefix="/api/v1")
app.include_router(assets.router, prefix="/api/v1")
app.include_router(integrity.router, prefix="/api/v1")

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

@app.get("/test")
def db_test(db:Session = Depends(get_db)):
    stmt = select(Asset).where(Asset.id == 1)

    asset = db.execute(stmt).scalar_one_or_none()

    if asset:
        return {
            "id" : asset.id,
            "target" : asset.target,
            "asset_type" : asset.asset_type
        }

    return {"status" : "Asset not found"}