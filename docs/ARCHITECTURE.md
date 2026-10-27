# Architecture and mathematical assumptions

## Data flow

```
Seeded tactical kernel -> immutable event log -> reducer -> versioned state
                                        |                 |
                                        |                 +-> SSE / React cursor
                                        +-> forecast / attribution / scenario
                                        +-> durable job outbox
                                             -> local queue OR Service Bus
                                             -> deterministic controller
                                             -> Investigation agent / tools
                                             -> Evidence & Reasoning agent
                                             -> Narrative agent
                                             -> deterministic validator
                                             -> persisted publication / recap
```

The domain contracts live in `backend/trajectan/domain.py`. FastAPI's exported OpenAPI schema generates the primary frontend event/state/forecast types. Match data and derived artifacts remain separate tables/records. SQLAlchemy supports local SQLite and configured PostgreSQL; SQLite is the only database exercised here.

## Model tactical-1.0

The match lasts two 2,700-second halves, without added time. Each action advances 8–24 seconds (slightly faster when trailing late). Both teams have 11 active players and five substitutes. Player attributes, role-weighted action selection, fatigue, team quality, coarse territory and tactical settings affect transitions. Team direction reverses at half-time. The coordinates are normalized `[0,100]` and transformed into an SVG pitch.

Candidate events are kickoff, pass, turnover, shot, foul, half-time and full-time. The action distribution is normalized implicitly by intervals of one uniform draw; the remainder is a pass. Pass success is bounded to `[0.35,0.95]` and responds to passing ability, distance, pressure, directness, fatigue and numerical advantage. Shot frequency grows with forward territory, directness, opponent pressing, team quality and numerical advantage. Shot conversion is bounded to `[0.015,0.55]` and depends on location, shooting ability and team attack/defense. Pressing trades recoveries against space when bypassed and increases fatigue. These are authored synthetic coefficients, not learned football estimates.

One shot event contains its goal/saved/missed outcome; a goal is never counted twice. Goal restarts are represented by possession handover and a centered ball within the shot reducer. Other shot outcomes hand the ball to the defending team in its defensive third. This is an explicit coarse abstraction: no corners, offsides, penalties, injury stoppages, full player motion, scheduled in-match substitutions or added time are generated yet. Substitutions, role changes and injuries are supported in scenarios. No claim of comprehensive football realism is made.

Authoritative generation uses `Random(match_seed * 1000003 + state.sequence)` per event. Snapshots therefore need no opaque PRNG serialization. Continuations use `Random(forecast_seed + sample_index * 104729)`. There is no read of future authoritative events. Forecasts simulate the same kernel through full time, returning empirical home/draw/away proportions and binomial standard errors.

## Scenarios and attribution

A scenario deep-copies the checkpoint and changes only validated intervention fields. Both baseline and branch use the same continuation seeds. The mean paired difference estimates a probability delta; standard error is the sample standard deviation of per-trial indicator differences divided by the square root of N. Branch-dependent random consumption can weaken pairing but does not change marginal correctness. Identical interventions reproduce exactly zero delta.

Forecast attribution replaces score/clock, then personnel/tactics, then possession/territory. Each contribution is the change in home-win probability between adjacent replacements with fixed simulation seeds. It telescopes to the observed change; a residual above `1e-9` invalidates reconciliation. Contributions are order-dependent and group correlated factors; they are not Shapley values or unique causal effects. Factor-level confidence intervals remain unimplemented and the output states that limitation.

## Intelligence and publication

Without configured Foundry, deterministic rules select tools and deterministic templates render facts. This is the **template baseline**, not autonomous model inference. When configured, the installed Agent Framework/Foundry adapter runs three distinct role instances with structured outputs and supervised code handoffs. The controller permits at most three planning rounds, eight tool calls and two scenario variants. Autonomous scenarios may use at most 128 continuations. A job has a 240-second execution timeout; each inference has a 30-second timeout. A timed-out inference is retried once; an invalid narrative gets one bounded repair using deterministic validation errors. Exhausted attempts return terminal failure/rejection.

Allowlisted tools retrieve pinned state context, recent events, possession statistics, window comparisons, forecast changes, prior findings and scenarios. The model cannot mutate canonical events or probabilities. Memory stores public decisions, evidence and tool results, not hidden reasoning. A new model-leading outcome can supersede an earlier finding without erasing it; otherwise a later published finding extends previous evidence. Rich hypothesis contradiction reasoning remains a next-stage task.

The independent validator checks finite values, exact state hash, match scope, numerical agreement, and event references at or before the pinned state. Arbitrary prose fields are forbidden. Published text is rendered from verified state/forecast values and an allowlisted narrative angle. This deliberately limits expressiveness until a broader verifiable claim language exists.

## Persistence, delivery and recovery

Events and snapshots are insert-only artifacts. Reusing an event/snapshot key with different content raises an error. Model changes require a model-version/migration strategy; a local development database may be intentionally rebuilt. Derived findings retain their original records. Jobs are persisted before delivery, use unique keys and a transactional conditional lease claim, and store terminal results. A relay sends pending job IDs every two seconds. Expired leases recover after five minutes; shutdown does not erase requests. Service Bus acknowledgements confirm delivery only; the database outbox re-delivers unfinished jobs. Duplicate delivery cannot acquire an active lease. Local worker recovery and deduplication are tested; cloud delivery is not.

Browser playback follows a resumable SSE replay of a fully generated immutable fixture. It is not a live external feed. Each viewer owns its playback cursor. Seeking pauses that viewer's stream and pins the historical state. Returning to live returns to the viewer's playback head, not a global stadium clock. SSE resumes by sequence/Last-Event-ID. Model jobs execute separately from playback. Two local workers and an eight-job pending limit bound work; distributed capacity planning, per-user rate limits and full operational telemetry remain pending.
