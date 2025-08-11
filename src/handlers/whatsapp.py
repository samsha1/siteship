import os
import httpx
from src.common.config import settings
from src.common.logger import get_logger
logger = get_logger(__name__)
from twilio.twiml.messaging_response import MessagingResponse
from src.core.models import get_twilio_client

TWILIO_ACCOUNT_SID=settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN= settings.TWILIO_AUTH_TOKEN

twilio_client = get_twilio_client()

def send_message(from_whatsapp_number:str, to_number:str, text: str) -> None:
    """Send a WhatsApp message using Twilio.

    Args:
        from_whatsapp_number (str): _description_
        to_number (str): _description_
        text (str): _description_
    """
    twilio_client.messages.create(
        body=text,
        from_=from_whatsapp_number,
        to=to_number  # e.g. 'whatsapp:+97798XXXXXXX'
    )
