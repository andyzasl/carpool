import logging
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers
from src.services.trip import close_expired_trips
from src.database.db import Base, engine
from sentry_sdk import capture_exception

# Initialize Sentry before the bot application
setup_sentry()

application: Application = None  # Global variable for the Telegram bot application

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

def main():
    global application
    setup_sentry()  # Initialize Sentry
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    set_bot_commands(application)
    register_handlers(application)

    # Set up webhook
    application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

    # Start the bot
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=WEBHOOK_URL.split("/")[-1],
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()  # Call the synchronous main function
