"""SDK constructor test only; no inference or cloud availability claim."""

import asyncio
import pytest


def test_foundry_sdk_construction_and_cleanup(monkeypatch):
    pytest.importorskip("agent_framework_foundry")
    from trajectan.agents import Foundry

    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/example",
    )
    monkeypatch.setenv("FOUNDRY_MODEL", "example")
    provider = Foundry()
    assert set(provider.agents) == {
        "Investigation",
        "Evidence & Reasoning",
        "Narrative",
    }
    assert provider.enabled
    asyncio.run(provider.close())


def test_actual_agent_framework_request_pipeline_with_stubbed_http(
    monkeypatch, tmp_path
):
    """Real Agent.run/Foundry SDK serialization; stubbed HTTP is NOT live inference."""
    pytest.importorskip("agent_framework_foundry")
    import json
    import httpx
    from openai import AsyncOpenAI
    from trajectan.agents import Foundry, Workflow
    from trajectan.domain import initial
    from trajectan.simulation import generate
    from trajectan.persistence import Store

    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/agentgate",
    )
    monkeypatch.setenv("FOUNDRY_MODEL", "gpt-4.1-mini")
    calls = []

    def transport(request):
        body = json.loads(request.content)
        title = body["text"]["format"]["schema"]["title"]
        calls.append(title)
        assert body["model"] == "gpt-4.1-mini"
        assert body["max_output_tokens"] == 1200
        if title == "Plan":
            answer = {
                "decision": "investigate",
                "tools": ["get_forecast", "get_event_window"],
                "reason": "Stubbed test plan",
                "scenarios": [],
            }
        elif title == "Review":
            answer = {"verdict": "supported", "reason": "Stubbed test review"}
        else:
            user = next(x for x in reversed(body["input"]) if x["role"] == "user")
            answer = json.loads(user["content"][0]["text"])["input"]
        return httpx.Response(
            200,
            json={
                "id": f"resp_stub_{len(calls)}",
                "object": "response",
                "created_at": 1,
                "status": "completed",
                "model": "gpt-4.1-mini",
                "output": [
                    {
                        "id": f"msg_{len(calls)}",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(answer),
                                "annotations": [],
                            }
                        ],
                    }
                ],
                "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
            },
        )

    async def run():
        events, states = generate(initial())
        store = Store("sqlite:///" + str(tmp_path / "sdk.db"))

        class Offline:
            enabled = False

        baseline = await Workflow(store, Offline()).run(states, events, 300)
        provider = Foundry()
        await provider.client.client.close()
        provider.client.client = AsyncOpenAI(
            api_key="unit-test-not-a-secret",
            base_url="https://unit.test/v1",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(transport)),
        )
        try:
            workflow = Workflow(store, provider)
            result = await workflow.run(states, events, 300)
            assert result["status"] == "published", result["trace"]
            assert calls == ["Plan", "Review", "Draft"]
            assert result["investigation_id"] != baseline["investigation_id"]
            assert provider.successful_calls == 3
            receipts = [x["inference"] for x in result["trace"] if "inference" in x]
            assert len(receipts) == 3 and all(
                x["response_id"].startswith("resp_stub_") for x in receipts
            )
            assert await workflow.run(states, events, 300) == result
            assert len(calls) == 3
        finally:
            await provider.close()

    asyncio.run(run())


def test_network_key_alias_and_sdk_auth_selection(monkeypatch):
    """Constructor compatibility only; no claim about proxy injection or Azure auth."""
    pytest.importorskip("agent_framework_foundry")
    from trajectan.agents import Foundry

    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/agentgate",
    )
    monkeypatch.delenv("FOUNDRY_MODEL", raising=False)
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4.1-mini")
    monkeypatch.setenv("TRAJECTAN_FOUNDRY_KEY", "unit-test-proxy-placeholder")
    provider = Foundry()
    assert provider.enabled and provider.auth_mode == "network-key"
    assert provider.model == "gpt-4.1-mini"
    assert provider.client.client.api_key == "unit-test-proxy-placeholder"
    assert "TRAJECTAN_FOUNDRY_KEY" not in provider.cache_identity
    # OpenAI SDK sends this override as Authorization: Bearer. The new runtime's
    # binding must permit that header, or provide an explicit compatible binding.
    assert provider.client.client.auth_headers == {
        "Authorization": "Bearer unit-test-proxy-placeholder"
    }
