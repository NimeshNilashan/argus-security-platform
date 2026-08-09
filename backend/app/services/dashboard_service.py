# Collects dashboard data for one user.

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.models.fim_baseline import FIMBaseline
from app.models.scan import Scan


def get_dashboard_summary(
    db: Session,
    user_id
):
    # Total number of findings.
    findings_count = (
        db.query(func.count(Finding.id))
        .join(Scan)
        .filter(Scan.user_id == user_id)
        .scalar()
    )

    # Number of high-severity findings.
    high_risk_count = (
        db.query(func.count(Finding.id))
        .join(Scan)
        .filter(
            Scan.user_id == user_id,
            Finding.severity == "high"
        )
        .scalar()
    )

    # Total scans performed by this user.
    scans_count = (
        db.query(func.count(Scan.id))
        .filter(Scan.user_id == user_id)
        .scalar()
    )

    # Total saved file-integrity baselines.
    files_count = (
        db.query(func.count(FIMBaseline.id))
        .filter(FIMBaseline.user_id == user_id)
        .scalar()
    )

    # Latest findings.
    recent_findings = (
        db.query(Finding)
        .join(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(Finding.created_at.desc())
        .limit(5)
        .all()
    )

    # Latest scans.
    recent_scans = (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(Scan.started_at.desc())
        .limit(5)
        .all()
    )

    return {
        "stats": {
            "findings": findings_count or 0,
            "high_risk": high_risk_count or 0,
            "scans": scans_count or 0,
            "files": files_count or 0,
        },
        "recent_findings": [
            {
                "id": str(finding.id),
                "severity": finding.severity,
                "title": finding.title,
                "description": finding.description,
                "created_at": finding.created_at,
                "scan_id": str(finding.scan_id),
            }
            for finding in recent_findings
        ],
        "recent_activity": [
            {
                "id": str(scan.id),
                "module": scan.module,
                "target": scan.target,
                "status": scan.status,
                "started_at": scan.started_at,
                "completed_at": scan.completed_at,
            }
            for scan in recent_scans
        ],
    }