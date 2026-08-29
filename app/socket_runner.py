"""Run a Slack Socket Mode bot that uses the project's knowledge base.

Usage:
  - Create a `.env` in the project root with `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`.
  - Optionally set `SLASH_COMMAND_NAME` to match your slash command (e.g. /schoolbot-ping).
  - Run: `python -m app.socket_runner` or `python app/socket_runner.py`

This runner uses `slack-bolt` and Socket Mode so you don't need a public URL.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.knowledge import answer_question, load_documents
from app.config import LOGGER


ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = ROOT / "knowledge_base"
DOCUMENTS = load_documents(KNOWLEDGE_BASE_PATH)


def main() -> None:
    load_dotenv(ROOT / ".env")

    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    slash_command = os.getenv("SLASH_COMMAND_NAME", "/schoolbot-ping")

    if not bot_token or not app_token:
        LOGGER.error("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in .env")
        sys.exit(1)

    app = App(token=bot_token)

    @app.command(slash_command)
    def handle_command(ack, respond, command, logger):
        ack()
        text = command.get("text", "") or ""
        logger.info("Slash command received: %s", text)
        answer = answer_question(text, DOCUMENTS)
        respond(text=answer)

    # Also register a handler for the common `/bot-ping` command to avoid
    # mismatches between the registered Slack command and the environment.
    @app.command("/bot-ping")
    def handle_bot_ping(ack, respond, command, logger):
        import time

        start = time.time()
        ack()
        text = command.get("text", "") or ""
        logger.info("/bot-ping received: %s", text)
        if not text.strip():
            latency_ms = int((time.time() - start) * 1000)
            respond(text=f"Pong!\nLatency: {latency_ms}ms")
            return

        # If the command included a question, answer from the knowledge base.
        answer = answer_question(text, DOCUMENTS)
        respond(text=answer)

    @app.event("message")
    def handle_message(body, say, logger):
        event = body.get("event", {})
        # Ignore bot messages and message subtypes
        if event.get("subtype") is not None or event.get("bot_id") is not None:
            return

        text = event.get("text", "") or ""
        channel = event.get("channel")
        logger.info("Message event in %s: %s", channel, text)
        answer = answer_question(text, DOCUMENTS)
        say(text=answer)

    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()
