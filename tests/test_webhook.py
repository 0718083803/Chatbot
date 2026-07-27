from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_whatsapp_webhook_returns_reply() -> None:
    response = client.post(
        "/whatsapp/webhook",
        json={
            "from_number": "+123456789",
            "message_text": "What time does the school office open?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["to"] == "+123456789"
    expected = "The school office is open from 8:00 AM to 3:00 PM."
    assert payload["message"] == expected


def test_whatsapp_webhook_handles_meta_payload() -> None:
    response = client.post(
        "/whatsapp/webhook",
        json={
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "2248689585968047",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551510041",
                                    "phone_number_id": "1165060260030303",
                                },
                                "messages": [
                                    {
                                        "from": "263718756962",
                                        "type": "text",
                                        "text": {"body": "Hi"},
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["to"] == "263718756962"
    assert payload["message"] == "Hello! How can I help you today?"
