import os
from fastapi.testclient import TestClient
from travel_agent_api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "Travel Agent API"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "config" in data


def test_chat_travel_agent_endpoint_laravel_format():
    os.environ["API_MODE"] = "test"
    payload = {
        "messages": [
            {
                "type": "human",
                "content": "Vorrei consigli su cosa vedere a Firenze"
            }
        ]
    }
    response = client.post("/chat/travel-agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert data[-1]["type"] == "ai"
    assert len(data[-1]["content"]) > 0


def test_chat_travel_agent_endpoint_swagger_format():
    os.environ["API_MODE"] = "test"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Cerco hotel a Roma"
            }
        ]
    }
    response = client.post("/chat/travel-agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[-1]["type"] == "ai"
