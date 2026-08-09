# Dashboard API endpoints.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.services.dashboard_service import get_dashboard_summary


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    clerk_user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    # Find the Argus user linked to the Clerk account.
    user = (
        db.query(User)
        .filter(User.clerk_user_id == clerk_user_id)
        .first()
    )

    if not user:
        return {
            "error": "User not found"
        }

    return get_dashboard_summary(
        db=db,
        user_id=user.id
    )