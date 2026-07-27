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
from app.twilio_whatsapp import send_twilio_message
from app.whatsapp import send_whatsapp_message

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
    """Handle webhook verification requests from Twilio or Meta."""
    verify_token = os.getenv("META_VERIFY_TOKEN") or os.getenv("TWILIO_VERIFY_TOKEN", "school-chatbot")
    if mode == "subscribe" and challenge is not None:
        return {"challenge": challenge}
    if mode == "subscribe" and challenge is None:
        return {"status": "ok"}
    if mode is None:
        return {"status": "ok"}
    if verify_token and mode == verify_token:
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="Invalid webhook verification")


def _extract_incoming_message(payload: Any) -> tuple[str | None, str | None]:
    """Extract a sender number and message text from either simple or Meta payloads."""
    if not isinstance(payload, dict):
        return None, None

    if "entry" in payload:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    continue

                message = messages[0]
                from_number = message.get("from")
                message_type = message.get("type", "")
                if message_type == "text":
                    message_text = message.get("text", {}).get("body", "")
                else:
                    message_text = ""
                return from_number, message_text

    from_number = payload.get("from_number")
    message_text = payload.get("message_text")
    if from_number is None or message_text is None:
        return None, None
    return from_number, message_text


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request) -> dict[str, str]:
    """Process incoming WhatsApp text messages and return a reply."""
    payload = await request.json()
    from_number, message_text = _extract_incoming_message(payload)
    if not from_number or not message_text or not str(message_text).strip():
        LOGGER.warning("Received empty WhatsApp message")
        raise HTTPException(status_code=400, detail="Message text is required")

    LOGGER.info("Incoming WhatsApp message from %s", from_number)
    answer = answer_question(str(message_text), DOCUMENTS)

    try:
        if os.getenv("META_ACCESS_TOKEN") and os.getenv("META_PHONE_NUMBER_ID"):
            send_whatsapp_message(from_number, answer)
        else:
            send_twilio_message(from_number, answer)
    except Exception as error:  # pragma: no cover - defensive logging
        LOGGER.exception("Failed to send WhatsApp reply: %s", error)

    return {
        "to": from_number,
        "message": answer,
    }
