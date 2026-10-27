"""Opt-in real Foundry/Agent Framework smoke test. Uses server-side identity only.
Runs three real role inferences; consumes existing model quota, creates no resources.
"""

import asyncio
import json
import os
from trajectan.agents import Foundry, Plan, Review
from trajectan.analytics import forecast
from trajectan.domain import Draft, Claim, initial
from trajectan.simulation import generate
from trajectan.validation import facts, validate


async def main():
    if not os.getenv("FOUNDRY_PROJECT_ENDPOINT"):
        raise SystemExit(
            "Set the exact agentgate project endpoint through server-side environment configuration. No secrets should be entered in chat."
        )
    os.environ.setdefault("FOUNDRY_MODEL", "gpt-4.1-mini")
    provider = Foundry()
    try:
        events, states = generate(initial(26))
        state = states[300]
        prediction = forecast(state, 32)
        draft = Draft(
            claims=[
                Claim(metric=k, value=v, source_sequence=300)
                for k, v in facts(state, prediction).items()
            ]
        )
        plan = await provider.ask(
            "Investigation",
            dict(
                state_sequence=300,
                facts=facts(state, prediction),
                instruction="Choose a short useful investigation plan for this synthetic checkpoint.",
            ),
            Plan,
        )
        review = await provider.ask(
            "Evidence & Reasoning",
            dict(
                source_sequence=300,
                verified_facts=facts(state, prediction),
                claims=draft.model_dump(),
            ),
            Review,
        )
        narrative = await provider.ask("Narrative", draft.model_dump(), Draft)
        report = validate(narrative, state, prediction, events[:300])
        result = {
            "execution": "real-foundry-agent-framework",
            "project": "agentgate",
            "deployment": os.environ["FOUNDRY_MODEL"],
            "roles_exercised": ["Investigation", "Evidence & Reasoning", "Narrative"],
            "plan_decision": plan.decision,
            "review_verdict": review.verdict,
            "deterministic_validation": report,
        }
        print(json.dumps(result, indent=2))
        if not report["valid"]:
            raise SystemExit(
                "Real inference completed, but narrative validation failed. Do not claim successful publication."
            )
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
