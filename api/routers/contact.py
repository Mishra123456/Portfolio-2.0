from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.models import ContactMessage
from api.schemas import ContactCreate, ContactResponse
from services.email import send_notification_email
from core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=201)
@limiter.limit("5/minute")
async def create_contact_message(
    request: Request,
    contact: ContactCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Received contact message from {contact.email}")
    try:
        # 1. Save to DB
        new_message = ContactMessage(
            full_name=contact.full_name,
            email=contact.email,
            message=contact.message
        )
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        logger.info(f"Saved message to DB with ID: {new_message.id}")
        
        # 2. Trigger background email
        background_tasks.add_task(send_notification_email, contact)
        
        return new_message
    except Exception as e:
        logger.error(f"Error processing contact message: {e}")
        raise
