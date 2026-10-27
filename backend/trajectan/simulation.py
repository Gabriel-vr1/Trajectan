"""One transition kernel for authoritative events and every Monte Carlo continuation.
Coefficients are illustrative synthetic assumptions, not fitted real football data.
"""

import hashlib
import json
import math
import random
from .domain import State, Event


def state_hash(state):
    return hashlib.sha256(
        json.dumps(state.model_dump(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def direction(team, period):
    return 1 if (team == 0) == (period == 1) else -1


def active(state, team):
    return [p for p in state.teams[team].players if p.active and p.available]


def propose(s: State, rng: random.Random) -> Event:
    team = s.possession
    start = s.ball
    base = dict(
        event_id=f"{s.match_id}:{s.sequence + 1}",
        match_id=s.match_id,
        sequence=s.sequence + 1,
        second=s.second,
        period=s.period,
        team=team,
        possession_id=s.possession_id,
        start=start,
        end=start,
    )
    if s.phase in ("ready", "halftime"):
        return Event(
            **(base | dict(period=2 if s.phase == "halftime" else 1, end=(50, 50))),
            kind="kickoff",
            outcome="restart",
        )
    if s.phase == "finished":
        raise ValueError("Match is finished")
    urgency = 2 if s.second > 4200 and s.score[team] < s.score[1 - team] else 0
    second = min(
        2700 if s.period == 1 else 5400, s.second + rng.randint(8, 24) - urgency
    )
    base["second"] = second
    if second in (2700, 5400):
        return Event(
            **base, kind="halftime" if second == 2700 else "fulltime", outcome="whistle"
        )
    own = s.teams[team]
    opposition = s.teams[1 - team]
    players = [p for p in active(s, team) if p.role != "GK"]
    weights = [
        1.3 if p.role == "MF" else 1.15 if p.role == "FW" else 0.8 for p in players
    ]
    player = rng.choices(players, weights=weights, k=1)[0]
    base["player"] = player.id
    t = own.tactics
    ot = opposition.tactics
    d = direction(team, s.period)
    progress = start[0] if d == 1 else 100 - start[0]
    fatigue = 1 - player.stamina
    # High pressing increases recovery odds but leaves space when bypassed.
    numbers = (len(active(s, team)) - len(active(s, 1 - team))) / 11
    shot_chance = max(
        0.01,
        (progress / 100) ** 3
        * (
            0.22
            + 0.16 * t.directness
            + 0.10 * ot.press
            + 0.18 * numbers
            + 0.15 * (own.attack - opposition.defense)
        ),
    )
    roll = rng.random()
    if roll < 0.025:
        offender = rng.choice([p for p in active(s, 1 - team) if p.role != "GK"])
        card = rng.random()
        outcome = (
            "red"
            if card < 0.018 or (card < 0.20 and offender.yellow)
            else "yellow"
            if card < 0.20
            else "foul"
        )
        if len(active(s, 1 - team)) <= 7:
            outcome = "foul"
        return Event(
            **(base | dict(team=1 - team, player=offender.id)),
            kind="foul",
            outcome=outcome,
        )
    if roll < 0.025 + shot_chance:
        xg = max(
            0.015,
            min(
                0.55,
                0.035
                + 0.28 * (progress / 100) ** 4
                + 0.13 * (player.shooting - 0.6)
                - 0.08 * abs(start[1] - 50) / 50
                + 0.05 * (own.attack - opposition.defense),
            ),
        )
        outcome = (
            "goal"
            if rng.random() < xg
            else "saved"
            if rng.random() < 0.60
            else "missed"
        )
        return Event(**base, kind="shot", outcome=outcome, xg=round(xg, 5))
    if roll < 0.065 + shot_chance + 0.045 * ot.press:
        return Event(**base, kind="turnover", outcome="recovery")
    advance = rng.uniform(-8, 22) + t.directness * 10 + (player.pace - 0.7) * 8
    x = max(2, min(98, start[0] + d * advance))
    y = max(3, min(97, start[1] + rng.uniform(-22, 22)))
    distance = math.hypot(x - start[0], y - start[1])
    probability = max(
        0.35,
        min(
            0.95,
            0.92
            + 0.15 * (player.passing - 0.7)
            - distance * 0.004
            - 0.09 * ot.press
            - 0.08 * fatigue
            - 0.08 * t.directness
            + 0.04 * ot.compactness
            + 0.15 * numbers,
        ),
    )
    receivers = [p for p in players if p.id != player.id]
    return Event(
        **(
            base
            | dict(end=(round(x, 2), round(y, 2)), receiver=rng.choice(receivers).id)
        ),
        kind="pass",
        outcome="complete" if rng.random() < probability else "intercepted",
    )


def apply(s: State, e: Event, copy=True):
    if copy:
        s = s.model_copy(deep=True)
    if (
        e.match_id != s.match_id
        or e.sequence != s.sequence + 1
        or e.second < s.second
        or e.second > 5400
    ):
        raise ValueError("Invalid event order or clock")
    if (
        e.event_id != f"{s.match_id}:{e.sequence}"
        or e.start != s.ball
        or e.possession_id != s.possession_id
    ):
        raise ValueError("Event provenance mismatch")
    if any(not 0 <= v <= 100 for v in (*e.start, *e.end)):
        raise ValueError("Outside pitch")
    allowed = {
        "kickoff": {"restart"},
        "pass": {"complete", "intercepted"},
        "turnover": {"recovery"},
        "shot": {"goal", "saved", "missed"},
        "foul": {"yellow", "red", "foul"},
        "halftime": {"whistle"},
        "fulltime": {"whistle"},
    }
    if e.outcome not in allowed[e.kind]:
        raise ValueError("Illegal action outcome")
    if e.kind != "shot" and e.xg != 0:
        raise ValueError("Only shots have xG")
    if e.kind != "pass" and e.receiver is not None:
        raise ValueError("Only passes have receivers")
    if e.kind in ("kickoff", "halftime", "fulltime") and e.player is not None:
        raise ValueError("Control events have no player")
    if e.kind != "kickoff" and e.second <= s.second:
        raise ValueError("Playing time must advance")
    if s.phase == "finished":
        raise ValueError("Match is finished")
    if s.phase in ("ready", "halftime") and e.kind != "kickoff":
        raise ValueError("Kickoff required")
    if e.kind == "kickoff" and s.phase not in ("ready", "halftime"):
        raise ValueError("Unexpected kickoff")
    expected_period = 2 if s.phase == "halftime" else s.period
    if e.period != expected_period:
        raise ValueError("Invalid period")
    if e.kind == "halftime" and (s.period != 1 or e.second != 2700):
        raise ValueError("Invalid halftime")
    if e.kind == "fulltime" and (s.period != 2 or e.second != 5400):
        raise ValueError("Invalid fulltime")
    if e.kind not in ("kickoff", "halftime", "fulltime"):
        if s.phase != "playing" or e.second >= (2700 if s.period == 1 else 5400):
            raise ValueError("Illegal playing time")
        if e.team != (1 - s.possession if e.kind == "foul" else s.possession):
            raise ValueError("Wrong possession team")
        if e.player not in [p.id for p in active(s, e.team)]:
            raise ValueError("Unavailable player")
    dt = e.second - s.second
    s.possession_seconds[s.possession] += dt
    for team in s.teams:
        for p in team.players:
            if p.active and p.available:
                p.stamina = max(
                    0.2, p.stamina - dt / 16000 * (1 + team.tactics.press * 0.5)
                )
    s.sequence = e.sequence
    s.second = e.second
    s.period = e.period
    s.ball = e.end
    if e.kind == "kickoff":
        s.phase = "playing"
        s.ball = (50, 50)
    elif e.kind == "halftime":
        s.phase = "halftime"
        s.possession = 1
        s.possession_id += 1
    elif e.kind == "fulltime":
        s.phase = "finished"
    elif e.kind == "pass":
        if (
            e.receiver not in [p.id for p in active(s, e.team)]
            or e.receiver == e.player
        ):
            raise ValueError("Illegal receiver")
        s.passes[e.team] += 1
        if e.outcome == "complete":
            s.completed[e.team] += 1
    elif e.kind == "shot":
        s.shots[e.team] += 1
        s.xg[e.team] += e.xg
        if e.outcome == "goal":
            s.score[e.team] += 1
    elif e.kind == "foul":
        p = next(p for p in s.teams[e.team].players if p.id == e.player)
        if e.outcome == "yellow":
            if p.yellow:
                raise ValueError("Second yellow must dismiss")
            p.yellow += 1
        if e.outcome == "red":
            if len(active(s, e.team)) <= 7:
                raise ValueError("Minimum team size")
            p.available = False
    if e.kind in ("shot", "turnover") or e.outcome == "intercepted":
        s.possession = 1 - s.possession
        s.possession_id += 1
        if e.kind == "shot":
            s.ball = (
                (50, 50)
                if e.outcome == "goal"
                else ((10 if direction(s.possession, s.period) == 1 else 90), 50)
            )
    return s


def generate(initial):
    s = initial.model_copy(deep=True)
    events = []
    states = [s.model_copy(deep=True)]
    while s.phase != "finished":
        # Per-event stream index makes snapshot continuation reproducible.
        e = propose(s, random.Random(s.seed * 1000003 + s.sequence))
        s = apply(s, e)
        events.append(e)
        states.append(s)
    return events, states


def replay(initial, events):
    s = initial.model_copy(deep=True)
    for e in events:
        s = apply(s, e, copy=False)
    return s
