# /backend/main.py
# Main FastAPI app entry point.

from fastapi import FastAPI, Request, HTTPException
from src.handlers import telegram

app = FastAPI()

@app.get("/ping")
async def ping():
    """A simple test route to check if the server is running."""
    return {"ping": "pong"}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """
    Endpoint to receive webhooks from the Telegram Bot API.
    """
    try:
        payload = await request.json()
        telegram.handle_telegram_webhook(payload)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))