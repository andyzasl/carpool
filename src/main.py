from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry  # Ensure correct relative import
from src.handlers.commands import register_handlers  # Ensure correct relative import
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.trip import close_expired_trips  # Ensure correct relative import
import logging
from src.database.db import Base, engine  # Ensure correct relative import
from flask import Flask, request, jsonify

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
def telegram_webhook():
    """
    Handle incoming Telegram updates via webhook.
    """
    try:
        data = request.get_json()
        if application:
            update = Update.de_json(data, application.bot)
            application.process_update(update)  # Process the update directly
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.exception("Error in Telegram webhook handler.")
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
        return jsonify({"error": "An error occurred"}), 500

def main():
    global application
    setup_sentry()  # Initialize Sentry
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
    register_handlers(application)

    # Set webhook for Telegram bot
    webhook_url = f"{WEBHOOK_URL}/webhook"
    application.bot.set_webhook(url=webhook_url)

    # Scheduler for background tasks
    scheduler = BackgroundScheduler()
    scheduler.add_job(close_expired_trips, "cron", hour=0, minute=0)  # Run at midnight
    scheduler.start()

if __name__ == "__main__":
    main()
