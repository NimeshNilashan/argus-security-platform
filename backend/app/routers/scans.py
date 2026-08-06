# API endpoints related to scans.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanResponse


router = APIRouter(
    prefix="/scans",
    tags=["Scans"]
)


# Create a new scan record.
@router.post("/", response_model=ScanResponse)
def create_scan(
    scan: ScanCreate,
    db: Session = Depends(get_db)
):

    new_scan = Scan(
        user_id=scan.user_id,
        module=scan.module,
        target=scan.target,
        status="running"
    )

    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    return new_scan

@router.get("/", response_model=list[ScanResponse])
def get_scans(
    db: Session = Depends(get_db)
):
    scans = db.query(Scan).all()

    return scans