import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.asyncio import AsyncioIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
XATA_DATABASE_URL = os.getenv("XATA_DATABASE_URL")
DATABASE_URL = XATA_DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///carpool.db")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

try:
    ADMIN_IDS = list(map(int, filter(None, os.getenv("ADMIN_IDS", "").split(","))))
except ValueError:
    ADMIN_IDS = []

logging.basicConfig(level=logging.INFO)

def setup_sentry():
    sentry_logging = LoggingIntegration(
        level=logging.WARN,
        event_level=logging.WARN
    )
    sentry_sdk.set_level("warning")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging, SqlalchemyIntegration(), AsyncioIntegration()],
        traces_sample_rate=1.0,
    )

    vercel_context = {
        "vercel_region": os.getenv("VERCEL_REGION"),
        "vercel_env": os.getenv("VERCEL_ENV"),
        "vercel_url": os.getenv("VERCEL_URL"),
    }
    sentry_sdk.set_context("vercel_runtime", vercel_context)
