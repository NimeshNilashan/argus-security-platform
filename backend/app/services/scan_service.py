# Shared scan creation logic used by all security modules.

from sqlalchemy.orm import Session

from app.models.scan import Scan


def create_scan(
    db: Session,
    user_id,
    module: str,
    target: str
):

    scan = Scan(
        user_id=user_id,
        module=module,
        target=target,
        status="running"
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    return scan