# routes/webhook.py
from fastapi import APIRouter, Request
from src.handlers.telegram import send_message
from src.services.gemini import generate_website_code

router = APIRouter()

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()

    chat_id = payload.get("message", {}).get("chat", {}).get("id")
    user_input = payload.get("message", {}).get("text", "")

    if not chat_id or not user_input:
        return {"ok": False, "reason": "Invalid payload"}

    code = await generate_website_code(user_input)

    # Optionally store in Supabase here...
    # e.g., await save_project(...)

    await send_message(chat_id, f"Here's your generated website:\n\n{code[:500]}...")

    return {"ok": True}
