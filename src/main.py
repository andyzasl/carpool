from fastapi import FastAPI, Request, HTTPException
from sentry_sdk import capture_exception, push_scope  # Import push_scope for detailed context
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters
from contextlib import asynccontextmanager
import logging
import os
import asyncio
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

setup_sentry()

# Global Application instance
application = None

def initialize_application():
    """Initialize the Telegram Application and register handlers."""
    global application
    try:
        if application is not None:
            logger.warning("Application already initialized, skipping reinitialization")
            return application

        logger.info("Creating new Telegram Application")
        application = (
            Application.builder()
            .token(TELEGRAM_TOKEN)
            .build()
        )
        register_handlers(application)

        logger.info("Handlers registered")
        logger.info(f"Registered handlers: {[str(h) for h in application.handlers[0]]}")
        return application
    except Exception as e:
        with push_scope() as scope:
            scope.set_tag("function", "initialize_application")
            scope.set_extra("error_message", str(e))
            capture_exception(e)
        logger.error(f"Failed to initialize Application: {str(e)}")
        application = None
        raise

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    global application
    logger.info("Starting lifespan handler")
    try:
        # Initialize the Telegram bot application
        initialize_application()

        if not application:
            logger.error("Application initialization failed")
            raise ValueError("Application not initialized")

        # Initialize the application
        logger.info("Calling application.initialize()")
        await application.initialize()
        logger.info("Application initialized successfully")

        # Set the webhook
        logger.info("Setting webhook")
        await application.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")

        yield  # Application runs here

    except Exception as e:
        logger.error(f"Error in lifespan startup: {str(e)}")
        capture_exception(e)
        raise
    finally:
        # Shutdown: Clean up
        if application:
            logger.info("Stopping application")
            await application.stop()
            logger.info("Application stopped")
            application = None
        else:
            logger.warning("No application instance found during shutdown")

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    """Handle webhook updates."""
    global application
    logger.info("Received webhook request")
    try:
        if not application:
            logger.error("Application not initialized")
            initialize_application()

        json_data = await request.json()
        logger.info(f"Raw update JSON: {json_data}")
        update = Update.de_json(json_data, application.bot)
        if not update:
            logger.warning("Invalid update received")
            return {"ok": False}

        logger.info("Update seems to be ok")
        logger.info(f"Parsed update: {update.to_dict()}")

        # Attempt process_update with state check
        logger.info("Checking application state before process_update")
        try:
            await application.initialize()
            await application.process_update(update)
            logger.info("Update processed successfully")
        except Exception as e:
            with push_scope() as scope:
                scope.set_tag("function", "webhook")
                scope.set_extra("update_data", update.to_dict())
                scope.set_extra("error_message", str(e))
                capture_exception(e)
            logger.error(f"Error in process_update: {str(e)}")
            logger.warning("Falling back to manual dispatch due to process_update error")
        return {"ok": True}
    except Exception as e:
        with push_scope() as scope:
            scope.set_tag("function", "webhook")
            scope.set_extra("request_data", await request.body())
            scope.set_extra("error_message", str(e))
            capture_exception(e)
        logger.error(f"Error in webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Command handler
async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Processing /start command")
    logger.info(f"Update details: {update.to_dict()}")
    try:
        await update.message.reply_text("Hello! I'm your bot.")
        logger.info("Reply sent successfully")
    except Exception as e:
        logger.error(f"Failed to send reply: {str(e)}")
        capture_exception(e)

# Echo handler for all text messages
async def echo(update: Update, context: CallbackContext) -> None:
    logger.info(f"Received message: {update.message.text}")
    try:
        await update.message.reply_text(f"Echo: {update.message.text}")
        logger.info("Echo reply sent")
    except Exception as e:
        logger.error(f"Failed to send echo reply: {str(e)}")
        capture_exception(e)

# Debug handler for all updates
async def debug_update(update: Update, context: CallbackContext) -> None:
    logger.debug(f"Debug: Received update: {update.to_dict()}")

