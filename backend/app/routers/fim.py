from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import tempfile
import os
import uuid


from app.config.database import get_db
from app.models.fim_baseline import FIMBaseline
from app.modules.file_integrity.checker import calculate_hash
from app.models.finding import Finding
from app.models.fim_baseline import FIMBaseline
from app.services.scan_service import create_scan

router = APIRouter(
    prefix="/fim",
    tags=["File Integrity"]
)


@router.post("/save")
async def save_baseline(
    user_id: str = Form(...),
    custom_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Temporarily save uploaded file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name


    try:
        # Calculate SHA-256 hash
        file_hash = calculate_hash(temp_path)


        baseline = FIMBaseline(
            user_id=user_id,
            custom_name=custom_name,
            filename=file.filename,
            hash=file_hash
        )


        db.add(baseline)
        db.commit()
        db.refresh(baseline)


        return {
            "message": "File baseline saved",
            "id": baseline.id,
            "filename": baseline.filename,
            "hash": baseline.hash
        }


    finally:
        # Remove temporary file
        os.remove(temp_path)


@router.post("/verify")
async def verify_file(
    user_id: str = Form(...),
    baseline_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    baseline = (
        db.query(FIMBaseline)
        .filter(FIMBaseline.id == baseline_id)
        .first()
    )

    if not baseline:
        return {
            "error": "Baseline not found"
        }


    # Create scan record for this FIM operation
    scan = create_scan(
        db=db,
        user_id=uuid.UUID(user_id),
        module="file_integrity",
        target=baseline.filename
    )


    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp:

        temp.write(await file.read())
        temp_path = temp.name


    try:

        current_hash = calculate_hash(temp_path)


        if current_hash == baseline.hash:

            scan.status = "completed"
            db.commit()

            return {
                "status": "verified",
                "message": "File integrity is intact",
                "scan_id": scan.id
            }


        finding = Finding(
            scan_id=scan.id,
            severity="high",
            title="File Integrity Violation",
            description=f"{baseline.filename} has been modified",
            data={
                "old_hash": baseline.hash,
                "new_hash": current_hash,
                "filename": baseline.filename
            }
        )


        scan.status = "completed"

        db.add(finding)
        db.commit()


        return {
            "status": "modified",
            "message": "File has been changed",
            "scan_id": scan.id,
            "finding_created": True
        }


    finally:

        os.remove(temp_path)