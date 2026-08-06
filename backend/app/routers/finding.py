# API endpoints for security findings.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.finding import Finding
from app.schemas.finding import (
    FindingCreate,
    FindingResponse
)


router = APIRouter(
    prefix="/findings",
    tags=["Findings"]
)


@router.post("/", response_model=FindingResponse)
def create_finding(
    finding: FindingCreate,
    db: Session = Depends(get_db)
):

    new_finding = Finding(
        scan_id=finding.scan_id,
        severity=finding.severity,
        title=finding.title,
        description=finding.description,
        data=finding.data
    )


    db.add(new_finding)
    db.commit()
    db.refresh(new_finding)

    return new_finding

@router.get("/", response_model=list[FindingResponse])
def get_findings(
    db: Session = Depends(get_db)
):

    findings = db.query(Finding).all()

    return findings