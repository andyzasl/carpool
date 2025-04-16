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

# Initialize Sentry before the bot application
setup_sentry()

app = FastAPI()  # FastAPI app for Vercel


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

@app.post("/webhook-x")
async def webhook_handler(request: Request):
    """
    Handle incoming webhook requests from Telegram.
    """
    sentry_sdk.set_context("app_state", {"state": pprint(app.state)})
    if not hasattr(app.state, "application") or app.state.application is None:
        capture_message("Application not initialized")
        raise RuntimeError("The application is not initialized. Ensure the on_startup function is executed.")

    try:
        # Parse the incoming update
        update = await request.json()
        telegram_update = Update.de_json(update, app.state.application.bot)  # Ensure app.state.application is set

        # Process the update asynchronously
        await app.state.application.process_update(telegram_update)  # Use await instead of create_task

        # Respond immediately to avoid timeout
        return JSONResponse(content={"ok": True})
    except Exception as e:
        # Capture exception and include all variables
        capture_exception(e)
        sentry_sdk.set_context("webhook_request", {"update": update})
        return JSONResponse(content={"ok": False, "error": str(e)})

@app.post("/webhook")
async def webhook(request: Request):
    """Handle webhook updates."""

    try:
        json_data = await request.json()
        update = Update.de_json(json_data, app.state.application.bot)

        # Pass the session to the handler
        context = CallbackContext(app.state.application)  # Create a context

        await app.state.application.process_update(update)
        return {"ok": True}
    except Exception as e:
        capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root_handler():
    """
    Return a 200 response for the root endpoint.
    """
    return JSONResponse(content={"message": "Carpool service is running"}, status_code=200)

async def on_startup():
    """
    Initialize the Telegram bot application and set up the webhook.
    """
    Base.metadata.create_all(bind=engine)  # Ensure database schema is initialized

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    register_handlers(application)
    set_bot_commands(application)

    # Set up webhook
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

    # Store the application in FastAPI state for access in the webhook handler
    app.state.application = application  # Ensure application is stored in app.state

async def on_shutdown():
    """
    Gracefully shut down the Telegram bot application.
    """
    await app.state.application.shutdown()


# Add startup and shutdown events to FastAPI
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)
