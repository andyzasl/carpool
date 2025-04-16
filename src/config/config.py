import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Load Telegram bot token from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///carpool.db")  # Default to local SQLite file
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Load admin IDs from environment variables
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
