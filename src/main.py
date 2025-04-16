import asyncio  # Import asyncio for running the async main function
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry  # Ensure correct relative import
from src.handlers.commands import register_handlers  # Ensure correct relative import
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.trip import close_expired_trips  # Ensure correct relative import
import logging
from src.database.db import Base, engine  # Ensure correct relative import
from flask import Flask, request, jsonify
from sentry_sdk import capture_exception  # Import Sentry's exception capture function

# Initialize Sentry before Flask app
setup_sentry()

# Flask app for Vercel
app = Flask(__name__)
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

@app.route("/webhook", methods=["POST"])
async def telegram_webhook():
    """
    Handle incoming Telegram updates via webhook.
    """
    global application
    if application is None:  # Ensure application is initialized
        main()  # Call main() to initialize the application
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)  # Process the update directly
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.exception("Error in Telegram webhook handler.")
        capture_exception(e)  # Send exception details to Sentry
        return jsonify({"error": "An error occurred"}), 500

@app.route("/api", methods=["POST"])
def vercel_handler():
    """
    Handle HTTP requests for Vercel deployment.
    """
    try:
        data = request.get_json()
        return jsonify({"message": "Request received", "data": data}), 200
    except Exception as e:
        logging.exception("Error in Vercel handler.")
        capture_exception(e)  # Send exception details to Sentry
        return jsonify({"error": "An error occurred"}), 500

async def main():
    global application
    setup_sentry()  # Initialize Sentry
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
    register_handlers(application)

    # Set webhook for Telegram bot
    webhook_url = f"{WEBHOOK_URL}/webhook"
    print(webhook_url)
    await application.bot.set_webhook(url=webhook_url)  # Await the async method

    # Scheduler for background tasks
    scheduler = BackgroundScheduler()
    scheduler.add_job(close_expired_trips, "cron", hour=0, minute=0)  # Run at midnight
    scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main function

