"""Helpers for sending WhatsApp messages with Twilio."""

from __future__ import annotations

import os
from typing import Any

from twilio.rest import Client

from app.config import LOGGER


def send_twilio_message(to_number: str, message: str) -> dict[str, Any]:
    """Send a WhatsApp message through the Twilio API."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    if not account_sid or not auth_token or not from_number:
        LOGGER.warning("Twilio credentials are not configured")
        return {"status": "not_configured"}

    client = Client(account_sid, auth_token)
    response = client.messages.create(
        from_=from_number,
        to=to_number,
        body=message,
    )
    return {"sid": response.sid, "status": response.status}
