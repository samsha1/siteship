from fastapi import FastAPI, Request, HTTPException
from src.handlers.telegram import send_message
from src.common.logger import get_logger

logger = get_logger(__name__)

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
        logger.info("Received webhook payload: %s", payload)
        return  await send_message(
            chat_id=payload.get("message", {}).get("chat", {}).get("id"),
            text=f"Received message: {payload.get('message', {}).get('text', '')}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))