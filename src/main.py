import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers
from src.services.trip import close_expired_trips
import logging
from src.database.db import Base, engine
from sentry_sdk import capture_exception
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.asyncio import AsyncioIntegration

# Initialize Sentry before FastAPI app
setup_sentry()

# FastAPI app for deployment
app = FastAPI()

application: Application = None  # Global variable for the Telegram bot application

async def set_bot_commands(application: Application):
    await application.bot.set_my_commands([
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
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram updates via webhook.
    """
    global application
    if application is None:  # Ensure application is initialized
        await main()  # Call main() to initialize the application
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)  # Process the update directly
        return JSONResponse({"status": "ok"}, status_code=200)
    except Exception as e:
        logging.exception("Error in Telegram webhook handler: ", e)
        capture_exception(e)  # Send exception details to Sentry
        return JSONResponse({"error": "An error occurred"}, status_code=500)

@app.post("/api")
async def vercel_handler(request: Request):
    """
    Handle HTTP requests for Vercel deployment.
    """
    try:
        data = await request.json()
        return JSONResponse({"message": "Request received", "data": data}, status_code=200)
    except Exception as e:
        logging.exception("Error in Vercel handler.")
        capture_exception(e)  # Send exception details to Sentry
        return JSONResponse({"error": "An error occurred"}, status_code=500)

async def main():
    global application
    setup_sentry()  # Initialize Sentry
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
    register_handlers(application)

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main function

