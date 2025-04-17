import logging
from telegram.ext import CommandHandler, ContextTypes, CallbackContext, Application
from telegram import Update
from src.services.user import register_user, switch_role, get_user  # Ensure correct relative import
from src.services.trip import create_trip, get_trip, list_trips  # Ensure correct relative import
from src.services.admin import get_full_status  # Ensure correct relative import
from src.config.config import ADMIN_IDS
from sentry_sdk import capture_exception, push_scope  # Import Sentry's exception capture function and push_scope
from xata.client import XataClient  # Ensure Xata client is used

xata = XataClient()  # Initialize Xata client

def register_handlers(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("switch_role", switch_role_command))
    application.add_handler(CommandHandler("create_trip", create_trip_command))
    application.add_handler(CommandHandler("get_trip", get_trip_command))
    application.add_handler(CommandHandler("list_trips", list_trips_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin_status", admin_status_command))
    application.add_handler(CommandHandler("my_id", my_id_command))  # Register new command
    application.add_error_handler(error_handler)  # Register the error handler

async def start(update: Update, context: CallbackContext) -> None:
    try:
        telegram_id = str(update.effective_user.id)  # Xata uses strings for IDs
        name = update.effective_user.full_name
        # Register user in Xata
        xata.records().upsert(table_name="users", record_id=str(telegram_id) , payload={"id": telegram_id, "name": name, "role": "passenger"})
        await update.message.reply_text(f"Welcome, {name}! You have been registered as a passenger.")
    except Exception as e:
        with push_scope() as scope:
            scope.set_tag("command", "/start")
            scope.set_extra("user_id", update.effective_user.id)
            scope.set_extra("error_message", str(e))
            capture_exception(e)  # Send exception details to Sentry
        await update.message.reply_text("An error occurred. Please try again later.")

async def switch_role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = str(update.effective_user.id)
        user = await xata.table("users").read(telegram_id)
        if user:
            new_role = "driver" if user["role"] == "passenger" else "passenger"
            await xata.table("users").update({"id": telegram_id, "role": new_role})
            await update.message.reply_text(f"Your role has been switched to {new_role}.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        with push_scope() as scope:
            scope.set_tag("command", "/switch_role")
            scope.set_extra("user_id", update.effective_user.id)
            scope.set_extra("error_message", str(e))
            capture_exception(e)  # Send exception details to Sentry
        await update.message.reply_text("An error occurred while switching roles. Please try again.")

async def create_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = str(update.effective_user.id)  # Xata uses strings for IDs
        user = await xata.table("users").read(telegram_id)  # Ensure the user is registered
        if user and user["role"] == "driver":
            # Example: Prompt the driver to provide trip details
            await update.message.reply_text(
                "Please provide trip details (e.g., seats and pickup points)."
            )
        elif user:
            await update.message.reply_text("Only drivers can create trips. Switch to driver role using /switch_role.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        capture_exception(e)  # Send exception details to Sentry
        await update.message.reply_text("An error occurred while creating the trip. Please try again.")

async def get_trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = str(update.effective_user.id)
        user = await xata.table("users").read(telegram_id)
        if user:
            if context.args:  # Check if trip ID is provided
                trip_id = str(context.args[0])
                trip_details = await xata.table("trips").read(trip_id)
                if trip_details:
                    response = (
                        f"Trip Details:\n"
                        f"ID: {trip_details['id']}\n"
                        f"Driver: {trip_details.get('driver_handler', 'N/A')}\n"
                        f"Status: {trip_details.get('status', 'N/A')}\n"
                        f"Created At: {trip_details.get('created_at', 'N/A')}\n"
                        f"Pickup Points:\n"
                    )
                    for point in trip_details.get("pickup_points", []):
                        response += f"- {point.get('address', 'Unknown')} at {point.get('time', 'Unknown')}\n"
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
        capture_exception(e)
        await update.message.reply_text("An error occurred while retrieving the trip. Please try again.")

async def list_trips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = str(update.effective_user.id)
        user = await xata.table("users").read(telegram_id)
        if user:
            trips = await xata.table("trips").get_all()
            if trips:
                response = "Available Trips:\n"
                for trip in trips:
                    response += (
                        f"- Trip ID: {trip.get('id', 'Unknown')}, "
                        f"Driver ID: {trip.get('driver_id', 'Unknown')}, "
                        f"Status: {trip.get('status', 'Unknown')}\n"
                    )
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("No trips are currently available.")
        else:
            await update.message.reply_text("You are not registered. Use /start to register.")
    except Exception as e:
        capture_exception(e)
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
        telegram_id = str(update.effective_user.id)  # Xata uses strings for IDs
        if telegram_id in ADMIN_IDS:  # Check if the user's Telegram ID is in ADMIN_IDS
            status = await xata.db().table("status").get_full()  # Fetch full database status
            await update.message.reply_text(f"Status:\n{status}")
        else:
            await update.message.reply_text("You do not have permission to access this command.")
    except Exception as e:
        capture_exception(e)  # Send exception details to Sentry
        await update.message.reply_text("An error occurred while fetching the database status. Please try again.")

async def my_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Respond with the user's Telegram ID.
    """
    try:
        telegram_id = str(update.effective_user.id)  # Xata uses strings for IDs
        await update.message.reply_text(f"Your Telegram ID is: {telegram_id}")
    except Exception as e:
        capture_exception(e)  # Send exception details to Sentry
        await update.message.reply_text("An error occurred. Please try again later.")

async def error_handler(update: object, context: CallbackContext) -> None:
    """
    Log the error and send a message to the user.
    """
    logging.error(f"Exception while handling an update: {context.error}")
    with push_scope() as scope:
        scope.set_tag("handler", "error_handler")
        scope.set_extra("update", update.to_dict() if isinstance(update, Update) else str(update))
        scope.set_extra("error_message", str(context.error))
        capture_exception(context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. Please try again later."
        )
