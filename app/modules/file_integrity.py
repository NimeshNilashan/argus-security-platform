# app/modules/file_integrity.py

import hashlib
import os
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Asset, ScanJob, Finding

class FileIntegrityModule:
    def __init__(self, db: Session):
        self.db = db

    def _compute_sha256(self, filepath: str) -> str | None:
        """Calculates SHA-256 hash using your original binary read method."""
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None

    def run_check(self, asset_id: int) -> dict:
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset ID {asset_id} not found")

        filepath = asset.target
        current_hash = self._compute_sha256(filepath)
        file_exists = os.path.exists(filepath)

        current_state = {
            "filepath": filepath,
            "exists": file_exists,
            "hash": current_hash
        }

        # Run differential analysis against previous database records
        self._process_scan_results(asset_id, current_state)

        return {"status": "completed", "result": current_state}

    def _process_scan_results(self, asset_id: int, current_state: dict):
        # Fetch last baseline job from PostgreSQL
        last_job = (
            self.db.query(ScanJob)
            .filter(
                ScanJob.asset_id == asset_id,
                ScanJob.module_name == "file_integrity",
                ScanJob.status == "SUCCESS"
            )
            .order_by(desc(ScanJob.timestamp))
            .first()
        )

        previous_state = last_job.raw_output if last_job else None

        # 1. Record the Scan Job
        new_job = ScanJob(
            asset_id=asset_id,
            module_name="file_integrity",
            status="SUCCESS",
            raw_output=current_state
        )
        self.db.add(new_job)
        self.db.flush()

        # 2. State Differential Logic
        if not current_state["exists"]:
            # Case A: File is missing or was deleted
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="CRITICAL",
                title=f"File Integrity Alert: File Missing ({current_state['filepath']})",
                details=current_state
            )
            self.db.add(finding)

        elif previous_state is None:
            # Case B: First scan ever (Baseline created)
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="INFO",
                title=f"File Integrity Baseline Set: {current_state['filepath']}",
                details={"initial_hash": current_state["hash"]}
            )
            self.db.add(finding)

        elif previous_state.get("hash") != current_state["hash"]:
            # Case C: Hash changed (File was modified!)
            finding = Finding(
                asset_id=asset_id,
                scan_job_id=new_job.id,
                severity="HIGH",
                title=f"File Integrity Violation: Modified File Detected!",
                details={
                    "filepath": current_state["filepath"],
                    "previous_hash": previous_state.get("hash"),
                    "current_hash": current_state["hash"]
                }
            )
            self.db.add(finding)

        # Case D: Hashes match -> Perfect integrity, 0 new alerts generated!

        self.db.commit()