"""Structured, evidence-linked hypotheses; never rewrites earlier findings."""


def hypotheses(state, events, prediction):
    current = events[max(0, state.sequence - 25) : state.sequence]
    previous = events[max(0, state.sequence - 50) : max(0, state.sequence - 25)]
    counts = lambda window: [
        sum(e.kind == "shot" and e.team == team for e in window) for team in (0, 1)
    ]
    now = counts(current)
    before = counts(previous)
    balance = now[0] - now[1]
    result = [
        dict(
            key="outcome_leader",
            assessment=max(
                prediction["probabilities"], key=prediction["probabilities"].get
            ),
            source_sequence=state.sequence,
            forecast_id=prediction["forecast_id"],
            evidence_ids=[e.event_id for e in current],
            qualifier="Most likely outcome within this synthetic model, not a certain result.",
        )
    ]
    if len(current) >= 10:
        result.append(
            dict(
                key="recent_shot_balance",
                assessment="home"
                if balance > 0
                else "away"
                if balance < 0
                else "level",
                counts=now,
                previous_counts=before,
                source_sequence=state.sequence,
                evidence_ids=[e.event_id for e in current],
                previous_evidence_ids=[e.event_id for e in previous],
                qualifier="Observed shot counts over an event window; not possession control or causal superiority.",
            )
        )
    return result


def relate(current, prior):
    relations = []
    for hypothesis in current:
        for finding in reversed(prior):
            old = next(
                (
                    h
                    for h in finding.get("hypotheses", [])
                    if h["key"] == hypothesis["key"]
                ),
                None,
            )
            if old is None:
                continue
            changed = old["assessment"] != hypothesis["assessment"]
            relations.append(
                dict(
                    type="contradicts" if changed else "supports",
                    target=finding["investigation_id"],
                    hypothesis=hypothesis["key"],
                    previous_assessment=old["assessment"],
                    assessment=hypothesis["assessment"],
                    previous_sequence=old["source_sequence"],
                    source_sequence=hypothesis["source_sequence"],
                    evidence=hypothesis["evidence_ids"],
                    basis=hypothesis["qualifier"],
                )
            )
            break
    return relations


def recap_memory(records, sequence):
    """Only published historical records; retain revision references and qualifiers."""
    scoped = [
        r
        for r in records
        if r["status"] == "published" and r["source_sequence"] <= sequence
    ]
    by_id = {r["investigation_id"]: r for r in scoped}
    revisions = []
    for result in scoped:
        for relation in result.get("relations", []):
            if relation["type"] != "contradicts" or relation["target"] not in by_id:
                continue
            revisions.append(
                dict(investigation_id=result["investigation_id"], **relation)
            )
    return dict(investigation_refs=list(by_id), revisions=revisions)
