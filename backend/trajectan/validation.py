from .domain import Draft
from .simulation import state_hash


def facts(state, forecast):
    return dict(
        home_score=state.score[0],
        away_score=state.score[1],
        home_shots=state.shots[0],
        away_shots=state.shots[1],
        home_xg=state.xg[0],
        away_xg=state.xg[1],
        home_win=forecast["probabilities"]["home"],
        draw=forecast["probabilities"]["draw"],
        away_win=forecast["probabilities"]["away"],
    )


def validate(draft: Draft, state, forecast, events, require_complete=False):
    expected = facts(state, forecast)
    valid_ids = {
        e.event_id
        for e in events
        if e.sequence <= state.sequence and e.match_id == state.match_id
    }
    errors = []
    if (
        forecast["source_sequence"] != state.sequence
        or forecast["state_hash"] != state_hash(state)
        or forecast["match_id"] != state.match_id
    ):
        errors.append("Forecast state mismatch")
    if not draft.claims:
        errors.append("No evidence claims")
    metrics = [c.metric for c in draft.claims]
    if len(metrics) != len(set(metrics)):
        errors.append("Duplicate factual claim")
    if require_complete and set(metrics) != set(expected):
        errors.append("Publication requires the complete verified fact set")
    for c in draft.claims:
        if c.source_sequence != state.sequence:
            errors.append("Claim state mismatch")
        if abs(c.value - expected[c.metric]) > 1e-8:
            errors.append(f"Unsupported value: {c.metric}")
        if any(ref not in valid_ids for ref in c.event_ids):
            errors.append("Unknown or future event reference")
    return dict(
        valid=not errors,
        errors=errors,
        validator_version="strict-claims-2",
        source_sequence=state.sequence,
    )


def render(state, forecast, draft, profile="viewer"):
    # All prose is rendered from verified data; a model selects the angle, not facts.
    f = facts(state, forecast)
    home, away = [t.name for t in state.teams]
    score = f"{home} {state.score[0]}–{state.score[1]} {away}"
    chance = f"{home} win {f['home_win']:.1%}; draw {f['draw']:.1%}; {away} win {f['away_win']:.1%}."
    if profile == "analyst":
        text = f"{score}. Shots {state.shots[0]}–{state.shots[1]}; model xG {state.xg[0]:.2f}–{state.xg[1]:.2f}. {chance} Based on {forecast['samples']} continuations at state {state.sequence}, seed {forecast['seed']}. Home-win Monte Carlo SE {forecast['standard_errors']['home']:.1%}."
    else:
        text = (
            f"{score}. "
            + (
                f"The teams have taken {state.shots[0]} and {state.shots[1]} shots. "
                if draft.angle == "chances"
                else ""
            )
            + chance
            + " These are possibilities from a synthetic football model, not a prediction of a real match."
        )
    return dict(
        profile=profile,
        headline=score,
        text=text,
        claims=draft.model_dump()["claims"],
        source_sequence=state.sequence,
        synthetic=True,
    )
