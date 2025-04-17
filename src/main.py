from fastapi import FastAPI, Request, HTTPException
from sentry_sdk import capture_exception, push_scope
from telegram import Update
from telegram.ext import Application, CallbackContext
from contextlib import asynccontextmanager
import logging
import asyncio
from xata.client import XataClient
from src.config.config import ADMIN_IDS, TELEGRAM_TOKEN, WEBHOOK_URL, setup_sentry
from src.handlers.commands import register_handlers
# Removed unused imports: os, CommandHandler, MessageHandler, filters
