import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .domain import (
    initial,
    ScenarioRequest,
    Draft,
    Claim,
    ForecastResult,
    MatchResponse,
    StateResponse,
)
from .simulation import generate, state_hash
from .analytics import forecast, scenario, attribution
from .persistence import Store
from .agents import Workflow
from .validation import facts, validate, render
from .jobs import Jobs, ServiceBusQueue
from .memory import recap_memory


@lru_cache(maxsize=3)
def match(seed):
    if seed not in (26, 77, 2026):
        raise HTTPException(404, "Unknown fixture seed")
    return generate(initial(seed))


def pinned(seed, seq):
    events, states = match(seed)
    if seq >= len(states) or seq < 0:
        raise HTTPException(404, "Unknown state sequence")
    return events, states, states[seq]


@lru_cache(maxsize=1024)
def cached_forecast(seed, seq):
    return forecast(pinned(seed, seq)[2])


@asynccontextmanager
async def lifespan(app):
    app.state.store = Store()
    app.state.workflow = Workflow(app.state.store)

    async def handle(request):
        seed = request["seed"]
        seq = request["sequence"]
        events, states, state = pinned(seed, seq)
        if request["kind"] == "investigation":
            return await app.state.workflow.run(
                states, events, seq, request.get("revision", 0)
            )
        payload = ScenarioRequest.model_validate(request["payload"])
        result = await asyncio.to_thread(scenario, state, payload)
        return app.state.store.put(
            request["key"], "scenario", state.match_id, state.sequence, result
        )

    queue = ServiceBusQueue() if os.getenv("SERVICE_BUS_NAMESPACE") else None
    app.state.jobs = Jobs(app.state.store, handle, queue)
    for seed in (26, 77, 2026):
        events, states = match(seed)
        app.state.store.put(
            f"events:demo-{seed}",
            "events",
            f"demo-{seed}",
            0,
            [e.model_dump() for e in events],
        )
        for state in states[::25]:
            app.state.store.put(
                f"snapshot:{state.match_id}:{state.sequence}",
                "snapshot",
                state.match_id,
                state.sequence,
                dict(state=state.model_dump(), state_hash=state_hash(state)),
            )
    app.state.jobs.start()
    yield
    await app.state.jobs.close()
    await app.state.workflow.provider.close()


app = FastAPI(title="Trajectan", version="1.0.0", lifespan=lifespan)


@app.get("/api/health")
def health():
    return dict(
        status="degraded"
        if not app.state.workflow.provider.enabled
        else "inference-observed"
        if getattr(app.state.workflow.provider, "successful_calls", 0)
        else "configured-unverified",
        model="tactical-1.0",
        ai="Foundry API responses observed; publication remains independently validated"
        if getattr(app.state.workflow.provider, "successful_calls", 0)
        else "configured; live call required"
        if app.state.workflow.provider.enabled
        else "unavailable; deterministic development fallback",
        database="sqlite-development"
        if app.state.store.url.startswith("sqlite")
        else "postgresql-configured",
        queue=app.state.jobs.queue.mode,
        queue_error=app.state.jobs.last_error,
        ai_configuration_error=getattr(
            app.state.workflow.provider, "configuration_error", None
        ),
        inference_calls=getattr(app.state.workflow.provider, "successful_calls", 0),
        synthetic=True,
    )


@app.get("/api/matches")
def matches():
    return [
        dict(
            seed=s, match_id=f"demo-{s}", home="Northbridge FC", away="Harbour Athletic"
        )
        for s in (26, 77, 2026)
    ]


@app.get("/api/matches/{seed}", response_model=MatchResponse)
def get_match(seed: int):
    events, states = match(seed)
    return dict(initial=states[0], events=events, total=len(events), synthetic=True)


@app.get("/api/matches/{seed}/states/{seq}", response_model=StateResponse)
def get_state(seed: int, seq: int):
    _, _, state = pinned(seed, seq)
    return dict(state=state, state_hash=state_hash(state))


@app.get("/api/matches/{seed}/forecasts/{seq}", response_model=ForecastResult)
def get_forecast(seed: int, seq: int):
    return cached_forecast(seed, seq)


@app.get("/api/matches/{seed}/attribution/{seq}")
def get_attribution(
    seed: int, seq: int, previous: int = Query(0, ge=0), reverse: bool = False
):
    _, states, state = pinned(seed, seq)
    if previous > seq:
        raise HTTPException(422, "Previous state must precede selected state")
    return attribution(states[previous], state, 64, reverse=reverse)


def submit(key, request):
    try:
        return app.state.jobs.submit(key, request)
    except ValueError as e:
        raise HTTPException(429, str(e))


@app.post("/api/matches/{seed}/investigations/{seq}")
async def investigate(seed: int, seq: int, revision: int = Query(0, ge=0, le=2)):
    events, states, state = pinned(seed, seq)
    return submit(
        app.state.workflow.execution_key(state, revision),
        dict(kind="investigation", seed=seed, sequence=seq, revision=revision),
    )


@app.get("/api/matches/{seed}/investigations")
def investigations(seed: int, sequence: int = Query(100000, ge=0)):
    match(seed)
    return app.state.store.list("investigation", f"demo-{seed}", sequence)


@app.post("/api/matches/{seed}/scenarios")
async def simulate(seed: int, request: ScenarioRequest):
    _, _, state = pinned(seed, request.sequence)
    from .analytics import intervene

    try:
        intervene(state, request)
    except ValueError as e:
        raise HTTPException(422, str(e))
    key = "scenario:" + str(
        uuid.uuid5(uuid.NAMESPACE_URL, state_hash(state) + request.model_dump_json())
    )
    return submit(
        key,
        dict(
            kind="scenario",
            seed=seed,
            sequence=state.sequence,
            key=key,
            payload=request.model_dump(),
        ),
    )


@app.get("/api/jobs/{key}")
def job(key: str):
    result = app.state.jobs.get(key)
    if result:
        return result
    raise HTTPException(404, "Unknown job")


@app.get("/api/matches/{seed}/recap/{seq}")
def recap(
    seed: int, seq: int, profile: str = Query("viewer", pattern="^(viewer|analyst)$")
):
    events, _, s = pinned(seed, seq)
    f = cached_forecast(seed, seq)
    draft = Draft(
        claims=[
            Claim(metric=k, value=v, source_sequence=seq)
            for k, v in facts(s, f).items()
        ],
        angle="chances",
    )
    report = validate(draft, s, f, events[:seq])
    return dict(
        **render(s, f, draft, profile),
        **recap_memory(app.state.store.list("investigation", s.match_id, seq), seq),
        validation=report,
        kind="full-time"
        if s.phase == "finished"
        else "half-time"
        if s.phase == "halftime"
        else "checkpoint",
        moments=[e.model_dump() for e in events[:seq] if e.outcome in ("goal", "red")],
        execution_mode="verified-deterministic-template",
    )


@app.get("/api/matches/{seed}/stream")
async def stream(seed: int, request: Request, after: int = Query(0, ge=0)):
    events, _ = match(seed)
    try:
        cursor = max(after, int(request.headers.get("last-event-id", "0")))
    except ValueError:
        raise HTTPException(422, "Invalid Last-Event-ID")

    async def output():
        for event in events[cursor:]:
            if await request.is_disconnected():
                break
            yield f"id: {event.sequence}\nevent: match\ndata: {event.model_dump_json()}\n\n"
            await asyncio.sleep(0.8)

    return StreamingResponse(
        output(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


web = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if web.exists():
    app.mount("/assets", StaticFiles(directory=web / "assets"), name="assets")

    @app.get("/")
    def index():
        return FileResponse(web / "index.html")
