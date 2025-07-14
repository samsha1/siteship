
from fastapi import FastAPI
from src.routes import webhook
from src.common.config import settings
import uvicorn
from contextlib import asynccontextmanager
import httpx
from supabase import create_client, Client, ClientOptions
from src.common.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Lifespan event handler for FastAPI application startup and shutdown.
    """
    logger.info("Starting SiteshipAI API")
    try:
        httpx_client = httpx.AsyncClient()
        
        options = ClientOptions(
            httpx_client=httpx_client,
            headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
        )
        
        app.state.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY,options=options
        )
        logger.info("Application started successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        await httpx_client.aclose()
        logger.info("Shutting down SiteshipAI API")
    

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for linking products to EPD using RAG",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )
    app.include_router(webhook.router)
    return app


app = create_app()


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=settings.WORKERS,
    )
