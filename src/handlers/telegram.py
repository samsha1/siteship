import os
import httpx
from src.common.config import settings
from src.common.logger import get_logger
logger = get_logger(__name__)
import requests

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            }
        )
        logger.info(response.text)
        response.raise_for_status()
