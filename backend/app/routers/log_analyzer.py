import os
import tempfile
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.finding import Finding
from app.services.scan_service import create_scan
from app.modules.log_analyzer.analyzer import analyze_log


router = APIRouter(
    prefix="/log-analyzer",
    tags=["Log Analyzer"]
)


@router.post("/analyze")
async def analyze_uploaded_log(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    scan_record = create_scan(
        db=db,
        user_id=uuid.UUID(user_id),
        module="log_analyzer",
        target=file.filename
    )

    # Save the uploaded log temporarily.
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".log"
    ) as temp:

        temp.write(await file.read())
        temp_path = temp.name

    try:

        results = analyze_log(temp_path)

        findings_created = 0

        for attack_type, ip_addresses in results["findings"].items():

            if not ip_addresses:
                continue

            # Remove duplicate IPs for cleaner findings.
            unique_ips = list(set(ip_addresses))

            finding = Finding(
                scan_id=scan_record.id,
                severity="high",
                title=f"{attack_type} Detected",
                description=(
                    f"{len(ip_addresses)} {attack_type} "
                    f"attempt(s) detected in the uploaded log."
                ),
                data={
                    "attack_type": attack_type,
                    "ip_addresses": unique_ips,
                    "attempt_count": len(ip_addresses)
                }
            )

            db.add(finding)
            findings_created += 1

        scan_record.status = "completed"

        db.commit()

        return {
            "scan_id": scan_record.id,
            "filename": file.filename,
            "total_lines": results["total_lines"],
            "attacks_detected": results["attacks_detected"],
            "findings_created": findings_created,
            "findings": results["findings"]
        }

    finally:

        os.remove(temp_path)