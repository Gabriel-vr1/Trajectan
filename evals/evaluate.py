"""Small reproducible internal synthetic evaluation; never real-world validation."""

import json
import math
import time
from pathlib import Path
from trajectan.domain import initial, MODEL
from trajectan.simulation import generate
from trajectan.analytics import forecast

started = time.monotonic()
rows = []
for seed in range(100, 120):
    events, states = generate(initial(seed))
    checkpoint = next(s for s in states if s.phase == "halftime")
    f = forecast(checkpoint, 64, 9000 + seed)
    score = states[-1].score
    outcome = 0 if score[0] > score[1] else 1 if score[0] == score[1] else 2
    p = list(f["probabilities"].values())
    rows.append(
        dict(
            seed=seed,
            source_sequence=checkpoint.sequence,
            score=score,
            shots=states[-1].shots,
            probabilities=p,
            outcome=outcome,
            brier=sum((v - int(i == outcome)) ** 2 for i, v in enumerate(p)),
            log_loss=-math.log(max(p[outcome], 1 / 128)),
        )
    )
report = dict(
    model_version=MODEL,
    match_seeds=list(range(100, 120)),
    forecast_samples=64,
    forecast_seed_design="9000 + match seed",
    checkpoint="half-time",
    brier_definition="sum over three outcomes (not divided by 3)",
    mean_brier=sum(r["brier"] for r in rows) / len(rows),
    mean_log_loss=sum(r["log_loss"] for r in rows) / len(rows),
    log_loss_floor=1 / 128,
    seconds=round(time.monotonic() - started, 3),
    limitations="20 held-out synthetic matches only; small sample, no real-match calibration. No live LLM or three-agent comparative benchmark was run.",
    rows=rows,
)
report["reliability_bins"] = [
    dict(
        lower=lo,
        upper=lo + 0.2,
        count=len(xs),
        mean_probability=sum(x[0] for x in xs) / len(xs) if xs else None,
        observed_frequency=sum(x[1] for x in xs) / len(xs) if xs else None,
    )
    for lo in (0, 0.2, 0.4, 0.6, 0.8)
    for xs in [
        [
            (p, int(i == r["outcome"]))
            for r in rows
            for i, p in enumerate(r["probabilities"])
            if lo <= p < (lo + 0.2) or (lo == 0.8 and p == 1)
        ]
    ]
]
Path("evals/results.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in report.items() if k not in ("rows", "reliability_bins")},
        indent=2,
    )
)
