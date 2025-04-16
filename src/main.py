import logging
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers
from src.database.db import Base, engine
from sentry_sdk import capture_exception
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum  # For Vercel compatibility

# Initialize Sentry before the bot application
setup_sentry()

application: Application = None  # Global variable for the Telegram bot application
fastapi_app = FastAPI()  # FastAPI app for Vercel

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

@fastapi_app.post(f"/{WEBHOOK_URL.split('/')[-1]}")
async def webhook_handler(request: Request):
    """
    Handle incoming webhook requests from Telegram.
    """
    global application
    try:
        update = await request.json()
        await application.update_queue.put(Update.de_json(update, application.bot))
        return JSONResponse(content={"ok": True})
    except Exception as e:
        capture_exception(e)
        return JSONResponse(content={"ok": False, "error": str(e)})

def main():
    global application
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
    register_handlers(application)

    # Set up webhook
    application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

# Initialize the bot application
main()

# Vercel handler
handler = Mangum(fastapi_app)
