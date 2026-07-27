"""Configuration helpers for the FastAPI app."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "School WhatsApp Chatbot")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV.lower() == "development"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
LOGGER = logging.getLogger("school_chatbot")
