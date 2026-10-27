"""Comparable held-out evidence cases for template, single-LLM and three-role modes.
Only template mode works without real Foundry access. Never substitutes fake inference.
"""

import argparse
import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from trajectan.agents import Foundry, Workflow
from trajectan.analytics import forecast
from trajectan.domain import initial, Draft, Claim
from trajectan.persistence import Store
from trajectan.simulation import generate, state_hash
from trajectan.validation import facts, validate


class Template:
    enabled = False


async def run(mode, count, output):
    provider = None
    if mode != "template":
        if not os.getenv("FOUNDRY_PROJECT_ENDPOINT"):
            raise SystemExit(
                "Real Foundry endpoint and server identity required; no fallback is permitted for model benchmark modes."
            )
        os.environ.setdefault("FOUNDRY_MODEL", "gpt-4.1-mini")
        provider = Foundry()
    rows = []
    try:
        with tempfile.TemporaryDirectory(prefix="trajectan-benchmark-") as directory:
            store = Store("sqlite:///" + str(Path(directory) / "cases.db"))
            for seed in range(501, 501 + count):
                events, states = generate(initial(seed))
                state = states[min(300, len(states) - 1)]
                started = time.monotonic()
                before = provider.successful_calls if provider else 0
                if mode == "single":
                    prediction = forecast(state)
                    baseline = Draft(
                        claims=[
                            Claim(metric=k, value=v, source_sequence=state.sequence)
                            for k, v in facts(state, prediction).items()
                        ]
                    )
                    try:
                        draft = await provider.ask(
                            "Narrative", baseline.model_dump(), Draft
                        )
                        report = validate(
                            draft,
                            state,
                            prediction,
                            events[: state.sequence],
                            require_complete=True,
                        )
                        result = {
                            "status": "published" if report["valid"] else "rejected",
                            "validation": report,
                            "tool_count": 1,
                        }
                    except Exception as error:
                        result = {
                            "status": "failed",
                            "validation": None,
                            "tool_count": 1,
                            "error_type": type(error).__name__,
                        }
                else:
                    result = await Workflow(store, provider or Template()).run(
                        states, events, state.sequence
                    )
                rows.append(
                    dict(
                        seed=seed,
                        state_sequence=state.sequence,
                        state_hash=state_hash(state),
                        mode=mode,
                        status=result["status"],
                        published_verified=bool(
                            result.get("validation", {})
                            and result["validation"]["valid"]
                            and result["status"] == "published"
                        ),
                        tool_count=result["tool_count"],
                        inference_calls=(provider.successful_calls - before)
                        if provider
                        else 0,
                        seconds=round(time.monotonic() - started, 3),
                    )
                )
            store.engine.dispose()
        report = {
            "model_version": "tactical-1.0",
            "mode": mode,
            "case_count": count,
            "checkpoint": "event 300 (or final event if shorter)",
            "forecast_samples": 128,
            "forecast_seed": 710,
            "verified_publication_rate": sum(r["published_verified"] for r in rows)
            / count,
            "mean_seconds": sum(r["seconds"] for r in rows) / count,
            "limitations": "Small synthetic suite. Measures validator acceptance and operational latency, not subjective narrative relevance, causal validity or real-football predictive accuracy. Different modes must use identical seeds/state hashes before comparing. Token costs are not estimated.",
            "rows": rows,
        }
        Path(output).write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
    finally:
        if provider:
            await provider.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--mode", choices=["template", "single", "multi"], default="template"
    )
    p.add_argument("--cases", type=int, default=3)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    if not 1 <= a.cases <= 20:
        p.error("--cases must be between 1 and 20")
    asyncio.run(run(a.mode, a.cases, a.output))
