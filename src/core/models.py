from typing import Optional
import google.genai as genai
from src.common.config import settings
from src.common.logger import get_logger
from supabase import create_async_client, Client as SupabaseClient
from src.services.gemini import Gemini
from twilio.rest import Client as TwilioClient

logger = get_logger(__name__)

async def init_supabase_client() -> SupabaseClient:
    """
    Initialize and return the Supabase Async client.
    """
    logger.info("Initializing Supabase Async client")
    return await create_async_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )

def init_twilio_client() -> TwilioClient:
    """
    Initialize and return the Twilio client.
    """
    return TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def init_gemini_client() -> Gemini:
    """
    Initialize and return the Gemini client.
    """
    logger.info("Initializing Gemini client")
    initialize_gemini = genai.Client(api_key=settings.GEMINI_API_KEY)
    return Gemini(initialize_gemini)
