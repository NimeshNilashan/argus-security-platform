import uuid

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.finding import Finding
from app.services.scan_service import create_scan
from app.modules.port_scanner.scanner import scan


router = APIRouter(
    prefix="/port-scanner",
    tags=["Port Scanner"]
)


@router.post("/scan")
def run_port_scan(
    user_id: str = Form(...),
    target: str = Form(...),
    max_port: int = Form(...),
    db: Session = Depends(get_db)
):

    scan_record = create_scan(
        db=db,
        user_id=uuid.UUID(user_id),
        module="port_scanner",
        target=target
    )

    results = scan(target, max_port)

    for result in results:

        finding = Finding(
            scan_id=scan_record.id,
            severity="medium",
            title=f"Open Port {result['port']}",
            description=(
                f"Port {result['port']} is open on {target}. "
                f"Detected service: {result['service']}."
            ),
            data=result
        )

        db.add(finding)

    scan_record.status = "completed"

    db.commit()

    return {
        "scan_id": scan_record.id,
        "target": target,
        "ports_scanned": max_port,
        "open_ports": results,
        "open_port_count": len(results)
    }