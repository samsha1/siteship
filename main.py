
from fastapi import FastAPI
from src.routes import webhook

app = FastAPI()
app.include_router(webhook.router)
