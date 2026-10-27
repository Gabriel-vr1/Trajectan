import asyncio
from trajectan.jobs import Jobs
from trajectan.persistence import Store


def test_durable_recovery_dedup_and_claim(tmp_path):
    store = Store("sqlite:///" + str(tmp_path / "jobs.db"))

    async def handler(request):
        return {"value": request["value"] * 2}

    first = Jobs(store, handler)
    first.submit("a", {"value": 3})
    first.submit("a", {"value": 99})
    resumed = Jobs(Store(store.url), handler)
    assert resumed.pending() == ["a"]
    assert resumed.claim("a") == {"value": 3}
    assert first.claim("a") is None
    resumed.finish("a", result={"value": 6})
    assert first.get("a")["result"] == {"value": 6}
    assert not resumed.pending()


def test_worker_failure_and_success(tmp_path):
    async def run():
        async def handler(request):
            if request["bad"]:
                raise ValueError("Invalid request")
            return {"ok": True}

        jobs = Jobs(Store("sqlite:///" + str(tmp_path / "jobs.db")), handler)
        jobs.submit("ok", {"bad": False})
        jobs.submit("bad", {"bad": True})
        jobs.start()
        for _ in range(50):
            if (
                jobs.get("bad")["status"] == "failed"
                and jobs.get("ok")["status"] == "completed"
            ):
                break
            await asyncio.sleep(0.05)
        await jobs.close()
        assert jobs.get("bad")["error"] == "Invalid request"
        assert jobs.get("ok")["result"] == {"ok": True}

    asyncio.run(run())


def test_immutable_event_record_conflict(tmp_path):
    import pytest

    store = Store("sqlite:///" + str(tmp_path / "immutable.db"))
    store.put("events:a", "events", "a", 0, [{"sequence": 1}])
    with pytest.raises(ValueError, match="Immutable record differs"):
        store.put("events:a", "events", "a", 0, [{"sequence": 2}])
    assert store.get("events:a") == [{"sequence": 1}]
