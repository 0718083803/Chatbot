from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_slack_events_returns_reply() -> None:
    response = client.post(
        "/slack/events",
        json={
            "type": "event_callback",
            "event": {
                "type": "message",
                "channel": "C123456",
                "user": "U123456",
                "text": "What time does the school office open?",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["channel"] == "C123456"
    expected = "The school office is open from 8:00 AM to 3:00 PM."
    assert payload["message"] == expected


def test_slack_events_url_verification() -> None:
    response = client.post(
        "/slack/events",
        json={"type": "url_verification", "challenge": "test_chal"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["challenge"] == "test_chal"
