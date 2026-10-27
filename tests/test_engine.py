import random
import pytest
from pydantic import ValidationError
from trajectan.domain import initial, ScenarioRequest, Draft, Claim
from trajectan.simulation import generate, replay, state_hash, apply, active, propose
from trajectan.analytics import forecast, scenario, attribution, intervene
from trajectan.validation import validate, render, facts


@pytest.fixture(scope="module")
def fixture():
    return generate(initial())


@pytest.mark.parametrize("seed", [26, 77, 2026])
def test_deterministic_legal_complete_match(seed):
    a, states = generate(initial(seed))
    b, end = generate(initial(seed))
    assert a == b and states[-1] == end[-1]
    assert states[-1].second == 5400 and states[-1].phase == "finished"
    assert sum(e.kind == "halftime" for e in a) == 1
    assert sum(e.kind == "kickoff" for e in a) == 2
    assert len({e.event_id for e in a}) == len(a)
    assert sum(states[-1].score) == sum(e.outcome == "goal" for e in a)
    assert sum(states[-1].shots) == sum(e.kind == "shot" for e in a)
    assert sum(states[-1].possession_seconds) == 5400
    for s in states:
        assert all(0 <= c <= 100 for c in s.ball)
        assert all(7 <= len(active(s, t)) <= 11 for t in (0, 1))


def test_snapshot_replay_and_continuation(fixture):
    events, states = fixture
    assert state_hash(replay(states[0], events)) == state_hash(
        replay(states[100], events[100:])
    )
    e = propose(states[100], random.Random(26 * 1000003 + 100))
    assert e == events[100]
    assert states[100].sequence == 100


@pytest.mark.parametrize(
    "change",
    [
        {"sequence": 99},
        {"team": 1},
        {"outcome": "goal"},
        {"end": (101, 20)},
        {"player": "unknown"},
        {"period": 2},
    ],
)
def test_invalid_event_rejected(fixture, change):
    events, states = fixture
    e = next(e for e in events if e.kind == "pass" and e.team == 0)
    with pytest.raises(ValueError):
        apply(states[e.sequence - 1], e.model_copy(update=change))


def test_probability_and_final_certainty(fixture):
    _, states = fixture
    f = forecast(states[250], 32)
    assert sum(f["probabilities"].values()) == pytest.approx(1)
    assert all(0 <= p <= 1 for p in f["probabilities"].values())
    assert f == forecast(states[250], 32)
    final = forecast(states[-1], 32)
    target = (
        "home"
        if states[-1].score[0] > states[-1].score[1]
        else "draw"
        if states[-1].score[0] == states[-1].score[1]
        else "away"
    )
    assert final["probabilities"][target] == 1


def test_scenario_isolation_and_noop(fixture):
    _, states = fixture
    s = states[250]
    before = state_hash(s)
    r = ScenarioRequest(
        sequence=250, action="press", value=s.teams[0].tactics.press, samples=32
    )
    result = scenario(s, r)
    assert all(v == 0 for v in result["delta"].values())
    assert all(v == 0 for v in result["delta_standard_errors"].values())
    assert state_hash(s) == before
    changed = scenario(s, r.model_copy(update={"value": 1.0}))
    assert changed == scenario(s, r.model_copy(update={"value": 1.0}))
    assert state_hash(s) == before


def test_circumstance_and_personnel_legality(fixture):
    _, states = fixture
    s = states[200]
    with pytest.raises(ValueError):
        intervene(s, ScenarioRequest(sequence=200, action="goal"))
    with pytest.raises(ValueError):
        intervene(
            s,
            ScenarioRequest(
                sequence=200, action="substitution", player="N1", replacement="N2"
            ),
        )
    branch = intervene(
        s,
        ScenarioRequest(
            sequence=200, action="substitution", player="N1", replacement="N12"
        ),
    )
    assert len(active(branch, 0)) == 11
    assert not branch.teams[0].players[0].available
    assert len(active(s, 0)) == 11
    with pytest.raises(ValidationError):
        ScenarioRequest(sequence=2, value=2)


def test_attribution_reconciles(fixture):
    _, states = fixture
    a = attribution(states[230], states[250], 32)
    assert a["delta"] == pytest.approx(
        sum(c["home"] for c in a["contributions"]) + a["residual"]
    )
    assert a["verified"] and abs(a["residual"]) < 1e-9


def test_claim_gate_rejects_invented_future_and_wrong_scope(fixture):
    events, states = fixture
    s = states[250]
    f = forecast(s, 32)
    good = Draft(
        claims=[
            Claim(
                metric="home_score",
                value=s.score[0],
                source_sequence=250,
                event_ids=[events[249].event_id],
            )
        ]
    )
    assert validate(good, s, f, events)["valid"]
    for update in (
        {"value": 999},
        {"source_sequence": 251},
        {"event_ids": [events[251].event_id]},
        {"event_ids": ["other:2"]},
    ):
        bad = Draft(claims=[good.claims[0].model_copy(update=update)])
        assert not validate(bad, s, f, events)["valid"]
    with pytest.raises(ValidationError):
        Draft.model_validate({"claims": [], "text": "This tactic guarantees victory"})
    assert not validate(Draft(claims=[]), s, f, events)["valid"]


def test_personalization_preserves_claims(fixture):
    events, states = fixture
    s = states[250]
    f = forecast(s, 32)
    d = Draft(
        claims=[
            Claim(metric=k, value=v, source_sequence=250)
            for k, v in facts(s, f).items()
        ]
    )
    viewer = render(s, f, d, "viewer")
    analyst = render(s, f, d, "analyst")
    assert viewer["claims"] == analyst["claims"]
    assert viewer["text"] != analyst["text"] and "Monte Carlo" in analyst["text"]


def test_nonfinite_and_cross_match_claims_rejected(fixture):
    with pytest.raises(ValidationError):
        Claim(metric="home_score", value=float("nan"), source_sequence=1)
    events, states = fixture
    s = states[-1]
    f = forecast(s, 32)
    d = Draft(
        claims=[
            Claim(metric="home_score", value=s.score[0], source_sequence=s.sequence)
        ]
    )
    assert not validate(d, s, f | {"match_id": "another-match"}, events)["valid"]
    assert not validate(d, s, f | {"state_hash": "tampered"}, events)["valid"]


def test_attribution_paired_intervals_and_order(fixture):
    _, states = fixture
    same = attribution(states[300], states[300], 32)
    assert same["delta_standard_error"] == 0
    assert all(
        c["standard_error"] == 0 and c["interval_95"] == [0, 0]
        for c in same["contributions"]
    )
    forward = attribution(states[280], states[300], 32)
    reverse = attribution(states[280], states[300], 32, reverse=True)
    assert forward["delta"] == reverse["delta"]
    assert forward["verified"] and reverse["verified"]
    assert all(
        c["interval_95"][0] <= c["home"] <= c["interval_95"][1]
        for c in forward["contributions"]
    )
    with pytest.raises(ValueError):
        attribution(states[300], states[280], 32)


def test_incomplete_publication_claims_and_duplicate_claims(fixture):
    events, states = fixture
    s = states[-1]
    f = forecast(s, 32)
    claim = Claim(metric="home_score", value=s.score[0], source_sequence=s.sequence)
    assert validate(Draft(claims=[claim]), s, f, events)["valid"]
    assert not validate(Draft(claims=[claim]), s, f, events, require_complete=True)[
        "valid"
    ]
    assert not validate(Draft(claims=[claim, claim]), s, f, events)["valid"]
