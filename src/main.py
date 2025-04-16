from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler
from contextlib import asynccontextmanager
import logging
import os
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

        # Set the webhook
        await application.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")

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
        # Fallback: Reinitialize if application is None
        if application is None:
            logger.warning("Application is None, reinitializing")
            initialize_application()
            await application.bot.set_webhook(url=settings.webhook_url)
            logger.info("Application reinitialized and webhook set")

        json_data = await request.json()
        update = Update.de_json(json_data, application.bot)
        if not update:
            logger.warning("Invalid update received")
            return {"ok": False}

        # Process the update
        await application.process_update(update)
        logger.info("Update processed successfully")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Example handler
async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Processing /start command")
    await update.message.reply_text("Hello! I'm your bot.")
