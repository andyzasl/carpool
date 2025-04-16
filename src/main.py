import logging
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers
from src.database.db import Base, engine
from sentry_sdk import capture_exception, capture_message
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import sentry_sdk
from pprint import pprint
from contextlib import asynccontextmanager

# Initialize Sentry before the bot application
setup_sentry()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global Application instance
application = None

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Initialize the Telegram bot application
    global application
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )
    logger.info("Telegram Application initialized")
    register_handlers(application)
    set_bot_commands(application)
    # Set the webhook
    await application.bot.set_webhook(url=WEBHOOK_URL)

    # Store the application in app.state
    app.state.application = application

    yield  # Application runs here

    # Shutdown: Clean up
    await application.stop()


app = FastAPI(lifespan=lifespan)  # FastAPI app for Vercel


def set_bot_commands(application: Application):
    application.bot.set_my_commands([
        BotCommand("start", "Register as a user"),
        BotCommand("switch_role", "Switch between driver and passenger roles"),
        BotCommand("create_trip", "Create a new trip (drivers only)"),
        BotCommand("get_trip", "Get details of a specific trip"),
        BotCommand("list_trips", "List all trips"),
        BotCommand("help", "Show help message"),
        BotCommand("admin_status", "List full database status (admin only)"),
        BotCommand("my_id", "Show your Telegram ID")
    ])


@app.post("/webhook")
async def webhook(request: Request):
    """Handle webhook updates."""
    global application
    logger.info("Received webhook request")
    try:
        json_data = await request.json()
        update = Update.de_json(json_data, application.bot)

        # Process the update using the Application instance
        await application.process_update(update)
        logger.info("Update processed successfully")
        return {"ok": True}
    except Exception as e:
        # Replace with your error logging (e.g., Sentry)
        print(f"Error: {str(e)}")  # Temporary logging
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root_handler():
    """
    Return a 200 response for the root endpoint.
    """
    return JSONResponse(content={"message": "Carpool service is running"}, status_code=200)
