import math
import random
from .domain import MODEL, ScenarioRequest
from .simulation import propose, apply, state_hash, active


def outcomes(state, samples, seed):
    results = []
    for i in range(samples):
        s = state.model_copy(deep=True)
        rng = random.Random(seed + i * 104729)
        while s.phase != "finished":
            apply(s, propose(s, rng), copy=False)
        results.append(
            0 if s.score[0] > s.score[1] else 1 if s.score[0] == s.score[1] else 2
        )
    return results


def summarize(state, results, seed):
    n = len(results)
    ps = [results.count(i) / n for i in range(3)]
    return dict(
        match_id=state.match_id,
        forecast_id=f"{state_hash(state)[:16]}:{n}:{seed}",
        source_sequence=state.sequence,
        state_hash=state_hash(state),
        model_version=MODEL,
        samples=n,
        seed=seed,
        probabilities=dict(zip(("home", "draw", "away"), ps)),
        standard_errors=dict(
            zip(("home", "draw", "away"), [math.sqrt(p * (1 - p) / n) for p in ps])
        ),
        label="Synthetic model forecast; not calibrated to real matches",
    )


def forecast(state, samples=128, seed=710):
    return summarize(state, outcomes(state, samples, seed), seed)


def intervene(state, r: ScenarioRequest):
    if state.phase == "finished":
        raise ValueError("Choose a checkpoint before full time")
    if (r.action in ("goal", "red_card", "injury")) != (r.category == "circumstance"):
        raise ValueError(
            "Tactical choices and hypothetical circumstances must be labelled separately"
        )
    branch = state.model_copy(deep=True)
    team = branch.teams[r.team]
    if r.action in ("press", "compactness", "directness"):
        setattr(team.tactics, r.action, r.value)
    elif r.action == "goal":
        branch.score[r.team] += 1
    else:
        p = next(
            (p for p in team.players if p.id == r.player and p.active and p.available),
            None,
        )
        if p is None:
            raise ValueError("Select an eligible active player")
        if r.action in ("red_card", "injury"):
            if len(active(branch, r.team)) <= 7:
                raise ValueError("Cannot reduce team below seven players")
            p.available = False
        elif r.action == "role":
            if not r.role or p.role == "GK" or r.role == "GK":
                raise ValueError("Choose an outfield role")
            p.role = r.role
        elif r.action == "substitution":
            q = next(
                (
                    q
                    for q in team.players
                    if q.id == r.replacement and not q.active and q.available
                ),
                None,
            )
            if q is None or team.substitutions >= 5:
                raise ValueError("Invalid substitution")
            p.active = False
            p.available = False
            q.active = True
            q.role = p.role
            team.substitutions += 1
    return branch


def scenario(state, r):
    before = state_hash(state)
    branch = intervene(state, r)
    a = outcomes(state, r.samples, r.seed)
    b = outcomes(branch, r.samples, r.seed)
    baseline = summarize(state, a, r.seed)
    alternative = summarize(branch, b, r.seed)
    delta = {}
    se = {}
    for i, key in enumerate(("home", "draw", "away")):
        diffs = [int(y == i) - int(x == i) for x, y in zip(a, b)]
        mean = sum(diffs) / r.samples
        delta[key] = mean
        se[key] = math.sqrt(
            sum((d - mean) ** 2 for d in diffs) / (r.samples - 1) / r.samples
        )
    assert state_hash(state) == before
    return dict(
        source_sequence=state.sequence,
        source_hash=before,
        intervention=r.model_dump(),
        baseline=baseline,
        alternative=alternative,
        delta=delta,
        delta_standard_errors=se,
        label="Hypothetical branch under Trajectan’s model; not a real-world causal prediction",
        seed_design="paired continuation seeds",
        status="completed",
    )


def paired_difference(before, after, target=0):
    differences = [int(y == target) - int(x == target) for x, y in zip(before, after)]
    n = len(differences)
    mean = sum(differences) / n
    se = (
        math.sqrt(sum((x - mean) ** 2 for x in differences) / (n - 1) / n)
        if n > 1
        else 0
    )
    return dict(
        mean=mean,
        standard_error=se,
        interval_95=[max(-1, mean - 1.96 * se), min(1, mean + 1.96 * se)],
    )


def attribution(previous, current, samples=128, seed=710, reverse=False):
    if (
        previous.match_id != current.match_id
        or previous.model_version != current.model_version
        or previous.sequence > current.sequence
    ):
        raise ValueError(
            "Attribution requires ordered states from the same match and model"
        )
    groups = [
        ("Score & clock", ["score", "second", "period", "phase"]),
        ("Personnel & tactics", ["teams"]),
        ("Possession & territory", ["possession", "possession_id", "ball"]),
    ]
    if reverse:
        groups.reverse()
    source = previous.model_copy(deep=True)
    start = outcomes(source, samples, seed)
    last = start
    contributions = []
    for label, fields in groups:
        for field in fields:
            setattr(source, field, getattr(current.model_copy(deep=True), field))
        nxt = outcomes(source, samples, seed)
        difference = paired_difference(last, nxt)
        contributions.append(
            dict(
                factor=label,
                home=difference["mean"],
                standard_error=difference["standard_error"],
                interval_95=difference["interval_95"],
            )
        )
        last = nxt
    end = outcomes(current, samples, seed)
    delta = paired_difference(start, end)
    residual = delta["mean"] - sum(x["home"] for x in contributions)
    return dict(
        previous_sequence=previous.sequence,
        source_sequence=current.sequence,
        previous_hash=state_hash(previous),
        source_hash=state_hash(current),
        model_version=MODEL,
        method="ordered-group-replacement-v2",
        order="reverse" if reverse else "forward",
        samples=samples,
        seed=seed,
        target="home",
        delta=delta["mean"],
        delta_standard_error=delta["standard_error"],
        delta_interval_95=delta["interval_95"],
        contributions=contributions,
        residual=residual,
        verified=abs(residual) < 1e-9,
        uncertainty="Paired Monte Carlo standard errors and approximate 95% normal intervals; correlated factors, not simultaneous confidence bounds. Zero observed variation does not establish population certainty.",
        limitation="Order-dependent model decomposition, not unique real-world causation.",
    )
