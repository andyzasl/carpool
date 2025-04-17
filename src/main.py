from fastapi import FastAPI, Request, HTTPException
from sentry_sdk import capture_exception
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, Filters
from contextlib import asynccontextmanager
import logging
import os
import asyncio
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry

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
        logger.info("Initializing Telegram Application")
        application = (
            Application.builder()
            .token(TELEGRAM_TOKEN)
            .build()
        )
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))  # Handle all text messages
        logger.info("Application initialized and handlers registered")
        return application
    except Exception as e:
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

        # Initialize the application and set the webhook
        application.initialize()
        # await application.bot.set_webhook(url=WEBHOOK_URL)
        # logger.info(f"Webhook set to {WEBHOOK_URL}")

        yield  # Application runs here

    except Exception as e:
        logger.error(f"Error in lifespan startup: {str(e)}")
        raise
    finally:
        # Shutdown: Clean up
        if application:
            await application.stop()
            logger.info("Application stopped")
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
        # Initialize the Telegram bot application
        initialize_application()

        json_data = await request.json()
        logger.info(f"Raw update JSON: {json_data}")
        update = Update.de_json(json_data, application.bot)
        if not update:
            logger.warning("Invalid update received")
            return {"ok": False}

        logger.info("Update seems to be ok")
        logger.info(f"Parsed update: {update.to_dict()}")
        # Run process_update in a thread to avoid blocking
        await asyncio.get_event_loop().run_in_executor(None, application.process_update, update)
        logger.info("Update processed successfully")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        capture_exception(e)
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
