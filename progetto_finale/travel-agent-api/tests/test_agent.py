import os
from travel_agent_api.services.agent_service import Agent


def test_agent_normalization():
    agent = Agent()
    # Test formato Laravel Livewire
    laravel_msgs = [{"type": "human", "content": "Voli per Parigi"}]
    normalized = agent._normalize_messages(laravel_msgs)
    assert len(normalized) == 1
    assert normalized[0]["role"] == "user"
    assert normalized[0]["content"] == "Voli per Parigi"

    # Test formato standard Swagger
    swagger_msgs = [{"role": "user", "content": "Hotel a Milano"}]
    normalized2 = agent._normalize_messages(swagger_msgs)
    assert len(normalized2) == 1
    assert normalized2[0]["role"] == "user"


def test_agent_run_mock_flight():
    os.environ["API_MODE"] = "test"
    agent = Agent()
    messages = [{"type": "human", "content": "Cerco voli da FCO a CDG"}]
    res = agent.run(messages)
    assert isinstance(res, list)
    assert len(res) >= 2
    last_msg = res[-1]
    assert last_msg["type"] == "ai"
    assert "Miglior Opzione" in last_msg["content"] or "Voli" in last_msg["content"]
