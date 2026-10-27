"""Opt-in real three-role Foundry/controller integration; provisions no resources.
Requires server-side identity and the exact existing Foundry project endpoint.
"""

import argparse
import asyncio
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from trajectan.agents import Foundry, Workflow
from trajectan.domain import initial
from trajectan.persistence import Store
from trajectan.simulation import generate


async def main(output):
    if not os.getenv("FOUNDRY_PROJECT_ENDPOINT"):
        report = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "status": "configuration_blocked",
            "live_inference_observed": False,
            "complete_workflow_verified": False,
            "roles_exercised": [],
            "failure": {"stage": "preflight", "code": "missing_project_endpoint"},
            "configuration_present": {
                name: bool(os.getenv(name))
                for name in (
                    "FOUNDRY_PROJECT_ENDPOINT",
                    "FOUNDRY_MODEL_DEPLOYMENT",
                    "TRAJECTAN_FOUNDRY_KEY",
                )
            },
        }
        if output:
            Path(output).write_text(json.dumps(report, indent=2) + "\n")
        raise SystemExit(
            "Missing FOUNDRY_PROJECT_ENDPOINT for agentgate. Configure server-side identity and network access; do not share keys or tokens in chat."
        )
    os.environ.setdefault(
        "FOUNDRY_MODEL", os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4.1-mini")
    )
    provider = Foundry()
    try:
        events, states = generate(initial(26))
        checkpoint = next(e.sequence for e in reversed(events) if e.outcome == "goal")
        with tempfile.TemporaryDirectory(prefix="trajectan-foundry-") as directory:
            store = Store("sqlite:///" + str(Path(directory) / "verification.db"))
            result = await Workflow(store, provider).run(states, events, checkpoint)
            store.engine.dispose()
        roles = sorted(
            {t["inference"]["role"] for t in result["trace"] if t.get("inference")}
        )
        complete = (
            result["status"] == "published"
            and result["validation"]["valid"]
            and set(roles) == {"Investigation", "Evidence & Reasoning", "Narrative"}
        )
        report = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "live_inference_observed": bool(roles),
            "complete_workflow_verified": complete,
            "deployment": os.environ["FOUNDRY_MODEL"],
            "roles_exercised": roles,
            "result": result,
        }
        if output:
            Path(output).write_text(json.dumps(report, indent=2) + "\n")
        print(
            json.dumps(
                {k: v for k, v in report.items() if k != "result"}
                | {"status": result["status"], "report": output},
                indent=2,
            )
        )
        if not complete:
            raise SystemExit(
                "The complete three-role workflow was not verified. Inspect the recorded terminal state and trace; no success claim is justified."
            )
    finally:
        await provider.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Optional local JSON evidence path; contains no credentials.",
    )
    asyncio.run(main(parser.parse_args().output))
