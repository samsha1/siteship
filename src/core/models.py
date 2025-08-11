from functools import cached_property
from typing import Optional

import google.genai as genai
from src.common.config import settings
from src.common.logger import get_logger
import httpx
from supabase import ClientOptions, create_client, Client as SupabaseClient
from src.services.gemini import Gemini
from twilio.rest import Client as TwilioClient


logger = get_logger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY
TWILIO_ACCOUNT_SID=settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN= settings.TWILIO_AUTH_TOKEN

_gemini_client: Optional[Gemini] = None
_supabase_client: Optional[SupabaseClient] = None
_twilio_client: Optional[TwilioClient] = None


class ModelClients:
    _instance: Optional["ModelClients"] = None

    def __init__(self):
        pass  # No explicit init needed

    def gemini_client(self) -> Gemini:
        """
            Initialize and return the Gemini client.
        Returns:
            genai.Client: _description_
        """
        logger.info("Initializing Gemini client")
        initialize_gemini = genai.Client(api_key=GEMINI_API_KEY)
        return Gemini(initialize_gemini)

    def supabase_client(self) -> SupabaseClient:
        """
            Initialize and return the Supabase client.
        Returns:
            SupabaseClient: _description_
        """
        logger.info("Initializing Supabase client")
        # httpx_client = httpx.AsyncClient()
        http_client = httpx.Client()

        options = ClientOptions(
            httpx_client=http_client,
            headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
        )
        
        _db_client:SupabaseClient = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY,options=options
        )
        if _db_client is None:
            raise Exception("Database _db_client not available")
        return _db_client

    def twillio_client(self) -> TwilioClient:
        """Initiate Twilio Client

        Returns:
            TwilioClient: _description_
        """
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        if twilio_client is None:
            raise Exception("Twilio _client not available")
        return twilio_client


    @classmethod
    def get_instance(cls) -> "ModelClients":
        """
            Get the singleton instance of ModelClients.
        Returns:
            ModelClients: _description_
        """
        if cls._instance is None:
            cls._instance = ModelClients()
        return cls._instance


def get_gemini_client() -> genai.Client:
    """
    Get the Gemini client singleton.
    """
    global _gemini_client
    
    if _gemini_client is None:
        try:
            init_clients()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    return _gemini_client

def get_supabase_client() -> SupabaseClient:
    """
    Get the Supabase client singleton.
    """
    global _supabase_client
    if _supabase_client is None:
        try:
            init_clients()
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
    return _supabase_client

def get_twilio_client() -> TwilioClient:
    """
    Get the Twilio client singleton.
    """
    global _twilio_client
    if not _twilio_client:
        try:
            init_clients()
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            
    return _twilio_client




def init_clients() -> None:
    """
    Initialize the instances.

    Raises:
        Exception: If model initialization fails
    """
    global _supabase_client, _twilio_client, _gemini_client
    try:
        logger.info("Initializing RAG models and OpenAI model validation")

        # Fetch available OpenAI models first
        models = ModelClients.get_instance()
        _supabase_client = models.supabase_client()
        if _supabase_client is None:
            raise Exception("Database client not available for model initialization")

        _gemini_client = models.gemini_client()
        _twilio_client = models.twillio_client()
        logger.info("RAG models initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize RAG models: {e}")
        raise
