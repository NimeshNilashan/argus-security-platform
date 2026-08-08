import uuid

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.models.finding import Finding
from app.services.scan_service import create_scan
from app.modules.osint.recon import run_recon


router = APIRouter(
    prefix="/osint",
    tags=["OSINT"]
)


@router.post("/recon")
def run_osint_recon(
    user_id: str = Form(...),
    domain: str = Form(...),
    db: Session = Depends(get_db)
):

    scan_record = create_scan(
        db=db,
        user_id=uuid.UUID(user_id),
        module="osint",
        target=domain
    )

    results = run_recon(
        domain,
        settings.virustotal_api_key
    )

    reputation = results.get("reputation", {})
    stats = reputation.get("stats", {})

    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)

    if malicious > 0 or suspicious > 0:

        finding = Finding(
            scan_id=scan_record.id,
            severity="high" if malicious > 0 else "medium",
            title="Domain Reputation Warning",
            description=(
                f"VirusTotal reported {malicious} malicious "
                f"and {suspicious} suspicious detections "
                f"for {domain}."
            ),
            data={
                "domain": domain,
                "malicious": malicious,
                "suspicious": suspicious,
                "reputation": reputation
            }
        )

        db.add(finding)

    scan_record.status = "completed"

    db.commit()

    return {
        "scan_id": scan_record.id,
        "domain": domain,
        "results": results
    }