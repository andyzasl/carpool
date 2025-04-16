import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Load Telegram bot token from environment variables
XATA_DATABASE_URL = os.getenv("XATA_DATABASE_URL")  # Xata.io database URL
DATABASE_URL = XATA_DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///carpool.db")  # Use Xata if configured, else SQLite
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# Safely parse ADMIN_IDS environment variable
try:
    ADMIN_IDS = list(map(int, filter(None, os.getenv("ADMIN_IDS", "").split(","))))
except ValueError:
    ADMIN_IDS = []  # Default to an empty list if parsing fails

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Webhook URL for Telegram bot

logging.basicConfig(level=logging.INFO)

def setup_sentry():
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.INFO
    )
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging, SqlalchemyIntegration()],
        traces_sample_rate=1.0,  # Adjust sampling rate as needed
    )
