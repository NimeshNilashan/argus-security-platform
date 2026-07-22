from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Asset, ScanJob, Finding
from app.modules.subdomain_scanner import SubdomainScannerModule

router = APIRouter()


@router.post("/subdomain/{asset_id}")
def trigger_subdomain_scan(
        asset_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    scanner = SubdomainScannerModule(db)
    background_tasks.add_task(scanner.run_scan, asset_id)

    return {
        "message": f"Subdomain scan initiated for asset {asset_id}",
        "status": "processing"
    }


@router.get("/subdomain/{asset_id}/results")
def get_subdomain_results(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    latest_job = (
        db.query(ScanJob)
        .filter(ScanJob.asset_id == asset_id, ScanJob.module_name == "subdomain_scan")
        .order_by(desc(ScanJob.timestamp))
        .first()
    )

    active_findings = (
        db.query(Finding)
        .join(ScanJob, Finding.scan_job_id == ScanJob.id)  # 1. Link the two tables together
        .filter(
            Finding.asset_id == asset_id,
            Finding.resolved == False,
            ScanJob.module_name == "subdomain_scan"  # 2. Filter by the module!
        )
        .all()
    )

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
                "details": f.details
            } for f in active_findings
        ]
    }