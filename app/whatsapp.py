"""Helpers for integrating with the Meta WhatsApp Cloud API."""

from __future__ import annotations

import os
from typing import Any

import requests

from app.config import LOGGER


def send_whatsapp_message(to_number: str, message: str) -> dict[str, Any]:
    """Send a WhatsApp message through the Meta Cloud API."""
    access_token = os.getenv("META_ACCESS_TOKEN")
    phone_number_id = os.getenv("META_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
        LOGGER.warning("Meta WhatsApp credentials are not configured")
        return {"status": "not_configured"}

    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()
