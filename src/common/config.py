"""
Configuration settings for the EPD Product Linking.
"""

from typing import List, Optional
from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    APP_NAME: str = Field(default="SiteshipAI API", description="API that works with AI Code agents to create web pages via Telegram/WhatsApp bots")
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    HOST: str = Field(default="0.0.0.0", description="Host to bind the application to")
    PORT: int = Field(default=8000, description="Port to bind the application to")
    WORKERS: int = Field(default=1, description="Number of worker processes")

    SIGNATURE_SECRET: str = Field(
        ..., description="Secret key for signature verification"
    )
    ENABLE_AUTH: bool = Field(default=True, description="Enable API authentication")

    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "https://materialisting.com",
        ],
        description="Allowed CORS origins",
    )

    RATE_LIMIT_REQUESTS: int = Field(
        default=100, description="Rate limit requests per minute"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    SSL_KEYFILE: Optional[str] = Field(None, description="SSL private key file path")
    SSL_CERTFILE: Optional[str] = Field(None, description="SSL certificate file path")

    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase project API key")
    SUPABASE_AUTH_EMAIL: Optional[str] = Field(
        None, description="Supabase authentication email"
    )
    SUPABASE_AUTH_PASSWORD: Optional[str] = Field(
        None, description="Supabase authentication password"
    )

    # OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    EMBEDDING_MODEL: str = Field(
        "text-embedding-3-large", description="OpenAI embedding model name"
    )
    EMBEDDING_MODEL_DIMENSION: int = Field(
        3072,
        description="The text-embedding-3-large model has a size of 3072 dimensions",
    )
    EMBEDDING_MODEL_PRICE: float = Field(
        0.13,
        description="The pricing for text-embedding-3-large is $0.13 per 1 million tokens",
    )
    COMPLETION_MODEL: str = Field(..., description="OpenAI completion model name")

    SUPPORTED_LLM_MODELS: List[str] = Field(
        ["gemini-2.5-pro", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"],
        description="Supported LLM models",
    )
    
    TELEGRAM_BOT_TOKEN: str = Field(
        ..., description="Telegram bot token for webhook integration"
    )
    
    GEMINI_API_KEY: str = Field(
        ..., description="Gemini API key for code generation"
    )

   

    CHUNK_SIZE: int = Field(100, description="Size of data processing chunks")
    TOP_K: int = Field(5, description="Number of top results to retrieve")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError(
                "Environment must be one of: development, staging, production"
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore',
    )


settings = Settings()
