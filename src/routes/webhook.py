# routes/webhook.py
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
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

    get_model_instances =  ModelClients.get_instance()
    code = None
    if get_model_instances.gemini_client:
        code = await get_model_instances.gemini_client.generate_website_code(user_input)
        if code:
            # call Supabase client to store the generated code
            supabase_client = get_model_instances.supabase_client()
            
            
            # Store to memcached or database if needed for model memory with user metadata
            # For example, you can store the code in a table named 'generated_codes'
            #store file index.html file in storage and return the storage URL
            
            # can we snapshot the code (?)
            
            """Send the generated code back to the user via Telegram"""
            await send_message(chat_id, f"Here's your generated website code:\n\n{code}...")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": True, "message": "Code generated and sent successfully!"}
            )  
        

    await send_message(chat_id, "Sorry, I couldn't generate the code for your request. Please try again later.")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Message Failed to send"},
    )
