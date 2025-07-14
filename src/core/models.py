from functools import cached_property
from typing import Optional

import google.genai as genai
from src.common.config import settings
from src.common.logger import get_logger
import httpx
from supabase import ClientOptions, create_client, Client as SupabaseClient
from src.services.gemini import Gemini

logger = get_logger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY


class ModelClients:
    _instance: Optional["ModelClients"] = None

    def __init__(self):
        pass  # No explicit init needed

    @cached_property
    def gemini_client(self) -> Gemini:
        """
            Initialize and return the Gemini client.
        Returns:
            genai.Client: _description_
        """
        logger.info("Initializing Gemini client")
        initialize_gemini = genai.Client(api_key=GEMINI_API_KEY)
        return Gemini(initialize_gemini)

    @cached_property
    def supabase_client(self) -> SupabaseClient:
        """
            Initialize and return the Supabase client.
        Returns:
            SupabaseClient: _description_
        """
        logger.info("Initializing Supabase client")
        httpx_client = httpx.AsyncClient()
        
        options = ClientOptions(
            httpx_client=httpx_client,
            headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
        )
        
        _db_client:SupabaseClient = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY,options=options
        )
        if _db_client is None:
            raise Exception("Database _db_client not available")
        return _db_client

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
    instance = ModelClients.get_instance()
    return instance.gemini_client
