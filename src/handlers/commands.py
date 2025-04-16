import logging
from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from src.services.user import register_user, switch_role, get_user  # Ensure correct relative import
from src.services.trip import create_trip, get_trip, list_trips  # Ensure correct relative import
from src.services.admin import get_full_status  # Ensure correct relative import
from src.config.config import ADMIN_IDS

def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("switch_role", switch_role_command))
    application.add_handler(CommandHandler("create_trip", create_trip_command))
    application.add_handler(CommandHandler("get_trip", get_trip_command))
    application.add_handler(CommandHandler("list_trips", list_trips_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin_status", admin_status_command))
    application.add_handler(CommandHandler("my_id", my_id_command))  # Register new command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        name = update.effective_user.full_name
        register_user(telegram_id=telegram_id, name=name)  # Ensure no explicit session argument
        await update.message.reply_text(f"Welcome, {name}! You have been registered as a passenger.")
    except Exception as e:
        logging.exception("Error in /start command.")
        await update.message.reply_text("An error occurred. Please try again later.")

async def switch_role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        user = get_user(telegram_id=telegram_id)  # Pass telegram_id
        if user:
            new_role = "driver" if user.role == "passenger" else "passenger"
            switch_role(user_id=user.id, new_role=new_role)
            await update.message.reply_text(f"Your role has been switched to {new_role}.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        logging.exception("Error in /switch_role command.")
        await update.message.reply_text("An error occurred while switching roles. Please try again.")

async def create_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        user = get_user(telegram_id=telegram_id)  # Ensure the user is registered
        if user and user.role == "driver":
            # Example: Prompt the driver to provide trip details
            await update.message.reply_text(
                "Please provide trip details (e.g., seats and pickup points)."
            )
        elif user:
            await update.message.reply_text("Only drivers can create trips. Switch to driver role using /switch_role.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        logging.exception("Error in /create_trip command.")
        await update.message.reply_text("An error occurred while creating the trip. Please try again.")

async def get_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        user = get_user(telegram_id=telegram_id)  # Ensure the user is registered
        if user:
            if context.args:  # Check if trip ID is provided
                trip_id = int(context.args[0])
                trip_details = get_trip(trip_id=trip_id)
                if trip_details:
                    response = f"Trip Details:\nID: {trip_details['id']}\nDriver: {trip_details['driver_handler']}\nStatus: {trip_details['status']}\nCreated At: {trip_details['created_at']}\nPickup Points:\n"
                    for point in trip_details["pickup_points"]:
                        response += f"- {point['address']} at {point['time']}\n"
                    await update.message.reply_text(response)
                else:
                    await update.message.reply_text("Trip not found.")
            else:
                await update.message.reply_text("Please provide a trip ID. Usage: /get_trip <trip_id>")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except ValueError:
        await update.message.reply_text("Invalid trip ID. Please provide a valid number.")
    except Exception as e:
        logging.exception("Error in /get_trip command.")
        await update.message.reply_text("An error occurred while retrieving the trip. Please try again.")

async def list_trips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        user = get_user(telegram_id=telegram_id)  # Ensure the user is registered
        if user:
            trips = list_trips()  # Fetch all trips
            if trips:
                response = "Available Trips:\n"
                for trip in trips:
                    response += f"- Trip ID: {trip['id']}, Driver ID: {trip['driver_id']}, Status: {trip['status']}\n"
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("No trips are currently available.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        logging.exception("Error in /list_trips command.")
        await update.message.reply_text("An error occurred while listing trips. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provide a list of available commands and their descriptions.
    """
    help_text = (
        "Here are the available commands:\n"
        "/start - Register as a user\n"
        "/switch_role - Switch between driver and passenger roles\n"
        "/create_trip - Create a new trip (drivers only)\n"
        "/get_trip <trip_id> - Get details of a specific trip\n"
        "/list_trips - List all trips\n"
        "/admin_status - List full database status (admin only)\n"
        "/my_id - Show your Telegram ID\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def admin_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provide a full database status for admin users.
    """
    try:
        telegram_id = update.effective_user.id
        if telegram_id in ADMIN_IDS:  # Check if the user's Telegram ID is in ADMIN_IDS
            status = get_full_status()  # Fetch full database status
            await update.message.reply_text(f"Status:\n{status}")
        else:
            await update.message.reply_text("You do not have permission to access this command.")
    except Exception as e:
        logging.exception("Error in /admin_status command.")
        await update.message.reply_text("An error occurred while fetching the database status. Please try again.")

async def my_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Respond with the user's Telegram ID.
    """
    try:
        telegram_id = update.effective_user.id
        await update.message.reply_text(f"Your Telegram ID is: {telegram_id}")
    except Exception as e:
        logging.exception("Error in /my_id command.")
        await update.message.reply_text("An error occurred. Please try again later.")


