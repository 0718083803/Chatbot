"""FastAPI entrypoint for the school WhatsApp chatbot backend."""

import os
import json
import time
import hmac
import hashlib
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

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


def _verify_slack_signature(request: Request, body: bytes) -> None:
    """Verify Slack request signature to ensure request is from Slack.

    Raises HTTPException(401) on signature mismatch or 400 on malformed request.
    """
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if not signing_secret:
        LOGGER.warning("SLACK_SIGNING_SECRET not set; skipping Slack signature verification")
        return

    timestamp = request.headers.get("x-slack-request-timestamp")
    signature = request.headers.get("x-slack-signature")
    if not timestamp or not signature:
        LOGGER.warning("Missing Slack signature headers")
        raise HTTPException(status_code=400, detail="Missing Slack signature headers")

    try:
        req_ts = int(timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp")

    # Protect against replay attacks (allow 5 minutes)
    if abs(time.time() - req_ts) > 60 * 5:
        LOGGER.warning("Slack request timestamp outside allowed range")
        raise HTTPException(status_code=400, detail="Stale request")

    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = "v0=" + hmac.new(signing_secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, signature):
        LOGGER.warning("Slack signature verification failed")
        raise HTTPException(status_code=401, detail="Invalid Slack signature")


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
    """Handle Slack Events API requests and reply with answers from docs.

    Verifies request signatures using `SLACK_SIGNING_SECRET` if present.
    """
    body_bytes = await request.body()
    _verify_slack_signature(request, body_bytes)

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

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


@app.post("/slack/commands")
async def slack_commands(request: Request) -> dict[str, str]:
    """Handle Slack Slash Commands (application/x-www-form-urlencoded).

    Verifies request signatures and supports simple `/bot-ping` and
    forwarding text to the knowledge base for other commands.
    """
    body_bytes = await request.body()
    _verify_slack_signature(request, body_bytes)

    try:
        parsed = parse_qs(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid form payload")

    command = parsed.get("command", [None])[0]
    text = parsed.get("text", [""])[0]

    if command == "/bot-ping":
        return {"response_type": "ephemeral", "text": "Pong!"}

    # Fallback: treat the command text as a question for the knowledge base
    answer = answer_question(text or "", DOCUMENTS)
    return {"response_type": "in_channel", "text": answer}
