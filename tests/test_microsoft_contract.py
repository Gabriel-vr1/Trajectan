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
