
from fastapi import FastAPI
from src.common.config import settings
import uvicorn
from contextlib import asynccontextmanager
from src.common.logger import get_logger
from src.core.models import init_supabase_client, init_twilio_client, init_gemini_client
from src.routes import webhook

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Lifespan event handler for FastAPI application startup and shutdown.
    """
    logger.info("Starting SiteshipAI API")
    try:
        # Initialize AI & DB models and store in app.state
        app.state.supabase = await init_supabase_client()
        app.state.twilio = init_twilio_client()
        app.state.gemini = init_gemini_client()
        
        logger.info("Application started successfully")

        yield
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
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
