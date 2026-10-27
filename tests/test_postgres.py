"""Optional real local PostgreSQL checks. Not evidence of Azure connectivity."""

import asyncio
import os
import uuid
import pytest
from trajectan.persistence import Store
from trajectan.jobs import Jobs


@pytest.mark.skipif(
    not os.getenv("TEST_POSTGRES_URL"),
    reason="Provide an isolated test PostgreSQL database",
)
def test_postgres_artifacts_and_worker():
    store = Store(os.environ["TEST_POSTGRES_URL"])
    marker = "postgres-test-" + uuid.uuid4().hex
    payload = {"coordinates": [[1, 2], [3, 4]], "synthetic": True}
    assert store.put(marker, "events", marker, 0, payload) == payload
    assert store.put(marker, "events", marker, 0, payload) == payload
    with pytest.raises(ValueError):
        store.put(marker, "events", marker, 0, {"different": True})

    async def run():
        async def handler(request):
            return {"verified": request["seed"] == 26}

        jobs = Jobs(store, handler)
        jobs.submit(marker, {"seed": 26})
        jobs.start()
        try:
            for _ in range(100):
                result = jobs.get(marker)
                if result["status"] == "completed":
                    break
                await asyncio.sleep(0.05)
            assert result["status"] == "completed" and result["result"] == {
                "verified": True
            }
            assert jobs.claim(marker) is None
        finally:
            await jobs.close()

    asyncio.run(run())
    store.engine.dispose()
