"""Exercise a running production bundle without cloud credentials."""

import json
import sys
import time
import urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def call(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        base + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def job(path, body):
    current = call(path, body)
    for _ in range(120):
        if current["status"] == "completed":
            return current["result"]
        if current["status"] == "failed":
            raise RuntimeError(current["error"])
        time.sleep(0.5)
        current = call("/api/jobs/" + current["job_id"])
    raise RuntimeError("Job did not complete")


for _ in range(30):
    try:
        health = call("/api/health")
        break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("API did not start")
with urllib.request.urlopen(base, timeout=10) as response:
    assert b'<div id="root">' in response.read()
fixture = call("/api/matches/26")
seq = next(e["sequence"] for e in fixture["events"] if e["kind"] == "halftime")
before = call(f"/api/matches/26/states/{seq}")
insight = job(f"/api/matches/26/investigations/{seq}", {})
assert insight["status"] == "published" and insight["validation"]["valid"]
branch = job(
    "/api/matches/26/scenarios",
    {"sequence": seq, "action": "press", "value": 0.8, "samples": 32},
)
assert abs(sum(branch["alternative"]["probabilities"].values()) - 1) < 1e-9
assert call(f"/api/matches/26/states/{seq}") == before
recap = call(f"/api/matches/26/recap/{seq}?profile=analyst")
assert recap["validation"]["valid"] and "Monte Carlo" in recap["text"]
print(
    json.dumps(
        {
            "health": health,
            "events": fixture["total"],
            "checkpoint": seq,
            "investigation": insight["status"],
            "scenario": branch["status"],
            "history_unchanged": True,
            "recap_verified": True,
        },
        indent=2,
    )
)
