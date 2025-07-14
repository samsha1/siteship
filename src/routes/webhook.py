# routes/webhook.py
from fastapi import APIRouter, Request
from src.handlers.telegram import send_message
from src.core.models import ModelClients
router = APIRouter()

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook requests."""
    payload = await request.json()

    chat_id = payload.get("message", {}).get("chat", {}).get("id")
    user_input = payload.get("message", {}).get("text", "")

    if not chat_id or not user_input:
        return {"ok": False, "reason": "Invalid payload"}

    gemini_client =  ModelClients.get_instance().gemini_client
    code = None
    if gemini_client:
        code = await gemini_client.generate_website_code(user_input)

    await send_message(chat_id, f"Here's your generated website:\n\n{code}...")

    return {"ok": True}
