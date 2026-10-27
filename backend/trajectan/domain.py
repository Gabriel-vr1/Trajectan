"""Versioned wire contracts. All team/player identities are fictional."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

MODEL = "tactical-1.0"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Tactics(Strict):
    press: float = Field(default=0.5, ge=0, le=1)
    compactness: float = Field(default=0.5, ge=0, le=1)
    directness: float = Field(default=0.5, ge=0, le=1)


class Player(Strict):
    id: str
    name: str
    role: Literal["GK", "DF", "MF", "FW"]
    passing: float
    shooting: float
    defending: float
    pace: float
    stamina: float = 1
    yellow: int = 0
    available: bool = True
    active: bool = True


class Team(Strict):
    name: str
    attack: float
    defense: float
    tactics: Tactics = Field(default_factory=Tactics)
    players: list[Player]
    substitutions: int = 0


class State(Strict):
    match_id: str
    seed: int
    model_version: str = MODEL
    schema_version: int = 1
    sequence: int = 0
    second: int = 0
    period: int = 1
    phase: Literal["ready", "playing", "halftime", "finished"] = "ready"
    score: list[int] = Field(default_factory=lambda: [0, 0])
    shots: list[int] = Field(default_factory=lambda: [0, 0])
    xg: list[float] = Field(default_factory=lambda: [0.0, 0.0])
    passes: list[int] = Field(default_factory=lambda: [0, 0])
    completed: list[int] = Field(default_factory=lambda: [0, 0])
    possession_seconds: list[int] = Field(default_factory=lambda: [0, 0])
    possession: int = 0
    possession_id: int = 1
    ball: tuple[float, float] = (50, 50)
    teams: list[Team]


class Event(Strict):
    event_id: str
    match_id: str
    sequence: int
    schema_version: int = 1
    second: int
    period: int
    kind: Literal["kickoff", "pass", "turnover", "shot", "foul", "halftime", "fulltime"]
    team: int = Field(ge=0, le=1)
    player: str | None = None
    receiver: str | None = None
    possession_id: int
    start: tuple[float, float]
    end: tuple[float, float]
    outcome: Literal[
        "restart",
        "complete",
        "intercepted",
        "recovery",
        "goal",
        "saved",
        "missed",
        "yellow",
        "red",
        "foul",
        "whistle",
    ]
    xg: float = Field(default=0, ge=0, le=1)


class ScenarioRequest(Strict):
    sequence: int = Field(ge=0)
    team: int = Field(default=0, ge=0, le=1)
    category: Literal["tactical", "circumstance"] = "tactical"
    action: Literal[
        "press",
        "compactness",
        "directness",
        "substitution",
        "role",
        "goal",
        "red_card",
        "injury",
    ] = "press"
    value: float = Field(default=0.8, ge=0, le=1)
    player: str | None = None
    replacement: str | None = None
    role: Literal["GK", "DF", "MF", "FW"] | None = None
    samples: int = Field(default=128, ge=32, le=512)
    seed: int = Field(default=710, ge=0, le=2147483647)


class Claim(Strict):
    metric: Literal[
        "home_score",
        "away_score",
        "home_shots",
        "away_shots",
        "home_xg",
        "away_xg",
        "home_win",
        "draw",
        "away_win",
    ]
    value: float
    source_sequence: int
    event_ids: list[str] = Field(default_factory=list)


class Draft(Strict):
    claims: list[Claim]
    # Select verified renderers, never publish unvalidated free-form factual prose.
    angle: Literal["score", "chances", "forecast"] = "forecast"


def initial(seed=26):
    names = [("Northbridge FC", "N", 0.73, 0.70), ("Harbour Athletic", "H", 0.69, 0.74)]
    teams = []
    for name, prefix, attack, defense in names:
        players = [
            Player(
                id=f"{prefix}{i}",
                name=f"{prefix}. {surname}",
                role=("GK" if i == 1 else "DF" if i < 6 else "MF" if i < 9 else "FW"),
                passing=0.63 + i % 4 * 0.05,
                shooting=0.55 + i % 5 * 0.06,
                defending=0.65,
                pace=0.65 + i % 3 * 0.05,
                active=i <= 11,
            )
            for i, surname in enumerate(
                [
                    "Vale",
                    "Reed",
                    "Stone",
                    "Moss",
                    "Lake",
                    "Ellis",
                    "Quinn",
                    "Lane",
                    "Cole",
                    "Finch",
                    "Wren",
                    "Ash",
                    "Brook",
                    "Dale",
                    "West",
                    "Frost",
                ],
                1,
            )
        ]
        teams.append(Team(name=name, attack=attack, defense=defense, players=players))
    return State(match_id=f"demo-{seed}", seed=seed, teams=teams)


class Probabilities(Strict):
    home: float = Field(ge=0, le=1)
    draw: float = Field(ge=0, le=1)
    away: float = Field(ge=0, le=1)


class ForecastResult(Strict):
    match_id: str
    forecast_id: str
    source_sequence: int
    state_hash: str
    model_version: str
    samples: int
    seed: int
    probabilities: Probabilities
    standard_errors: Probabilities
    label: str


class MatchResponse(Strict):
    initial: State
    events: list[Event]
    total: int
    synthetic: bool


class StateResponse(Strict):
    state: State
    state_hash: str
