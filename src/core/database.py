"""
Database core module for managing database connections.
"""

from typing import Optional

import httpx

from src.common.config import settings
from src.utils.logger import get_logger
from supabase import ClientOptions, create_client, Client

# This is not used in the current context, but kept for reference

logger = get_logger(__name__)

_db_client: Optional[Client] = None


def init_db_client() -> Client:
    """
    Initialize the global database client.

    Returns:
        SupabaseClient: Initialized database client

    Raises:
        Exception: If database initialization fails
    """
    global _db_client

    try:
        logger.info("Initializing database client")

        httpx_client = httpx.AsyncClient()
        
        options = ClientOptions(
            httpx_client=httpx_client,
            headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
        )
        
        _db_client:Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY,options=options
        )

        return _db_client

    except Exception as e:
        logger.error(f"Failed to initialize database client: {e}")
        raise


def get_db_client() -> Optional[Client]:
    """
    Get the global database client instance.

    Returns:
        SupabaseClient: Database client instance or None if not initialized
    """
    global _db_client

    if _db_client is None:
        logger.warning("Database client not initialized, attempting to initialize")
        try:
            return init_db_client()
        except Exception as e:
            logger.error(f"Failed to get database client: {e}")
            return None

    return _db_client


def close_db_client() -> None:
    """
    Close the global database client connection.
    """
    global _db_client

    if _db_client is not None:
        logger.info("Closing database client")
        # !info: -
        # SupabaseClient doesn't have explicit close method 
        # but we can reset the global reference
        _db_client = None
        logger.info("Database client closed")


def check_db_health() -> bool:
    """
    Check if the database connection is healthy.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        client = get_db_client()
        if client is None:
            return False

        return True

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
