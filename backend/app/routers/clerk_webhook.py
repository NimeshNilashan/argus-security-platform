# Receives and verifies Clerk webhook events.

import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError

from app.config.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    # Clerk signs the raw request body.
    payload = await request.body()

    signing_secret = os.getenv("CLERK_WEBHOOK_SIGNING_SECRET")

    if not signing_secret:
        raise HTTPException(
            status_code=500,
            detail="Clerk webhook signing secret is not configured"
        )

    try:
        webhook = Webhook(signing_secret)

        event = webhook.verify(
            payload,
            dict(request.headers)
        )

    except WebhookVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature"
        )

    event_type = event.get("type")
    data = event.get("data", {})

    # Create an Argus user when Clerk creates an account.
    if event_type == "user.created":

        clerk_user_id = data.get("id")

        email_addresses = data.get("email_addresses", [])

        if not clerk_user_id or not email_addresses:
            raise HTTPException(
                status_code=400,
                detail="Missing Clerk user information"
            )

        email = email_addresses[0].get("email_address")

        # Prevent duplicate users if Clerk retries the webhook.
        existing_user = (
            db.query(User)
            .filter(User.clerk_user_id == clerk_user_id)
            .first()
        )

        if existing_user:
            return {
                "message": "User already exists"
            }

        user = User(
            clerk_user_id=clerk_user_id,
            email=email
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "User created",
            "user_id": str(user.id)
        }

    return {
        "message": "Webhook received",
        "event_type": event_type
    }