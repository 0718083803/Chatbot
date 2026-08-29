"""Helpers for integrating with Slack."""

from __future__ import annotations

import os
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.config import LOGGER


def send_slack_message(channel: str, message: str) -> dict[str, Any]:
    """Send a message to a Slack channel using the bot token.

    If the `SLACK_BOT_TOKEN` is not configured, the function returns
    a sentinel value so the caller can continue in test environments.
    """
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        LOGGER.warning("Slack bot token is not configured")
        return {"status": "not_configured"}

    client = WebClient(token=token)
    try:
        resp = client.chat_postMessage(channel=channel, text=message)
        return {"ts": resp["ts"], "status": "sent"}
    except SlackApiError as error:  # pragma: no cover - defensive
        LOGGER.exception("Failed to send Slack message: %s", error)
        return {"status": "error", "error": str(error)}
