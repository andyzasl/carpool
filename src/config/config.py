import os
from dotenv import load_dotenv
import logging
import sentry_sdk

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def setup_sentry():
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN)


def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
    )
