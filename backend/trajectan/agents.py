"""Three specialized model roles, bounded by a deterministic controller.
Without Foundry credentials this runs a transparent rule-based development baseline.
"""

import asyncio
import hashlib
from contextvars import ContextVar
import json
import os
import time
from datetime import datetime, timezone
from typing import Literal
from pydantic import Field, ValidationError
from .domain import Strict, Draft, Claim, ScenarioRequest
from .analytics import forecast, attribution, scenario
from .simulation import state_hash
from .memory import hypotheses, relate
from .validation import validate, facts, render


class Plan(Strict):
    decision: Literal["investigate", "defer", "reject"] = "investigate"
    tools: list[
        Literal[
            "get_event_window",
            "analyze_possessions",
            "get_forecast",
            "explain_forecast_change",
            "get_prior_investigations",
            "compare_match_periods",
            "simulate_scenario",
        ]
    ] = Field(max_length=8)
    reason: str = Field(max_length=300)
    scenarios: list[ScenarioRequest] = Field(default_factory=list, max_length=2)


class Review(Strict):
    verdict: Literal["supported", "needs_more_evidence", "inconclusive", "rejected"]
    reason: str = Field(max_length=300)


class Foundry:
    execution_mode = "foundry-agent-framework"

    def __init__(self):
        self.model = (
            os.getenv("FOUNDRY_MODEL")
            or os.getenv("FOUNDRY_MODEL_DEPLOYMENT")
            or "gpt-4.1-mini"
        )
        self.enabled = bool(os.getenv("FOUNDRY_PROJECT_ENDPOINT"))
        self.auth_mode = (
            "network-key" if os.getenv("TRAJECTAN_FOUNDRY_KEY") else "entra"
        )
        self.agents = {}
        self.successful_calls = 0
        self.receipts = []
        self.last_receipt = ContextVar("inference_receipt", default=None)
        self.cache_identity = hashlib.sha256(
            json.dumps(
                {
                    "endpoint": os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
                    "model": self.model,
                    "auth_mode": self.auth_mode,
                    "sdk": "1.23.0/1.15.0",
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16]
        if self.enabled:
            from agent_framework import Agent
            from agent_framework.foundry import FoundryChatClient
            from azure.identity.aio import DefaultAzureCredential

            self.credential = DefaultAzureCredential()
            project = None
            if self.auth_mode == "network-key":
                from azure.ai.projects.aio import AIProjectClient

                class NetworkKeyProjectClient(AIProjectClient):
                    def get_openai_client(self, **kwargs):
                        # SDK-supported override. The network-bound variable may be
                        # a proxy placeholder; pass it unchanged and never log it.
                        kwargs["api_key"] = os.environ["TRAJECTAN_FOUNDRY_KEY"]
                        return super().get_openai_client(**kwargs)

                project = NetworkKeyProjectClient(
                    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                    credential=self.credential,
                )
            client = FoundryChatClient(
                project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                project_client=project,
                model=self.model,
                credential=self.credential,
            )
            self.client = client
            for role, instructions in {
                "Investigation": "Select useful allowlisted tools to investigate this pinned synthetic match. Defer if evidence is routine. Return JSON matching the provided schema. Do not invent facts.",
                "Evidence & Reasoning": "Independently review the provided tool evidence. Request more evidence if needed; reject unsupported claims. Return JSON matching the provided schema.",
                "Narrative": "Select a narrative angle and copy exact structured claims from verified facts. Return JSON matching the schema. No new numbers or free-form prose.",
            }.items():
                self.agents[role] = Agent(
                    client=client,
                    name=role.replace(" & ", "_"),
                    instructions=instructions,
                    default_options={"max_output_tokens": 1200},
                )

    async def close(self):
        if self.enabled:
            await self.client.client.close()
            await self.client.project_client.close()
            await self.credential.close()

    async def ask(self, role, payload, schema):
        started = time.monotonic()
        self.last_receipt.set(None)
        response = await asyncio.wait_for(
            self.agents[role].run(
                json.dumps(dict(input=payload, schema=schema.model_json_schema())),
                options={"response_format": schema},
            ),
            timeout=30,
        )
        receipt = dict(
            role=role,
            response_id=response.response_id,
            duration_ms=round((time.monotonic() - started) * 1000, 2),
            deployment=self.model,
            auth_mode=self.auth_mode,
            sdk="agent-framework-core/1.23.0",
            at=datetime.now(timezone.utc).isoformat(),
        )
        self.last_receipt.set(receipt)
        self.receipts.append(receipt)
        self.receipts = self.receipts[-100:]
        self.successful_calls += 1
        return schema.model_validate_json(response.text)


class UnavailableProvider:
    enabled = False

    def __init__(self, reason):
        self.configuration_error = reason

    async def close(self):
        pass


class Workflow:
    def __init__(self, store, provider=None):
        self.store = store
        if provider is not None:
            self.provider = provider
        else:
            try:
                self.provider = Foundry()
            except (ImportError, ValueError) as error:
                self.provider = UnavailableProvider(
                    type(error).__name__ + ": Foundry configuration unavailable"
                )

    @property
    def execution_mode(self):
        return (
            getattr(self.provider, "execution_mode", "model-provider-test-double")
            if self.provider.enabled
            else "deterministic-development-fallback"
        )

    def execution_key(self, state, revision=0):
        identity = getattr(self.provider, "cache_identity", self.execution_mode)
        return f"investigation:v2:{state.match_id}:{state.sequence}:{state_hash(state)[:12]}:{self.execution_mode}:{identity}:r{revision}"

    async def run(self, states, events, seq, revision=0):
        state = states[seq]
        key = self.execution_key(state, revision)
        existing = self.store.get(key)
        if existing:
            return existing
        trace = []
        tools = {}
        calls = 0
        mode = self.execution_mode

        def record(stage, operation, detail="", elapsed=0):
            trace.append(
                dict(
                    stage=stage,
                    operation=operation,
                    detail=detail,
                    duration_ms=round(elapsed * 1000, 2),
                    at=datetime.now(timezone.utc).isoformat(),
                    source_sequence=seq,
                )
            )

        async def invoke(role, payload, schema):
            for attempt in range(2):
                started = time.monotonic()
                try:
                    answer = await self.provider.ask(role, payload, schema)
                    record(
                        "agent_execution",
                        role,
                        f"Structured response; attempt {attempt + 1}",
                        time.monotonic() - started,
                    )
                    receipt = getattr(self.provider, "last_receipt", None)
                    if receipt is not None and receipt.get() is not None:
                        trace[-1]["inference"] = dict(receipt.get())
                    return answer
                except (TimeoutError, ValidationError) as error:
                    record(
                        "agent_execution",
                        role,
                        f"{type(error).__name__}; attempt {attempt + 1}",
                        time.monotonic() - started,
                    )
                    if attempt:
                        raise

        record("queued", "pin_state", f"State {seq}; execution: {mode}")
        window = events[max(0, seq - 25) : seq]
        significant = any(e.kind == "shot" or e.outcome == "red" for e in window)
        status = "investigating"
        draft = None
        validation = None
        review = None
        try:
            for round_index in range(3):
                record("investigating", "planning_round", str(round_index + 1))
                if self.provider.enabled:
                    plan = await invoke(
                        "Investigation",
                        dict(
                            state=state.model_dump(),
                            recent=[e.model_dump() for e in window],
                            observations=tools,
                        ),
                        Plan,
                    )
                    record("investigating", "Investigation", plan.reason)
                else:
                    plan = Plan(
                        tools=[
                            "get_event_window",
                            "analyze_possessions",
                            "get_forecast",
                            "get_prior_investigations",
                        ]
                        + (
                            ["explain_forecast_change"]
                            if significant and seq > 1
                            else []
                        ),
                        reason="Rule-based selection: chance/discipline evidence"
                        if significant
                        else "Rule-based checkpoint summary",
                    )
                    record("investigating", "fallback_plan", plan.reason)
                if plan.decision != "investigate":
                    status = "inconclusive" if plan.decision == "defer" else "rejected"
                    break
                for tool in plan.tools:
                    if tool in tools:
                        continue
                    if calls >= 8:
                        raise ValueError("Analytical tool budget exhausted")
                    calls += 1
                    began = time.monotonic()
                    if tool == "get_event_window":
                        result = [e.model_dump() for e in window]
                    elif tool == "analyze_possessions":
                        result = dict(
                            shots=state.shots,
                            xg=state.xg,
                            passes=state.passes,
                            completed=state.completed,
                            possession_seconds=state.possession_seconds,
                            evidence=[e.event_id for e in window],
                        )
                    elif tool == "get_forecast":
                        result = await asyncio.to_thread(forecast, state)
                    elif tool == "explain_forecast_change":
                        result = await asyncio.to_thread(
                            attribution, states[max(0, seq - 20)], state, 64
                        )
                    elif tool == "compare_match_periods":
                        earlier = events[max(0, seq - 50) : max(0, seq - 25)]
                        result = dict(
                            previous_window=[e.event_id for e in earlier],
                            current_window=[e.event_id for e in window],
                            previous_shots=sum(e.kind == "shot" for e in earlier),
                            current_shots=sum(e.kind == "shot" for e in window),
                        )
                    elif tool == "simulate_scenario":
                        result = []
                        for request in plan.scenarios:
                            if request.sequence != seq:
                                raise ValueError("Scenario must use pinned checkpoint")
                            if request.samples > 128:
                                raise ValueError(
                                    "Autonomous scenario sample budget exceeded"
                                )
                            result.append(
                                await asyncio.to_thread(scenario, state, request)
                            )
                    else:
                        result = [
                            dict(
                                investigation_id=i["investigation_id"],
                                source_sequence=i["source_sequence"],
                                status=i["status"],
                                hypothesis=i.get("hypothesis"),
                                evidence_ids=i["evidence_ids"],
                            )
                            for i in self.store.list(
                                "investigation", state.match_id, seq - 1
                            )[-3:]
                        ]
                    tools[tool] = result
                    record("investigating", tool, "completed", time.monotonic() - began)
                record(
                    "evidence_review",
                    "handoff",
                    "Independent evidence review"
                    if self.provider.enabled
                    else "Deterministic completeness review",
                )
                if self.provider.enabled:
                    review = await invoke(
                        "Evidence & Reasoning",
                        dict(observations=tools, source_sequence=seq),
                        Review,
                    )
                else:
                    review = Review(
                        verdict="supported"
                        if "get_forecast" in tools
                        else "needs_more_evidence",
                        reason="Pinned numerical outputs are available",
                    )
                record(
                    "evidence_review", "review", review.verdict + ": " + review.reason
                )
                if review.verdict == "needs_more_evidence":
                    continue
                if review.verdict != "supported":
                    status = review.verdict
                    break
                if "get_forecast" not in tools:
                    status = "inconclusive"
                    break
                fc = tools["get_forecast"]
                values = facts(state, fc)
                baseline = Draft(
                    claims=[
                        Claim(
                            metric=k,
                            value=v,
                            source_sequence=seq,
                            event_ids=[window[-1].event_id] if window else [],
                        )
                        for k, v in values.items()
                    ],
                    angle="chances" if significant else "forecast",
                )
                record(
                    "narrating",
                    "handoff",
                    "Narrative"
                    if self.provider.enabled
                    else "Verified template renderer",
                )
                draft = (
                    await invoke("Narrative", baseline.model_dump(), Draft)
                    if self.provider.enabled
                    else baseline
                )
                record("validating", "validate_evidence")
                validation = validate(
                    draft, state, fc, events[:seq], require_complete=True
                )
                if not validation["valid"] and self.provider.enabled:
                    record(
                        "narrating",
                        "repair",
                        "One bounded repair using validator errors",
                    )
                    draft = await invoke(
                        "Narrative",
                        dict(
                            verified=baseline.model_dump(), errors=validation["errors"]
                        ),
                        Draft,
                    )
                    validation = validate(
                        draft, state, fc, events[:seq], require_complete=True
                    )
                    record(
                        "validating",
                        "validate_repair",
                        "passed" if validation["valid"] else "rejected",
                    )
                status = "published" if validation["valid"] else "rejected"
                break
            else:
                status = "inconclusive"
        except Exception as error:
            status = "failed"
            record(
                "failed",
                "workflow_error",
                type(error).__name__
                + "; inference or tool failed. No AI output published.",
            )
        record(status, "finalize")
        previous = self.store.list("investigation", state.match_id, seq - 1)
        previous = [i for i in previous if i["status"] == "published"]
        hypothesis = None
        if status == "published":
            probabilities = tools["get_forecast"]["probabilities"]
            hypothesis = dict(
                question="Which result is most likely under the current model?",
                favored=max(probabilities, key=probabilities.get),
                basis=tools["get_forecast"]["forecast_id"],
            )
        relation = (
            "supersedes"
            if previous
            and hypothesis
            and previous[-1].get("hypothesis", {}).get("favored")
            != hypothesis["favored"]
            else "extends"
        )
        assessments = (
            hypotheses(state, events, tools["get_forecast"])
            if status == "published"
            else []
        )
        relationships = relate(assessments, previous)
        result = dict(
            investigation_id=key,
            source_sequence=seq,
            source_hash=state_hash(state),
            revision=revision,
            match_id=state.match_id,
            execution_mode=mode,
            status=status,
            trace=trace,
            tool_count=calls,
            evidence_ids=[e.event_id for e in window],
            observations=tools,
            validation=validation,
            hypothesis=hypothesis,
            hypotheses=assessments,
            relations=relationships
            + (
                [
                    dict(
                        type=relation,
                        target=previous[-1]["investigation_id"],
                        evidence=[e.event_id for e in window],
                    )
                ]
                if previous and hypothesis
                else []
            ),
            narratives={},
        )
        if status == "published":
            result["narratives"] = {
                p: render(state, tools["get_forecast"], draft, p)
                for p in ("viewer", "analyst")
            }
        return self.store.put(key, "investigation", state.match_id, seq, result)
