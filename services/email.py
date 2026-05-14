import httpx
import logging
from api.schemas import ContactCreate
from core.config import settings

logger = logging.getLogger(__name__)

def send_notification_email(contact: ContactCreate):
    """
    Background task to forward the contact message to Formspree.
    """
    logger.info(f"Forwarding contact message to Formspree: {settings.FORMSPREE_URL}")
    
    if not settings.FORMSPREE_URL:
        logger.warning("FORMSPREE_URL is empty! Cannot forward message.")
        return

    payload = {
        "full_name": contact.full_name,
        "email": contact.email,
        "message": contact.message,
        "_subject": f"Portfolio Message from {contact.full_name}"
    }

    try:
        response = httpx.post(settings.FORMSPREE_URL, json=payload)
        if response.status_code == 200:
            logger.info("Message forwarded to Formspree successfully!")
        else:
            logger.error(f"Formspree returned error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to forward message to Formspree: {e}")
