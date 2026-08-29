"""FastAPI entrypoint for the school WhatsApp chatbot backend."""

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.config import APP_NAME
from app.config import DEBUG
from app.config import LOGGER
from app.knowledge import answer_question
from app.knowledge import load_documents
from app.slack import send_slack_message

app = FastAPI(title=APP_NAME, debug=DEBUG)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"
KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent.parent / "knowledge_base"
DOCUMENTS = load_documents(KNOWLEDGE_BASE_PATH)


@app.get("/", response_class=HTMLResponse)
def read_root() -> HTMLResponse:
    """Serve the simple school question-answer web page."""
    LOGGER.info("Home page requested")
    return HTMLResponse(content=TEMPLATE_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health endpoint used for local verification and deployment checks."""
    LOGGER.info("Health check requested")
    return {"status": "ok"}


@app.get("/ask")
def ask(question: str | None = None) -> dict[str, str]:
    """Answer a question using the school knowledge base."""
    if question is None:
        return {"answer": "Please provide a question."}

    LOGGER.info("Ask endpoint requested for question: %s", question)
    return {"answer": answer_question(question, DOCUMENTS)}


@app.get("/whatsapp/webhook")
def verify_whatsapp_webhook(mode: str | None = None, challenge: str | None = None) -> dict[str, str]:
    """Legacy endpoint retained for compatibility; returns a simple OK result."""
    return {"status": "ok"}


def _extract_slack_event(payload: Any) -> tuple[str | None, str | None, dict[str, Any] | None]:
    """Extract a Slack channel and text from an events API payload.

    Returns a tuple of (channel, text, original_event). For URL verification
    payloads, returns (None, None, payload) so the caller can respond with
    the challenge.
    """
    if not isinstance(payload, dict):
        return None, None, None

    # URL verification challenge from Slack
    if payload.get("type") == "url_verification":
        return None, None, payload

    # Event callback
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        # Ignore bot messages or non-message events
        if event.get("type") != "message" or event.get("subtype") is not None:
            return None, None, None

        channel = event.get("channel")
        text = event.get("text")
        return channel, text, event

    return None, None, None


@app.post("/slack/events")
async def slack_events(request: Request) -> dict[str, str]:
    """Handle Slack Events API requests and reply with answers from docs."""
    payload = await request.json()
    channel, message_text, original = _extract_slack_event(payload)

    # Respond to URL verification challenges
    if original and original.get("type") == "url_verification":
        challenge = original.get("challenge")
        return {"challenge": challenge}

    if not channel or not message_text or not str(message_text).strip():
        LOGGER.warning("Received empty Slack message or unsupported event")
        raise HTTPException(status_code=400, detail="Message text is required")

    LOGGER.info("Incoming Slack message from channel %s", channel)
    answer = answer_question(str(message_text), DOCUMENTS)

    try:
        send_slack_message(channel, answer)
    except Exception as error:  # pragma: no cover - defensive logging
        LOGGER.exception("Failed to send Slack reply: %s", error)

    return {
        "channel": channel,
        "message": answer,
    }
