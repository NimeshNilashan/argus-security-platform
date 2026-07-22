from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Asset

router = APIRouter()


# Pydantic schema dictates what the JSON body must look like
class AssetCreate(BaseModel):
    target: str
    asset_type: str

@router.post("/assets")
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    new_asset = Asset(
        target=asset_in.target,
        asset_type=asset_in.asset_type
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return {
        "message": "Asset created",
        "asset_id": new_asset.id,
        "target": new_asset.target,
        "asset_type": new_asset.asset_type
    }