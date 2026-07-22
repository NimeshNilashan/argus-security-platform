from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Asset, ScanJob, Finding
from app.modules.file_integrity import FileIntegrityModule

router = APIRouter()


@router.post("/integrity/{asset_id}")
def trigger_integrity_check(
        asset_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    checker = FileIntegrityModule(db)
    background_tasks.add_task(checker.run_check, asset_id)

    return {
        "message": f"File integrity check initiated for asset {asset_id}",
        "status": "processing"
    }


@router.get("/integrity/{asset_id}/results")
def get_integrity_results(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    latest_job = (
        db.query(ScanJob)
        .filter(ScanJob.asset_id == asset_id, ScanJob.module_name == "file_integrity")
        .order_by(desc(ScanJob.timestamp))
        .first()
    )

    active_findings = (
        db.query(Finding)
        .join(ScanJob, Finding.scan_job_id == ScanJob.id)
        .filter(
            Finding.asset_id == asset_id,
            Finding.resolved == False,
            ScanJob.module_name == "file_integrity"
        )
        .all()
    )

    return {
        "asset_id": asset_id,
        "target_filepath": asset.target,
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
                "details": f.details
            } for f in active_findings
        ]
    }