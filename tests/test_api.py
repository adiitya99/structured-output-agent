
import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from structured_agent.api import app
from structured_agent.api import limiter

client = TestClient(app)

def test_response_includes_request_id():
    response = client.get("/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert str(UUID(request_id)) == request_id


def test_valid_client_request_id_is_reused():
    request_id = "12345678-1234-5678-1234-567812345678"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_client_request_id_is_replaced():
    response = client.get(
        "/health",
        headers={"X-Request-ID": "not-a-valid-uuid"},
    )

    returned_id = response.headers["X-Request-ID"]

    assert str(UUID(returned_id)) == returned_id
    assert returned_id != "not-a-valid-uuid"


@pytest.fixture(autouse=True)
def configure_test_api_key(monkeypatch):
    monkeypatch.setenv("AGENT_API_KEY", "test-secret-key")


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_returns_valid_output():
    response = client.post(
        "/tasks",
        json={"prompt": "Help me study computer networks"},
        headers={"X-API-Key": "test-secret-key"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["summary"] == "Initial simulated response"
    assert data["category"] == "study"
    assert data["confidence"] == 0.9
    assert data["next_steps"] == ["Review the task"]


def test_empty_prompt_is_rejected():
    response = client.post(
        "/tasks",
        json={"prompt": ""},
        headers={"X-API-Key": "test-secret-key"},
    )

    assert response.status_code == 422


def test_extra_request_field_is_rejected():
    response = client.post(
        "/tasks",
        json={
            "prompt": "Study networking",
            "admin": True,
        },
        headers={"X-API-Key": "test-secret-key"},
    )

    assert response.status_code == 422


def test_tasks_reject_missing_api_key():
    response = client.post(
        "/tasks",
        json={"prompt": "Study networking"},
    )

    assert response.status_code == 401


def test_tasks_reject_wrong_api_key():
    response = client.post(
        "/tasks",
        json={"prompt": "Study networking"},
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_task_rate_limit_returns_429():
    limiter.reset()

    try:
        responses = [
            client.post(
                "/tasks",
                json={"prompt": "Study networking"},
                headers={"X-API-Key": "test-secret-key"},
            )
            for _ in range(11)
        ]

        assert any(response.status_code == 429 for response in responses)
    finally:
        limiter.reset()
def test_tasks_reject_when_server_key_is_unconfigured(monkeypatch):
    monkeypatch.delenv("AGENT_API_KEY", raising=False)

    response = client.post(
        "/tasks",
        json={"prompt": "Study networking"},
        headers={"X-API-Key": "test-secret-key"},
    )

    assert response.status_code == 503
