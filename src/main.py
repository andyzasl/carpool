from telegram.ext import Application
from telegram import BotCommand
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, setup_sentry  # Ensure correct relative import
from src.handlers.commands import register_handlers  # Ensure correct relative import
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.trip import close_expired_trips  # Ensure correct relative import
import logging
from src.database.db import Base, engine  # Ensure correct relative import
from flask import Flask, request, jsonify  # Add Flask for Vercel handler


async def set_bot_commands(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Register as a user"),
        BotCommand("switch_role", "Switch between driver and passenger roles"),
        BotCommand("create_trip", "Create a new trip (drivers only)"),
        BotCommand("get_trip", "Get details of a specific trip"),
        BotCommand("list_trips", "List all trips"),
        BotCommand("help", "Show help message"),
        BotCommand("admin_status", "List full database status (admin only)"),  # Add new command
        BotCommand("my_id", "Show your Telegram ID")  # Add new command
    ])

def main():
    setup_sentry()  # Initialize Sentry
    print('Admins:', ADMIN_IDS)
    # Ensure database schema is initialized
    Base.metadata.create_all(bind=engine)

    application = Application.builder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
    register_handlers(application)

    scheduler = BackgroundScheduler()
    scheduler.add_job(close_expired_trips, "cron", hour=0, minute=0)  # Run at midnight
    scheduler.start()

    try:
        application.run_polling()
    except Exception as e:
        logging.exception("An error occurred in the bot.")
        raise

app = Flask(__name__)  # Flask app for Vercel

@app.route("/api", methods=["POST"])
def vercel_handler():
    """
    Handle HTTP requests for Vercel deployment.
    """
    try:
        data = request.get_json()
        # Example: Respond with received data
        return jsonify({"message": "Request received", "data": data}), 200
    except Exception as e:
        logging.exception("Error in Vercel handler.")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == "__main__":
    main()
