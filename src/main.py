from fastapi import FastAPI, Request
from telegram.ext import Application, ApplicationBuilder
from telegram.ext.webhook import WebhookHandler
from src.config.config import TELEGRAM_TOKEN, setup_sentry, WEBHOOK_URL
from src.handlers.commands import register_handlers
from src.database.db import Base, engine  # Ensure correct relative import
import logging

# Initialize FastAPI app
app = FastAPI()

# Initialize Sentry
setup_sentry()

# Ensure database schema is initialized
Base.metadata.create_all(bind=engine)

# Initialize Telegram bot application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
register_handlers(application)

# Set up webhook handler
webhook_handler = WebhookHandler(application)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.
    """
    return await webhook_handler.handle(request)

@app.on_event("startup")
async def on_startup():
    """
    Set the webhook URL when the application starts.
    """
    await application.bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    """
    Clean up resources when the application shuts down.
    """
    await application.shutdown()
