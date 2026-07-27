"""Pydantic schemas for WhatsApp webhook payloads."""

from pydantic import BaseModel


class WhatsAppMessage(BaseModel):
    """Incoming WhatsApp message payload."""

    from_number: str
    message_text: str
