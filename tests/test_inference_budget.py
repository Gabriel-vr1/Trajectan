"""A public deployment's inference allowance survives concurrency and restarts."""

from concurrent.futures import ThreadPoolExecutor
import pytest
from trajectan.persistence import Store


def test_allowance_is_atomic_persistent_and_not_replenished(tmp_path):
    store = Store("sqlite:///" + str(tmp_path / "budget.db"))

    def reserve(_):
        try:
            store.reserve_inference(5)
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, range(16))) == 5
    store.engine.dispose()
    restarted = Store(store.url)
    with pytest.raises(ValueError, match="allowance is exhausted"):
        restarted.reserve_inference(5)
    restarted.engine.dispose()
