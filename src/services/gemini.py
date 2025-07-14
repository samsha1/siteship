import httpx
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

async def generate_website_code(user_requirements: str) -> str:
    """Generate static website code from Gemini Pro."""
    prompt_template = f"""
            You are an expert AI web developer.
            Your task is to generate a simple but complete static website...
#        (same as before)
    """

    payload = {
        "contents": [{"parts": [{"text": prompt_template}]}]
    }

    params = {"key": GEMINI_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_API_URL, params=params, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        text = (
            data["candidates"][0]["content"]["parts"][0]["text"]
            if "candidates" in data and data["candidates"]
            else ""
        )
        logger.info("Gemini raw output: %s", text)
        return text
