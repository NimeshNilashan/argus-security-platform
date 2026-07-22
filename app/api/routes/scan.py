from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db  # Assuming you have a get_db dependency
from sqlalchemy import desc
from app.modules.port_scanner import PortScannerModule
from app.models import Asset, ScanJob, Finding

router = APIRouter()


@router.post("/scan/{asset_id}")
def trigger_scan(
        asset_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    # 1. Initialize the module with our DB session
    scanner = PortScannerModule(db)

    # 2. Add the task to the background
    # This prevents the API from hanging while waiting for network I/O
    background_tasks.add_task(scanner.run_scan, asset_id)

    return {
        "message": f"Scan initiated for asset {asset_id}",
        "status": "processing"
    }

@router.get("/scan/{asset_id}/results")
def get_scan_results(asset_id: int, db: Session = Depends(get_db)):
    # 1. Verify the asset actually exists in the system
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 2. Fetch the absolute latest scan job (whether SUCCESS or FAILED)
    latest_job = (
        db.query(ScanJob)
        .filter(ScanJob.asset_id == asset_id, ScanJob.module_name == "port_scan")
        .order_by(desc(ScanJob.timestamp))
        .first()
    )

    # 3. YOUR TURN: Fetch all UNRESOLVED findings for this asset
    # Hint: You need to filter where the Finding's asset_id matches the requested asset_id,
    # AND where Finding.resolved is equal to False.
    # End your query chain with .all() to pull every matching record into a Python list.
    active_findings = (
        db.query(Finding)
        .join(ScanJob.asset_id == asset_id, ScanJob.module_name == "port_scan")
        .filter(Finding.asset_id == asset_id, Finding.resolved == False)
        .all()
    )

    # 4. Package everything into a clean JSON response for the frontend
    return {
        "asset_id": asset_id,
        "target": asset.target,
        "latest_scan": {
            "id": latest_job.id if latest_job else None,
            "status": latest_job.status if latest_job else "NEVER_SCANNED",
            "timestamp": latest_job.timestamp if latest_job else None,
            "raw_results": latest_job.raw_output if latest_job else None
        },
        "active_findings": [
            {
                "id": f.id,
                "severity": f.severity,
                "title": f.title,
                "details": f.details,
                "timestamp": f.timestamp
            } for f in active_findings
        ]
    }