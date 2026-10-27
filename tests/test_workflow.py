import asyncio
import pytest
from trajectan.agents import Workflow, Plan, Review
from trajectan.domain import initial, Draft, Claim
from trajectan.simulation import generate
from trajectan.persistence import Store


class Offline:
    enabled = False


class Fault:
    enabled = True

    async def ask(self, *args):
        raise TimeoutError("Unavailable")


class Reject:
    enabled = True

    async def ask(self, role, payload, schema):
        if schema is Plan:
            return Plan(tools=["get_forecast"], reason="Test fixture plan")
        if schema is Review:
            return Review(verdict="supported", reason="Test review")
        return Draft(
            claims=[Claim(metric="home_score", value=999, source_sequence=300)]
        )


class Loop:
    enabled = True

    async def ask(self, role, payload, schema):
        if schema is Plan:
            return Plan(tools=["get_event_window"], reason="Test plan")
        return Review(verdict="needs_more_evidence", reason="Insufficient evidence")


@pytest.fixture(scope="module")
def fixture():
    return generate(initial())


@pytest.mark.parametrize(
    "provider,expected",
    [
        (Offline(), "published"),
        (Fault(), "failed"),
        (Reject(), "rejected"),
        (Loop(), "inconclusive"),
    ],
)
def test_workflow_status_and_budget(tmp_path, fixture, provider, expected):
    events, states = fixture
    store = Store("sqlite:///" + str(tmp_path / "test.db"))
    w = Workflow(store, provider)
    result = asyncio.run(w.run(states, events, 300))
    assert result["status"] == expected
    assert result["tool_count"] <= 8
    assert len([x for x in result["trace"] if x["operation"] == "planning_round"]) <= 3
    assert all(x["source_sequence"] == 300 for x in result["trace"])
    if expected != "published":
        assert not result["narratives"]
    assert asyncio.run(w.run(states, events, 300)) == result
    assert len(store.list("investigation", states[0].match_id)) == 1
    assert not store.list("investigation", states[0].match_id, 299)


def test_memory_links_keep_original(tmp_path, fixture):
    events, states = fixture
    w = Workflow(Store("sqlite:///" + str(tmp_path / "test.db")), Offline())
    first = asyncio.run(w.run(states, events, 300))
    second = asyncio.run(w.run(states, events, 320))
    assert second["relations"][0]["target"] == first["investigation_id"]
    assert w.store.get(first["investigation_id"]) == first


def test_invalid_foundry_configuration_preserves_local_workflow(tmp_path, monkeypatch):
    import trajectan.agents as agents

    def unavailable():
        raise ImportError("Optional connector unavailable")

    monkeypatch.setattr(agents, "Foundry", unavailable)
    workflow = Workflow(Store("sqlite:///" + str(tmp_path / "test.db")))
    assert not workflow.provider.enabled
    assert "configuration unavailable" in workflow.provider.configuration_error
