---
title: "TRAJECTAN | Master Project Reference & Decision Record"
subtitle: "Microsoft × Premier League — Inside the Game Developer Hackathon 2026"
author: "Project strategy and architecture reference"
date: "26 October 2026"
lang: en-GB
---

# TRAJECTAN

**MASTER PROJECT REFERENCE & DECISION RECORD**  
**Version:** 1.0  |  **Reference date:** 26 October 2026  |  **Document status:** Approved strategic direction; pre-implementation reference  
**Intended readers:** Future AI assistants, Codex/development agents, project owner, reviewers and collaborators  
**Purpose:** Provide a durable, self-contained and traceable source of truth for what Trajectan is, what has been decided, why it was chosen, and what is still to be implemented or verified.

> **Use this document as the canonical record of Trajectan's approved product and architectural intent—not as evidence that any component has already been implemented.** Competition rules remain governed by the organisers' official rules. Actual code, tests and deployment state must be established from the repository and operational evidence once development begins.

## Document navigation

1. Reading rules, authority and status labels
2. Executive project brief
3. Hackathon context, requirements and deadlines
4. Competitive landscape and differentiation
5. Product definition, audiences and scope
6. Confirmed decision register
7. Canonical user journey and functional requirements
8. System architecture and processing flows
9. Football simulation, forecasting and attribution design
10. Data architecture and interface contracts
11. Agentic intelligence and evidence verification
12. Microsoft/Azure infrastructure and operational architecture
13. UX, workspaces, visual design and interaction rules
14. Narratives, personalization and broadcast outputs
15. Security, licensing and responsible claims
16. Evaluation and acceptance criteria
17. Development execution and Codex handoff
18. Submission readiness and outstanding verification
19. AI assistant operating instructions and glossary
20. Provenance, precedence and change log

# 1. Reading rules, authority and status labels

## 1.1 Source hierarchy

Resolve conflicting information in this order:

1. **Organiser's current official rules and submission platform** govern eligibility, intellectual property, deadlines, judging and formal submission conditions. The October 9 competition reference summarizes—not replaces—the official rules.
2. **The actual project repository, automated tests, deployed infrastructure and measured results** govern implementation status, technical behaviour, coverage and demonstrable performance. No such live state is established by this document.
3. **This Trajectan master reference** governs project identity, selected product direction, feature scope, architecture and intended design, except where later explicitly amended.
4. **The 9 October 2026 competition overview/reference** captures the supplied official material and its original source citations.
5. **The 9 October 2026 execution plan** records early scheduling and workflow preferences; its historical dates and preliminary project assumptions are superseded where the later Trajectan planning conversation made explicit decisions.
6. **Earlier planning conversations, screenshots and competitor descriptions** provide context, not stronger authority than this consolidated decision record.

If a later repository or planning artefact appears inconsistent, flag the conflict rather than silently overriding it. Distinguish a documented intention from a verified implementation.

## 1.2 Status vocabulary

| Label | Interpretation | How future AI should use it |
|:---|:---|:---|
| **CONFIRMED** | Explicitly selected or subsequently approved by the project owner | Preserve unless asked to revise |
| **SELECTED—VERIFY** | Specific technology/implementation direction accepted, subject to access and compatibility | Attempt verification before implementation; do not assume deployed |
| **DESIGN DEFAULT** | Engineering detail selected for this reference to fill a noncontroversial gap | Implement when compatible, but log justified deviations |
| **TO SPECIFY** | Important low-level design or measured setting not yet locked | Choose and test during development; do not invent it as previously approved |
| **TO VERIFY** | External fact, available account resource or runtime condition not established | Inspect actual evidence before claiming it |
| **HISTORICAL** | Earlier research, competitor self-description or superseded target | Retain for provenance; do not treat as current operational fact |
| **OFFICIAL-SOURCE SUMMARY** | Summary of the supplied 9 October organiser materials | Consult current official rules if a formal compliance claim is at stake |

## 1.3 Scope of this artefact

This document is a **strategy, architecture, requirements and design memory**, designed to be useful to an AI assistant starting in a new chat with no access to the planning history. It captures decisions and fills in selected practical design defaults, while marking unsolved mathematical parameterisation, SDK compatibility and cloud access as unverified. A subsequent **Trajectan Development Specification / implementation backlog** should derive directly from this reference; it may add code-level precision but should not silently redefine the product.

# 2. Executive project brief

## 2.1 Identity and mission

**Name:** Trajectan.  
**Category:** Autonomous, Explainable Match Intelligence Platform.  
**Competition:** Microsoft × Premier League, *Inside the Game: Developer Hackathon 2026*.  
**Challenge:** “The Synthetic Match Insights Engine for Premier League Studio.”

**Mission:** Transform a coherent stream of synthetic football-match events into evolving, evidence-grounded match intelligence: probability forecasts, explanations of what changed, autonomous investigations, controlled hypothetical experiments, broadcast-ready narratives and audience-sensitive presentation.

**Operating sequence:** **Observe → Detect → Investigate → Forecast → Experiment → Verify → Communicate.** The order is a conceptual intelligence cycle, not a requirement that every event generates all seven steps. Ordinary playback should stay responsive independently of AI operations.

**Core differentiator:** A reproducible probabilistic football world is used for match event generation, outcome forecasting and intervention experiments; supervised AI agents determine what to investigate, select bounded tools, revisit evidence-linked hypotheses, verify interpretations and publish grounded explanations. A unified football-first interface exposes both the match and the actual analytical work.

**Positioning:** Neither a chatbot with football vocabulary nor a static match analytics dashboard. The intended product is a coherent, inspectable workflow for live-play, studio, broadcast, streaming, and interactive match exploration.

## 2.2 What the project must prove

A judge or user should be able to see one synthetic match development, inspect the event evidence, observe an adaptive AI investigation, see a mathematically grounded change in outcome estimates, compare a bounded tactical alternative, verify the narrative, and view a resulting broadcast/recap presentation. The result should remain useful without reading code or requiring a guided explanation from the developer.

## 2.3 Epistemic boundaries

- **Observed synthetic match events:** The events the Trajectan simulator generated and committed to its immutable record. They are not real Premier League events.
- **Model-derived statistics and probabilities:** Calculations conditional on Trajectan's stated assumptions and simulator version. They are not validated real-world win probabilities unless independent evidence supports that claim.
- **Hypothetical outcomes:** Simulated counterfactual continuations from an identified checkpoint with a declared intervention, not things that happened in the authoritative match.
- **AI interpretations:** Claims or summaries derived from evidence and explicitly verified where mechanically testable; potentially fallible and revisable.

Never collapse these categories in data, APIs, visual labels, recaps or marketing language.

# 3. Hackathon context, requirements and deadlines

## 3.1 Challenge brief — official-source summary

The supplied competition reference describes the task as creating a **new functioning AI-powered application** that processes **synthetic, football-realistic match events** into explainable match intelligence, live narratives, automated recaps, and audience-specific studio/broadcast/streaming experiences. No real Premier League match dataset or broadcast footage is supplied. The central pipeline is:

| Stage | Required product interpretation for Trajectan |
|:---|:---|
| **Ingest** | Accept reproducible synthetic events, sequence them and persist the authoritative history |
| **Interpret** | Maintain match state, statistics, tactical indicators and probabilistic forecasts |
| **Explain** | Link significant findings to specific match-state versions, evidence and model attribution |
| **Render** | Display event-aware pitch graphics, intelligence cards, timelines, overlays and recaps |
| **Personalize** | Vary presentation for meaningful audience needs without changing verified facts |

The original challenge lists optional avenues such as player tagging, pass difficulty, pressure changes, ball/shot speed, video-based auto-eventing and multilingual output; **these are not all mandatory**. Trajectan focuses on a coherent simulated-event pipeline, not unlicensed match video or full computer vision.

## 3.2 Formal judging framework — official-source summary

The provided reference reports a Stage 1 viability screen (theme fit and reasonable use of featured technology), followed by **five equally weighted criteria**:

| Criterion | Weight | Trajectan proof point |
|:---|---:|:---|
| Technological implementation | 20% | Deterministic event engine, typed contracts, tests, reproducibility, sound Azure implementation |
| Agentic design & innovation | 20% | Distinct agents, adaptive tool selection, bounded handoffs, memory and demonstrated benefit over baselines |
| Real-world impact & applicability | 20% | Credible live studio/broadcast use case, reliable operation, structured overlay outputs |
| User experience & presentation | 20% | Integrated Match Centre, usable drill-down, responsive and polished end-to-end demonstration |
| Category adherence | 20% | Entire ingest → interpret → explain → render → personalize pipeline using synthetic events |

Do not optimize exclusively for one criterion or assert that any particular architecture guarantees a prize. The supplied source describes awards including Grand Prize, Microsoft Foundry, Enterprise Solution, Multi-Agent/Orchestration and Azure Cloud Native Integration; **no prize category has been formally chosen as the sole target**.

## 3.3 Submission obligations — official-source summary

- A new, working application created within the allowed contest period.
- A brief English project pitch describing the problem, solution, audience and technology.
- A **public GitHub repository** with clear README, setup, licensing and demonstration instructions.
- A publicly hosted, genuine working **demo video strictly under two minutes** (original execution plan targets approximately 100–110 seconds).
- A working build or judge-accessible deployment/test build with free, unrestricted access through judging.
- Rights-compliant code, media, libraries and datasets; avoid unauthorized league/team trademarks, match footage and music.
- Confirm the submission portal actually records the submission, not merely that assets were uploaded.

## 3.4 Dates and time-zone interpretation

The supplied rules summary records **submission close: 27 October 2026, 23:59 PDT = 28 October 2026, 08:59 SAST (UTC+2)**. Registration opened 29 September, the event began 6 October, and registration closed 20 October 2026. Dates reflect the supplied October 9 source and should be checked against the live platform before final submission.

**Historical scheduling note:** The October 9 execution plan hoped to submit by 25 October and avoid new features after 23 October. Those were internal risk-management targets, **not organiser deadlines**; they have passed as of this reference and must not be mistaken for binding rules. The planning conversation subsequently prioritized preserving Trajectan's approved capabilities while sequencing work rationally.

## 3.5 Eligibility, data rights and uncertainty

The supplied source reports eligibility restrictions, teams of up to four, a project creation-after-registration rule, broad licensing granted to promotion entities upon submission, and third-party rights obligations. It does not conclusively establish the participant's account access, eligibility, prize selection or actual submission status. Consult the live official rules (`https://aka.ms/insidethegame/rules`) when formal confirmation is needed. This is a project reference, not legal advice.

# 4. Competitive landscape and differentiation

## 4.1 Research context

Earlier competitor research examined visible project listings/screenshots and several participant-published descriptions. Those descriptions were **primarily self-reported**; stated integrations, benchmarks, deployments and accuracy should not be treated as independently verified. The purpose was to identify crowded feature patterns and defensible opportunities, not to allege that other projects lack capabilities.

| Competitor / reference | Reported positioning and capabilities | Evidence caution / Trajectan implication |
|:---|:---|:---|
| **PULSE XI** | Synthetic match generation; ProofTrail evidence; FanDNA personalization; proposed ForkCast tactical what-ifs | At review time, active Foundry inference was not independently validated; evidence trails and scenarios alone are not differentiators |
| **Synthetic Match Insights Engine** | Six-stage pipeline, seeded replay, statistics, narratives, custom orchestrator, optional Gemini, Monte Carlo “Second Guess”, overlays | Described as working/deployed but claimed Microsoft Agent Framework and Azure adapter coverage was limited or unvalidated; build genuinely integrated Microsoft execution |
| **PitchPulse Studio** | Broadcast copilot, Narrator–Verifier pattern, telemetry receipts, spatial metrics and cues | Claimed Azure/broadcast capabilities lacked independent demonstration during review; verification alone is a crowded claim |
| **InsideLens** | Weighted factors, evidence graphs, counterfactuals, audience personas and languages including Zulu | Interpretive factor weightings do not by themselves prove causal attribution; make model-based attribution reproducible and numerically reconciled |
| **Other observed names** | MatchDesk, MatchDirector, VYBE, Shadow Match, MatchMind, and additional listings | Presence acknowledged; no robust technical-performance conclusions established here |

## 4.2 Observed competitive saturation

Synthetic replay, AI commentary, multi-agent descriptions, evidence/provenance badges, language/persona variants, forecast curves and “what-if” marketing appear in the competitive landscape. Trajectan should **not** describe any one of these features as categorically unprecedented.

## 4.3 Trajectan's differentiation hypothesis

Trajectan aims to distinguish itself through the **demonstrated integration** of: (a) coherent stateful event generation; (b) forecast-change attribution tied to an explicit probabilistic model; (c) autonomous selection of investigations and bounded scenarios; (d) structured evidentiary review and final deterministic validation; (e) longitudinal memory that can revise prior interpretations; and (f) a polished, synchronized football-first experience producing studio-ready outputs. Each component must be visible in real traces or tests.

**Competitive claim discipline:** “Novel” is a design aspiration to test, not a verified fact. The actual evidence should show that the full workflow provides insight quality or recoverability not achieved by simpler baseline configurations.

# 5. Product definition, audiences and scope

## 5.1 Audience strategy

The planning discussion deliberately rejected a forced binary decision between “fan-first” and “broadcaster-first.” Trajectan is an **intelligence engine with adaptable presentation** for studio, live broadcast, streaming, football analysts and curious supporters. A professional studio workflow is a credible showcase for impact; a clear match-centre UX makes the output accessible to nontechnical viewers. Avoid framing this as two separate products.

## 5.2 Value proposition

**User problem:** Raw match events and static metrics do not adequately explain why a development matters, how estimates changed, what alternatives could have occurred or how to communicate the story for different viewers.  
**Response:** Trajectan tracks meaningful state changes, launches focused investigations, verifies computational claims and converts results into contextually relevant visual and narrative products.

## 5.3 Approved feature inventory

These are all part of the approved complete product scope; “core slice” here describes implementation order, **not permission to silently drop later items**.

| Feature | Required observable behaviour | Evidence of completion |
|:---|:---|:---|
| Synthetic Match Engine | Coherent seeded possession-based event stream | Repeatable seeded match and validated event log |
| Live Match Centre | Score, clock, playback, pitch, forecasts, statistics, timelines | Working synchronized UI |
| Outcome forecasting | Home/draw/away probabilities updated from state | Stored model-versioned forecasts with coherent probabilities |
| Autonomous investigation | Meaningful detection, hypothesis, tool selection | Real adaptive trace including selected operations |
| Forecast attribution | Explains forecast deltas within model assumptions | Reconciled contribution result and references |
| Evidence verification | Unsupported factual/numeric claims checked or rejected | Validator reports and failure examples |
| Scenario Lab | Tactical/circumstance branches compared to baseline | Reproducible baseline/alternative outputs |
| Investigation memory | Finds, relates and revises past hypotheses | Evidence-linked investigation history |
| Evolving match narratives | Insights follow match evolution and correct prior inferences | Chronological outputs with state references |
| Broadcast graphics | Structured overlays and visual preview | Timestamped verified overlay payloads |
| Automated recaps | Half-time and full-time evidence-based synthesis | Recaps linked to match events and investigations |
| Personalization | Distinct outputs for different viewing needs | At least two meaningful audience presentation modes |
| Investigation trace | Shows genuine actions, status and evidence | Inspectable logged operations, not fabricated chain-of-thought |
| Historical exploration | Selecting past event reconstructs proper state | Consistent event/snapshot replay and time travel |

## 5.4 Non-goals and guardrails

- No requirement for proprietary real Premier League events, unauthorized footage, league branding or team assets.
- No full-fidelity player-motion physics, computer-vision extraction or giant multilingual catalogue without explicit later scope approval.
- No arbitrary AI-generated probabilities, invented tactical causality or fictitious agent execution traces.
- No vector database, Microsoft Fabric integration, Azure Event Hubs or independent microservice per analytical tool purely for feature-count optics.
- No reliance on an LLM to enforce football state validity or perform authoritative numerical computations.
- No forced agent investigation of every possession event.

# 6. Confirmed decision register

The entries below are authoritative project decisions. A “selected—verify” label means the direction was accepted while access/SDK details remain to be established.

| ID | Status | Decision |
|:---|:---|:---|
| D01 | CONFIRMED | Product identity is **Trajectan**, an autonomous explainable match intelligence platform |
| D02 | CONFIRMED | Unifying loop: observe, detect, investigate, forecast, experiment, verify, communicate |
| D03 | CONFIRMED | Balance studio, broadcast, streaming and audience-personalized experiences rather than choosing an artificial single-audience exclusion |
| D04 | CONFIRMED | One probabilistic tactical-state model underlies match generation, forecasting and interventions |
| D05 | CONFIRMED | Team + player attributes with selective spatial modelling; avoid full motion modelling |
| D06 | CONFIRMED | Possession-based sequences contain individual, event-ID-addressable football actions |
| D07 | CONFIRMED | Hybrid parameterized probabilistic mechanics; learned calibration only if evidence justifies it |
| D08 | CONFIRMED | Event sourcing with versioned snapshots; immutable events remain authoritative |
| D09 | CONFIRMED | Hybrid statistical detection and AI significance triage |
| D10 | CONFIRMED | Three specialized agents: Investigation; Evidence & Reasoning; Narrative |
| D11 | CONFIRMED | Bounded dynamic planning with an allowlisted analytical tool registry |
| D12 | CONFIRMED | Shared evidence-linked, revisable investigation memory |
| D13 | CONFIRMED | Supervised adaptive handoffs plus deterministic final validation |
| D14 | CONFIRMED | Purposeful hybrid Microsoft/Azure architecture; async investigations do not block match playback |
| D15 | CONFIRMED | Service Bus-centered async messaging; **not** a dual Event Hubs + Service Bus design |
| D16 | SELECTED—VERIFY | Microsoft Foundry for actual model inference; Agent Framework for coordination and tool use |
| D17 | SELECTED—VERIFY | Python/FastAPI, Azure Container Apps, Azure Service Bus, PostgreSQL Flexible Server |
| D18 | SELECTED—VERIFY | React/TypeScript/Vite, Tailwind with bespoke tokens, Recharts and custom pitch SVG, Azure Static Web Apps |
| D19 | CONFIRMED | Four synchronized workspaces: Match Centre, Intelligence, Scenario Lab, Broadcast & Recaps |
| D20 | CONFIRMED | Complete Intelligence Journey as primary end-to-end experience |
| D21 | CONFIRMED | Adaptive Guided Exploration: proactive prompts with no forced step sequence |
| D22 | CONFIRMED | Integrated Match Command Centre, borrowing pitch immersion and intelligence-first analytical depth |
| D23 | CONFIRMED | Adaptive editorial visual system: navy, warm off-white, restrained lime and cyan |
| D24 | CONFIRMED | At least two meaningful audience modes; content adaptation must preserve verified facts |
| D25 | DESIGN DEFAULT | SSE for server→browser match updates; adopt WebSockets only if bidirectional requirements justify them |
| D26 | DESIGN DEFAULT | Initial budgets: 8 analytical tool calls, 3 planning rounds, 2 evidence-return cycles, 2 scenario variants per investigation; tune with measurements |
| D27 | CONFIRMED | Benchmark against templates and single-LLM explanations; never fabricate test results |
| D28 | CONFIRMED | Produce one authoritative Codex handoff and use a working vertical slice before expanding |

**Decision interpretation:** At 26 October 2026 this is an approved direction and reference; it does **not** establish an existing codebase, Azure deployment, active Foundry deployment or completed submission.

# 7. Canonical user journey and functional requirements

## 7.1 Complete Intelligence Journey

Use a seeded fictional match for the principal reproducible demonstration. Avoid asserting that any particular match event or calculated percentages already exist until generated by the implemented model.

1. **Match playback** displays a new synthetic action and commits it to the event log.
2. **State and forecast update** refreshes scores, tactical indicators and home/draw/away probabilities; charts retain timestamp/version references.
3. **Significance detection** assesses deterministic candidates such as goals, red cards, unusually large probability shifts or sustained attacking patterns.
4. **Agent triage** accepts, defers or rejects investigation candidates according to novelty, evidence and available budget.
5. **Investigation** retrieves match-state context, possession windows, attribution outputs and relevant prior findings; it can adapt its tool plan.
6. **Experiment (when warranted)** applies an allowlisted tactical intervention to a historical checkpoint and requests matched baseline/scenario simulations.
7. **Evidence review** inspects the findings and can request bounded additional work.
8. **Narrative generation and validation** produces an insight, overlay or recap only when machine-verifiable content passes deterministic checks.
9. **Publication and exploration** attach the result to the unified timeline; users can open its trace, evidence, scenario or broadcast version.
10. **Continuity** links later investigations to earlier supported/contradicted hypotheses and incorporates supported developments into recaps.

The journey is **nonlinear for users** and **conditional for the engine**. A routine pass need not trigger an investigation; a failed model inference must not stall the score clock or corrupt match state.

## 7.2 Product-level behavioural invariants

- Selecting an event in the match timeline changes the pitch, selected forecast, shown evidence and context panel to the corresponding committed state version.
- While inspecting an older moment, the historical cursor must not jump to the live head on new SSE updates; provide an explicit “Return to live” action.
- Every investigation and scenario attaches to the exact state that initiated it, even if the live match progresses.
- A scenario branch is visually and structurally separate from the canonical match history.
- Suggested next actions (inspect, explore scenario, view broadcast) must be discoverable but dismissible.
- A rejected or inconclusive investigation remains inspectable but is not presented as a verified factual insight.
- Audience switching changes tone, granularity and visual emphasis, never the verified numbers or event identities.

# 8. System architecture and processing flows

## 8.1 Logical components and ownership

| Component | Owns | Does not own |
|:---|:---|:---|
| Match generator | Seeded synthetic event proposals and model transition sampling | Persisted AI narratives |
| Event application / state reducer | Validates/applies ordered events; constructs state and metrics | LLM interpretation |
| Forecast and attribution engine | Numerical projections, uncertainties, explainable factor comparisons | User-facing factual prose |
| Scenario engine | Reproducible hypothetical branches and intervention comparisons | Changes to historical source events |
| Significance detector | Statistical/football triggers and priority suggestions | Publication approval |
| Agent workflow/controller | Bounded planning, tool use, handoffs, retries and trace status | Authoritative event mutation |
| Evidence validator | Numeric integrity, provenance, assertions, schema/policy checks | Arbitrary generation of analytical findings |
| Narrative renderer | Evidence-grounded written/structured output | Probability computation |
| Persistence layer | Immutable event history, snapshots, derived objects and audit links | Changing old records without a revision record |
| Frontend | Match visibility, exploration, overlays and personalization | Determination of authoritative football state |

**Logical independence ≠ microservices everywhere.** Modules may share a codebase and deploy as a modest number of runtime roles. Domains and contracts should remain clean enough to separate workers when necessary.

## 8.2 Real-time match path

1. The generator samples an action from the current tactical state using a controlled random-number generator.
2. The backend validates action legality and commits it with an ordered match sequence number and immutable ID.
3. The deterministic reducer applies it to the match state. Periodic versioned snapshots are written as derived checkpoints.
4. Metrics and selected forecast updates are generated; a significance detector creates candidate intelligence triggers.
5. The backend streams a **versioned update** to browser clients, initially via server-sent events (SSE).
6. Triggered asynchronous investigations enter an outbox/message pathway and do not block this live path.

**Ordering note:** Wall-clock arrival order is not enough. A match-scoped monotonic sequence governs committed match-event order. Client reconnection should recover the last applied version and retrieve missed events rather than applying out-of-order update payloads.

## 8.3 Asynchronous intelligence and simulation path

1. Persist an `InvestigationRequest` (or `SimulationRequest`) referencing `match_id`, `state_sequence`, model version and request ID.
2. Deliver the queued work through **Azure Service Bus**; persist trace correlation identifiers.
3. A worker accepts the request **idempotently**, loads the pinned match state and executes its bounded tools/agent workflow.
4. Heavy forecast or intervention computation runs in a separate logical compute role or bounded worker pool where practical.
5. Persist structured outputs, provenance, validator reports and terminal investigation states.
6. Publish completion/status updates to the browser; display results at their originating match event or time.

**DESIGN DEFAULT:** Use a durable transactional-outbox pattern or equivalent recovery mechanism for the database-commit-to-Service-Bus boundary. This prevents committing a trigger without eventually queuing it and supports safe retries; it is an implementation default rather than a previously measured necessity.

## 8.4 Consistency and failure principles

- **Exactly-once *effect*, not magical exactly-once transport:** Account for at-least-once message delivery; use unique job keys, deduplication and transactional result finalization.
- **State pinning:** Agents must not silently switch to a later match-state version mid-investigation. If they need the latest state, request a distinct read and record the difference.
- **Event log priority:** Snapshots and forecast caches can be regenerated from appropriate versioned inputs; they never replace the event history.
- **Async staleness:** Late findings may be published with a “historical moment” label or suppressed as stale according to explicit policy, rather than masquerading as current analysis.
- **Reduced operation:** If Foundry or Service Bus becomes unavailable, keep match playback, event inspection and deterministic statistics functioning; indicate unavailable AI features truthfully.
- **Failure isolation:** Background queue backlog or long Monte Carlo simulations must not make the match UI unusable.

# 9. Football simulation, forecasting and attribution design

## 9.1 Selected modelling philosophy

**CONFIRMED:** A single **hybrid, transparent, parameterized probabilistic tactical-state model** drives synthetic event generation, future-match continuations and counterfactual interventions. Parameter calibration or learning is allowed only when supported by suitable data and measured validation; training on self-generated events does not establish real-football fidelity.

**TO SPECIFY IN DEVELOPMENT:** Exact coefficients, allowed parameter ranges, transition frequency, stochastic distributions, venue effects, xG approximation, edge cases and performance budgets. These must be version-controlled in code/configuration and tested, not attributed retroactively to earlier planning.

## 9.2 Match-state abstraction

Maintain at least these groups in `MatchState`:

- **Fixture and clock:** match ID, teams, current period, simulation second, score, stoppages and match phase.
- **Team profiles:** attacking/defensive quality, passing, pressing capability, transition speed, endurance and tactical settings.
- **Player profiles and live condition:** team membership, role, ability (passing/shooting/defending/pressing/pace), stamina, cards, availability and substitution status.
- **Possession and space:** current possession team/player, ball position, direction of attack, coarse pitch zones and modeled pressure.
- **Dynamic information:** recent possession patterns, fatigue, disciplinary effects, tactical adjustments, time/score context.
- **Reproducibility:** simulation/model/config versions, seeded PRNG state or equivalent reproducible random-stream index.

Stable attributes and mutable match conditions must not be conflated. The state must be sufficient to generate the next event without reading future outcomes.

## 9.3 Football event taxonomy and legality

| Class | Initial event representations | Important modelling rule |
|:---|:---|:---|
| Match control | Kickoff, period start/end, full-time | Legal period/clock transitions |
| Possession | Recovery, turnover, possession termination | Distinct possession IDs and legal handover |
| Passing | Pass attempted with success/outcome, endpoints, progressive flag | “Progressive pass” ordinarily derived from a pass, not an extra physical action |
| Pressure/defence | Press, tackle, interception, clearance, block | Modelled pressure is synthetic, not tracked defender distance |
| Chance creation | Shot attempted, location, quality and outcome | xG-like rating must be a defined model output |
| Score | Goal linked to shot/action, scorer and team | Avoid double-counting the shot and goal |
| Discipline | Foul, yellow card, red card | Enforce legal player counts and availability |
| Personnel/tactics | Substitution, role change, tactical adjustment | Validate lineup limits and permissible intervention ranges |

An event can contain typed subattributes and references rather than multiplying top-level event types for every football adjective. Events must be deterministic to reapply, even if their generation used stochastic sampling.

## 9.4 Probabilistic transitions — design default

A canonical transition step chooses legal candidate actions from state-dependent probabilities. A practical first implementation may use logistic/softmax functions whose inputs include player ability, pressure, fatigue, passing distance, zone, game phase, score and tactics. Illustrative—not finalized—passing formulation:

`P(completion | state, pass) = sigmoid(b0 + b1*passer_quality - b2*distance - b3*modelled_pressure - b4*fatigue + b5*tactical_fit)`.

Required properties:

1. Each sampled choice comes from a normalized distribution of **legal** transitions.
2. Changes in tactical settings have **trade-offs**, not an always-positive global bonus (e.g., higher press may improve high recoveries but create space if bypassed).
3. Shot-generation rates and conversion probabilities respond coherently to chance context; one recorded shot drives at most one goal.
4. Match clock, score, cards and personnel constraints remain valid throughout simulation.
5. Parameter changes and RNG seed/model version are recorded for reproducibility.
6. The implementation separates **structural football rules**, **model coefficients** and **intervenable tactical settings**; agents cannot edit the first two as experiments.

## 9.5 Forecasting

For a pinned match state at sequence `s`, run `N` sampled future continuations under the same transition model through full time. Compute:

`P(home win) = count(home final score > away final score) / N`;
`P(draw) = count(equal final score) / N`;
`P(away win) = count(home final score < away final score) / N`.

Persist `N`, seed design, model/config version, source state and sampling uncertainty; all three probabilities must lie in `[0,1]` and sum to 1 within declared floating-point tolerance. For basic Monte Carlo proportion estimates, a binomial standard error approximation may be displayed; correlated outcomes and multiple comparisons require careful interpretation. Precompute or cache only against **immutable state version + model/config + seed/sample design**, never a mutable “latest” key.

Forecast performance is to be evaluated on **held-out synthetic matches generated under declared rules**, including calibration/reliability and appropriate Brier/log loss where meaningful. Such validation establishes internal synthetic-model behaviour, not accuracy on actual Premier League fixtures.

## 9.6 Tactical interventions and scenario comparisons

Two distinct intervention classes are approved:

1. **Tactical choices:** pressing intensity, compactness, attacking directness, eligible player substitution or role assignment.
2. **Altered circumstances:** hypothetical goal, red card or injury at a stated checkpoint. These are counterfactual premises, **not tactical choices**, and must be labelled separately.

The scenario engine branches from an immutable pinned checkpoint. Compare its outcome distribution to a baseline continuation from **that same checkpoint**. Use matched or paired random-number streams when compatible with intervention mechanics to reduce variance; report confidence/uncertainty for **deltas** where feasible. Store both the original state and the intervention; neither modifies the authoritative match.

**Scenario interpretation:** Describe a difference as “under Trajectan's model, this intervention changes the simulated outcome distribution by …,” not as a proven real-world causal effect. If a scenario changes a red card or goal, ensure downstream state legality remains intact.

## 9.7 Forecast-change attribution

A high-value differentiator is explaining **why the model's forecast changed between state versions**, not merely reporting a new percentage.

**Selected methodology:** Group model inputs into interpretable explanatory families, for example scoreline/game clock, disciplinary/player availability, possession/territory indicators, tactical configuration and player-condition variables. Compute controlled factor replacement comparisons, optionally with a **Shapley-style approximation** to reduce path-dependence, using consistent Monte Carlo seeds where appropriate.

**Design contract:** Attribution returns the observed forecast delta; group contributions for the specified probability target; a **reconciliation residual**; estimation uncertainty; exact state/model references; method version; and a plain-language limitation. A tolerance violation marks the explanation provisional or unpublishable. Since the simulator is stochastic and correlated inputs can change jointly, call this **model-based forecast attribution**, not a unique causal decomposition of the real game.

**TO SPECIFY:** Exact factor partitions, reference state construction, permutation count/sample budget, confidence interval strategy, nonlinear interactions and handling of non-intervenable correlated features. Benchmarks should compare against simpler leave-one-group-out approaches; use the smallest methodology that achieves stable, defensible results.

## 9.8 Simulation and model testing

Required test classes:

- **Invariant tests:** legal clock and score transitions, player availability, team possession, pitch bounds, probabilities and unique action links.
- **Determinism:** same model + seed + inputs yields same canonical event log and final match state.
- **Event replay:** full replay equals snapshot + suffix replay, with canonical state hashes.
- **Statistical plausibility:** inspect distribution of possessions, shots, goals, cards, action locations, scoreline and tactical changes; document assumed reference ranges and their provenance.
- **Forecast calibration:** assess held-out synthetic fixtures, reliability plots and probability scoring.
- **Sensitivity:** stronger/sharper tactical settings have interpretable, bounded effects under model assumptions.
- **Scenario integrity:** identical baseline config produces approximately zero estimated difference within sampling uncertainty; divergent intervention alters only permitted settings.
- **No look-ahead:** event/window queries and forecasts at historical state `s` never use event `s+1` or later except explicitly labelled posterior analysis.

# 10. Data architecture and interface contracts

## 10.1 Immutable log and derived checkpoints

**CONFIRMED:** Event sourcing with versioned snapshots. For each match, `sequence_number` is unique and monotonic. An immutable `MatchEvent` records an action; applying its deterministic reducer transforms state `S_(n-1)` into `S_n`. A `MatchSnapshot` records `S_n` with compatible reducer/model/schema versions and a content hash. Loading a snapshot and replaying events `n+1..m` must produce the same canonical `S_m` as replaying `1..m`.

**DESIGN DEFAULT:** Store separate versioned analytical projections (forecasts, scenario jobs and narratives) rather than inserting them into the football-event log. Their own audit records can also be append-only, but an AI-generated “goal” must never be indistinguishable from a football goal.

## 10.2 Canonical contract matrix

The eight previously agreed domain contracts are listed below, with adjunct workflow objects needed for implementation. Fields describe semantics, not a frozen wire-format schema; exact Pydantic/TypeScript definitions must be finalized from this table.

| Contract | Minimum identifying fields | Main content | Hard invariant |
|:---|:---|:---|:---|
| `MatchEvent` | `event_id`, `match_id`, `sequence_number`, `schema_version` | `match_second`, period, event type, team/player, possession, positions, outcome, typed metadata, creation time | Authoritative, unique sequence; legal deterministic application |
| `PossessionSequence` | `possession_id`, `match_id` | Possessing team, start/end event IDs and times, ordered events, start/end zones, termination cause | Sequence relationships agree with events |
| `MatchState` | `match_id`, `state_sequence`, `model_version`, `state_schema_version` | Clock/score, team, player, tactic, spatial, momentum/pressure and RNG state | Sufficient for continued deterministic generation |
| `MatchSnapshot` | `snapshot_id`, `match_id`, `state_sequence` | Serialized `MatchState`, `state_hash`, `created_at`, reducer/config versions | Matches full replay under compatible version |
| `ForecastResult` | `forecast_id`, `match_id`, `state_sequence`, `model_version` | Home/draw/away probabilities, Monte Carlo `N`, seed plan, uncertainty, created time | Probabilities normalized; no future leakage |
| `ScenarioResult` | `scenario_id`, `match_id`, `source_state_sequence` | Requester origin, intervention, baseline and branch forecasts, paired-seed parameters, deltas, uncertainty | Source history unchanged; explicit hypothetical label |
| `InvestigationResult` | `investigation_id`, `match_id`, `source_state_sequence`, `trigger_id` | Hypotheses, tools, observations, evidence/forecast/scenario refs, review outcome, status, relationship links | Can terminate inconclusive; no fabricated evidence |
| `NarrativeOutput` | `narrative_id`, `match_id`, `source_state_sequence`, `type` | Verified claims, references, audience profile, structured overlay/content, validation/publishing state | Fact and model claims demonstrably supported |
| `InvestigationRequest` (adjunct) | `request_id`, `match_id`, `source_state_sequence` | Trigger, priority, budget, idempotency key, model/agent config version | Safe to retry without duplicate effects |
| `AttributionResult` (adjunct) | `attribution_id`, previous/current state refs | Target probability, contributions, residual, uncertainty, method/model version | Reconciles within declared tolerance or flags uncertainty |
| `ValidationReport` (adjunct) | `report_id`, artifact ref | Schema/numeric/provenance checks, rejected claims, result, validator version | Publication gate uses machine-verifiable result |

**Clarification:** `possession_id`, `player_id` and spatial coordinates may be nullable for appropriate control events; do not require a fictional player for half-time. `event_type` plus `metadata` must be discriminated/typed to reject invalid combinations.

## 10.3 Recommended identifiers and metadata

Use stable UUIDs for globally addressable objects and a monotonic integer for match event ordering. Every stored derived result should have `created_at` (UTC), model and relevant schema/tool version, optional correlation/trace ID, and `source_state_sequence`. Game time and wall-clock time are different fields; do not compare one as though it were the other.

## 10.4 Pitch coordinates and direction

**CONFIRMED:** Normalize the pitch to `x ∈ [0,100]`, `y ∈ [0,100]`, with an explicit attack-direction mapping per team/period. Derive coarse tactical zones from coordinates through one centralized transform. For player-centric statistics, calculate forward progression relative to the team's attacking orientation; do not assume absolute increasing `x` always means progressing toward goal. Modelled “pressure” should be explicitly described as synthetic unless based on actual defender position data.

## 10.5 Persistence and state consistency rules

- Constraints ensure `(match_id, sequence_number)` and `event_id` uniqueness, and link dependent artefacts to a valid match/version.
- Replay cannot depend on mutable external APIs, nondeterministic processing order or unfrozen model coefficients.
- Snapshots carry schema, state, model and reducer versions and cannot be loaded if incompatible without explicit migration or rebuild.
- A job referencing a superseded or missing version fails safely, rather than silently consuming whatever is current.
- Derived outputs should be revisable through **new revision records or status transitions with an audit trail**, not evidence-destructive rewrites.
- Duplicates from Service Bus are deduplicated by idempotency key and persisted completion state.

## 10.6 API contract families — implementation targets

| Family | Operations (illustrative; paths to be specified) | Key behaviour |
|:---|:---|:---|
| Matches | List/create/read fixtures; start, pause, resume, seek/replay demo | Explicit user authorization and controlled state transitions |
| Events/states | Read committed events, possession sequences, snapshots, historical state | Pagination, ordering, state version pinning |
| Forecasts | Current/historical result, forecast-change attribution | Model metadata and uncertainties |
| Investigations | List, detail, trace, evidence and relations; enqueue bounded request | Idempotent execution and status subscriptions |
| Scenarios | Validate intervention, submit simulation, compare results | Asynchronous job IDs; never mutate live source |
| Narratives | Live insights, recaps, validated overlay payloads, audience profile | Verified-output-only public endpoints |
| Streaming | Subscribe to match/version/insight updates | Event IDs, reconnection, gap recovery and backpressure |
| Ops/health | Health, readiness and observability | No accidental exposure of credentials, model prompts or private diagnostics |

**TO SPECIFY:** Exact endpoint names, query pagination, authentication and OpenAPI response schemas. Use Pydantic DTOs, generate/document a stable OpenAPI contract, and derive compatible TypeScript types rather than duplicating rules by hand.

# 11. Agentic intelligence and evidence verification

## 11.1 Roles and responsibilities

| Role | May do | Must not do |
|:---|:---|:---|
| **Investigation Agent** | Triage meaningful triggers, form bounded hypotheses, retrieve evidence, select/sequence analytics, request approved interventions | Change events, change model rules, invent numerical values |
| **Evidence & Reasoning Agent** | Review interpretations, challenge unsupported or stale statements, inspect tool data, request limited extra analysis | Self-certify invalid metrics, overwrite authoritative evidence |
| **Narrative Agent** | Explain verified findings, generate structured commentary, overlays, half/full-time recaps and tailored versions | Generate new statistical evidence or publish without validation |
| **Deterministic Workflow Controller** | Enforce budget, stage routing, retries, timeouts, terminal states, version pinning and trace correlation | Pretend to be an additional reasoning agent |
| **Deterministic Validator** | Check numeric and reference claims, schema, evidence state, publication policy | Infer unsupported football causal claims |

**CONFIRMED:** The controller is code, **not a fourth LLM agent**. Microsoft Agent Framework coordinates actual agent execution; Foundry supplies actual inference when configured. Failed cloud inference must be labelled as unavailable, not silently represented as successful production Foundry reasoning.

## 11.2 Tool registry and permissions

| Tool | Outputs | Normal permitted caller |
|:---|:---|:---|
| `get_match_state` | Pinned authoritative state, metadata/hash | Investigation, Evidence |
| `get_event_window` | Ordered events with sequences, time range, refs | Investigation, Evidence |
| `analyze_possessions` | Sequence metrics, progression, pressure indicator, event refs | Investigation, Evidence |
| `compare_match_periods` | Window definitions, verified metric deltas, sample bases | Investigation, Evidence |
| `get_forecast` | Forecast result with samples/uncertainty | Investigation; Evidence reads results |
| `explain_forecast_change` | Group attributions, reconciliation and uncertainty | Investigation; Evidence inspects |
| `simulate_scenario` | Asynchronous job and structured baseline/intervention outcome | Investigation only under budget; user-requested via app workflow |
| `compare_scenarios` | Outcome deltas, uncertainty, comparative context | Investigation; Evidence inspects |
| `get_prior_investigations` | Relevant verified/inconclusive history, evidence-linked relationships | Investigation, Evidence; Narrative reads approved summary |
| `validate_evidence` | Structured claims-check report and references | Evidence plus deterministic publication pipeline |
| `prepare_narrative` / `generate_recap` | Draft typed output referencing verified facts | Narrative Agent only |

Tools must return **structured, validated responses** with error codes, version identifiers and trace IDs. Agent textual interpretation does not overwrite tool-returned numeric fields.

## 11.3 Supervised adaptive workflow state machine

Recommended internal stages:

`candidate → queued → investigating → evidence_review → [needs_more_evidence → investigating] → narrating → validating → published`.

Terminal alternatives: `inconclusive`, `rejected`, `failed`, `cancelled` or `superseded`. `Verified` is a finding/verdict; `published` is a distinct dissemination status. Preserve actual stage transitions, timestamps, tool IDs and reasons. A bounded correction loop can return to the Investigation Agent or request narrative revision; repeat calls must respect the global tool/latency budget.

## 11.4 Initial execution budgets — configurable defaults

| Control | Initial default | Finalization rule |
|:---|---:|:---|
| Tool invocations per investigation | 8 | Measure usefulness, failures and costs |
| Investigation planning rounds | 3 | Enforce at controller, not prompt-only |
| Additional evidence/correction cycles | 2 | Terminate inconclusive/rejected when exceeded |
| Scenario alternatives per autonomous investigation | 2 | Limit sample budget and duplicate scenarios |
| Concurrent investigations per match | 2 | Tune for responsiveness/cost |
| Recoverable agent retry | 1 | Idempotent call semantics required |
| Monte Carlo continuation count | Configurable | Benchmark precision, latency and available compute |

Do not confuse the planning budget with a permission to invent evidence. When no meaningful result is supported, emit an explicit inconclusive status and an intelligible UI state.

## 11.5 Significance and prioritization

Deterministic detectors create **candidate triggers** for a goal, sending-off, major forecast revision, relevant player change, persistent territorial shift or shot/pressure pattern. A transparent priority function ranks candidates using meaningfulness, magnitude, novelty relative to prior investigations, evidence sufficiency and estimated narrative utility. The Investigation Agent can accept, defer or decline a candidate; no fixed threshold guarantees that every event gets expensive analysis.

**TO SPECIFY:** Thresholds and weights after seeded-match evaluation. Store both accepted and declined candidate reasons when practical; distinguish an AI-selected tool path from a fixed pre-scripted demo.

## 11.6 Evidence-linked investigation memory

Store structured investigation summaries, hypothesis statuses and relationships: `supports`, `contradicts`, `supersedes`, `extends`, `related_to`. Every relation names the source and target investigations plus its evidentiary basis and creation version. Conclusions may be revised; underlying football events remain immutable. On revisit, an agent should retrieve **both the prior finding and its evidence references**, verify whether assumptions still hold, and record a changed assessment rather than editing the past.

Memory is not an unrestricted transcript of hidden deliberation. Preserve externally useful structured decisions, tool calls, claims, statuses, evidence links and concise rationale, not fabricated or purported private chain-of-thought.

## 11.7 Claim-validation contract

Narrative drafts should ideally present factual claims as structured objects with `claim_type` (observed event, computed statistic, forecast, hypothetical finding, model interpretation), `value`, `units`, `event/state/forecast/scenario_refs`, `qualifiers`, and display text. Deterministic checks should at minimum validate:

- referenced records exist and belong to the stated match and state scope;
- claimed score, clock, team/player, count and event outcome agree with the log;
- probability values and forecast deltas agree with stored model output within published rounding tolerance;
- counterfactual results are labelled hypothetical and include source checkpoint;
- model-explanatory language does not assert unsupported causal certainty;
- the output conforms to a typed schema and an authorized presentation profile.

If validation fails, allow one bounded rewrite/repair path or publish a conservative deterministic fallback. **Never silently replace a failed claim with invented supporting data.**

# 12. Microsoft/Azure infrastructure and operational architecture

## 12.1 Selected stack and technology rationale

The following Microsoft/Azure choices were approved as an architecture, **not verified as provisioned or accessible**. Validate region, account quotas, pricing, SDK versions and deployment rights before treating them as ready.

| Layer | Selected technology | Operational responsibility | Status |
|:---|:---|:---|:---|
| LLM inference | Microsoft Foundry | Hosted inference for specialized agents; model usage traces and evaluations | SELECTED—VERIFY |
| Agent execution | Microsoft Agent Framework | Tools, handoffs, workflow composition and agent lifecycle | SELECTED—VERIFY |
| Backend API and live processing | Python / FastAPI | Match APIs, event application, historical reads and live updates | SELECTED—VERIFY |
| Containers | Azure Container Apps | Host API and async intelligence/simulation worker roles | SELECTED—VERIFY |
| Async queue | Azure Service Bus | Investigation and computation job delivery with retry/dead-letter handling | CONFIRMED direction; provision TO VERIFY |
| Durable state | Azure Database for PostgreSQL Flexible Server | Ordered event log, snapshots, derived artefacts and references | SELECTED—VERIFY |
| Web frontend | React + TypeScript + Vite | Integrated analytical and editorial UX | SELECTED—VERIFY |
| Frontend hosting | Azure Static Web Apps | Public browser application | SELECTED—VERIFY |
| Telemetry | Azure Monitor / Application Insights | Correlated logs, errors, latency, cost and execution visibility | SELECTED—VERIFY |
| Build/deploy | GitHub and GitHub Actions | Public source, test gates and reproducible deployment | CONFIRMED development direction |
| Optional larger-object storage | Azure Blob Storage | Media, exported reports and heavy simulation artefacts when necessary | CONDITIONAL |

Use current maintained package names and documented integration paths **after verification**. Older Microsoft documentation may use changing “Azure AI Foundry”/“Microsoft Foundry” nomenclature; exact project/endpoint/API semantics should follow the verified active SDK. The hackathon objective is real Microsoft integration, not cosmetic mentions in a README.

## 12.2 Deployment roles

**API/web role:** FastAPI service serving match state, historical reads, scenario requests and SSE; kept responsive without LLM calls on the live event path.  
**Intelligence worker role:** Service Bus consumer executing bounded Agent Framework workflow and verification.  
**Computation role:** Worker pool or job handler running forecasts and scenario comparisons, separated from LLM latency where practical.  
**Data layer:** PostgreSQL for authoritative state and derived artefacts; Blob only if justified.  
**Frontend:** Azure Static Web Apps serving Vite bundle and forwarding requests to the backend through an explicit approved configuration.

These are operational roles, not a mandate for independent repos or many network services. A modular monorepo or equivalent is acceptable.

## 12.3 Why Service Bus, not Event Hubs

**CONFIRMED:** Use Service Bus to schedule reliable investigations, simulations, retries and dead-letter handling. Synthetic football matches have relatively modest event volume; an additional Event Hubs layer was assessed as unjustified complexity for this project. The application and database handle authoritative event ordering and live streaming; **Service Bus is delivery infrastructure, not match source of truth**. This still constitutes a meaningful event-driven architecture.

## 12.4 Live updates and client reconstruction

**DESIGN DEFAULT:** SSE communicates match-head progression, intelligence job status, verified publication events and time-linked UI updates. Include a stream event ID, match ID and relevant sequence/version in notifications. On reconnect, the browser reads the last committed state version and fetches missing updates before resuming. Use WebSockets only if a genuine bidirectional low-latency interaction emerges; playback controls can begin as ordinary versioned HTTP requests.

## 12.5 Reliability, security and operations

- Use Microsoft Entra/managed identities between eligible Azure services where supported. Where credentials cannot be avoided, store them server-side in approved secret storage/environment settings; **never** in the repository, browser bundle or public logs.
- Apply least-privilege identities/roles to service clients. Restrict dashboard/admin operations separately from free judge view access.
- Queue messages should reference persisted jobs, not contain entire mutable match-state objects. Include idempotency and correlation IDs.
- Bound model request tokens, agent tool calls, simulation duration, retries and concurrent background work to avoid uncontrolled expenses.
- Expose clear health/readiness checks for API, database, queue and Foundry dependency reachability; distinguish degraded versus healthy state.
- Instrument ingest latency, forecast latency/sample size, investigation duration, queue age, rejection rate, tool failures and validation blocks.
- Deploy a reproducible seed-based mode so the demonstration remains useful even if external model latency changes. Any local or deterministic fallback must be clearly labelled, and **must not be counted as successful live Foundry execution**.
- Avoid paid cloud-resource provisioning without checking the account's quotas, spending/credits and authorization; the earlier planning instruction reserves escalation for material paid-service decisions.

## 12.6 Required pre-implementation compatibility checks

**TO VERIFY:** (1) Azure subscription and region; (2) Foundry project/resource and model deployment; (3) Agent Framework Python SDK version and supported Foundry connector; (4) token/rate limits and inference costs; (5) Service Bus tier/features and queue access; (6) PostgreSQL server permission/networking; (7) Static Web Apps↔Container Apps ingress/CORS; (8) managed identity and CI/CD credentials; (9) unrestricted judge access; and (10) actual repository/deployment ownership.

If an accepted service is unavailable, **record a justified deviation and preserve functional contracts**. Do not quietly pretend a substitute service satisfies the same Microsoft integration evidence requirement.

# 13. UX, workspaces, visual design and interaction rules

## 13.1 Governing design concept

**CONFIRMED:** A **Unified Intelligence Workspace** built as an **Integrated Match Command Centre**, retaining a visually compelling interactive football pitch (pitch-centric strength) and prominently visible explainable autonomous intelligence (intelligence-centric strength). The product uses **Adaptive Guided Exploration** rather than compulsory onboarding tours or a chatbot-first interface.

**Design references:** Official Premier League site for football identity/editorial information hierarchy; FotMob-style football timeline/visual analytics for discoverable statistics; broadcast lower-third conventions for consumable overlays. Take inspiration from interaction patterns and hierarchy only. **Do not duplicate copyrighted UI layouts, trademarked logos or unlicensed artwork.** Trajectan's original name, graphics and controls must be distinguishable.

## 13.2 Persistent application shell

Desktop navigation labels: **Match Centre | Intelligence | Scenario Lab | Broadcast & Recaps**. Keep a global fixture selector, clear match clock and selected-timestamp context. A user changing tabs should retain `match_id`, selected historical `state_sequence`, investigation focus and intended scenario checkpoint. Distinguish **LIVE** from **VIEWING HISTORICAL MOMENT** to prevent misreading old analytics as live.

## 13.3 Match Centre specification

Visual priority: (1) teams/score/clock and playback; (2) interactive pitch; (3) outcome probability trend and active intelligence; (4) unified intelligence/event timeline; (5) expand-on-demand contextual evidence. Desktop composition puts pitch and intelligence side by side, with coherent space rather than identical column widths. Small screens stack cards and move navigation into an accessible compact pattern.

**Required components and interactions:**

- **Scoreboard:** home/away placeholders or original team identities, score, period, current simulation time, playback state, seeded demo selector.
- **Pitch:** accurate aspect ratio and orientation; event markers, shot locations and selected possession paths; tooltips and keyboard-reachable event selection; no fabricated player tracking animation.
- **Forecast panel:** home/draw/away trajectory, current or selected-state point, uncertainty/sample basis on detail view, click-to-attribution.
- **Match analytics:** shots/chances, possession, progression, attacking pressure indicators with honest model labels; no static decorative chart detached from events.
- **Unified timeline:** chronological football events, forecast shifts, investigation states, evidence-validated narratives and scenario references; type distinction and filter.
- **Context panel:** selected event or investigation, observed facts, estimated metrics, evidence and actions: `View investigation`, `Explore scenario`, `View broadcast output`, `Return to live`.

## 13.4 Intelligence workspace specification

A structured **investigation explorer**, not a raw chat log. Show the question/trigger, source state, timeline of actual tool operations, bounded planning/handoffs, evidence links, forecast attribution and uncertainty, review verdict, rejected/inconclusive reasons, related/superseded hypotheses and corresponding published insights.

**Investigation Trace** displays recorded public execution events (tool names, parameters suitable to expose, durations/status and source refs). Do not display invented tool calls or private internal chain-of-thought. Selecting a supporting match event navigates to the correct historical Match Centre state.

## 13.5 Scenario Lab specification

Select or inherit an immutable checkpoint and choose from approved tactical controls: pressing, compactness, directness, role and permitted substitution. Separate a labelled **Hypothetical Circumstances** area for goal/red-card/injury premises. Validate range, player eligibility, team and time. Compare baseline and alternative side by side: win/draw/loss probabilities, relevant tactical metrics, absolute percentage-point deltas, sample counts, uncertainty, source state and assumptions. Show queue/running/completed/failed statuses. Agent-proposed scenarios and user-requested scenarios must be distinguishable.

## 13.6 Broadcast & Recaps specification

Offer verified live commentary, an explanatory insight feed, time-linked overlay preview, half-time and full-time recaps, and a presentation-profile selector. Render structured overlays as actual accessible graphics, not just JSON dumps. Support controlled export of text/structured overlays (a screenshot/image export is optional if technically reasonable). Recaps must be traceable back to selected source events, forecasts and verified investigations.

## 13.7 Visual identity and design tokens

The aesthetic is **adaptive editorial**: dark football-broadcast areas with light analytical surfaces, original Trajectan branding and precise statistics. The following hex values are **DESIGN DEFAULT tokens**, not values explicitly chosen earlier; they may be tuned for measured contrast and consistency:

| Token | Initial value | Use |
|:---|:---|:---|
| `ink-950` | `#11182B` | Midnight navy identity, header and prominent dark surface |
| `ink-800` | `#24324A` | Secondary dark surfaces and neutral text hierarchy |
| `paper-50` | `#F7F6F0` | Warm off-white editorial surface |
| `paper-100` | `#EDEBE4` | Subtle dividers and card backgrounds |
| `lime-400` | `#C9F15A` | High-attention interactive/intelligence accent |
| `cyan-500` | `#45AECB` | Supporting chart/analysis accent |
| `white` | `#FFFFFF` | Contrast on deep navy; cards where necessary |
| `danger-500` | `#CB4C55` | Warnings, negative model movements and red cards |

**Typography:** A licensed, football-inspired condensed display face for major match headings plus a highly legible sans-serif (e.g., appropriately licensed Barlow Condensed and Inter, or system-safe equivalents). Verify webfont rights if external fonts are introduced. Strong typographic hierarchy, measured spacing, contrast-compliant semantic status colours and restrained motion. **Avoid** pervasive neon/glow/glassmorphism and generic “AI dashboard” decoration.

## 13.8 Responsive and accessible interaction

- Minimum meaningful mobile access to the four workspaces; do not squash full desktop panels into unreadable columns.
- Use keyboard-reachable controls, focus indicators, ARIA labels for chart summaries and contrast-checked text/badges.
- Avoid relying on colour alone to indicate observed vs forecast vs hypothetical or positive vs negative outcomes.
- Loading, queued, empty, degraded, cancelled and error states are first-class component states.
- Respect reduced-motion preferences; animation clarifies pitch/forecast changes but must not obscure the authoritative clock or numbers.
- On time travel, clearly label selected version and allow deliberate return to current play.
- On narrative regeneration due to profile changes, reuse verified evidence rather than silently changing numerical analysis.

# 14. Narratives, personalization and broadcast outputs

## 14.1 Approved narrative products

| Output type | Trigger/source | Minimum structural requirement |
|:---|:---|:---|
| Live event commentary | Committed event or validated deterministic summary | Match time, event refs, accurate observation language |
| Significant-moment intelligence | Verified investigation | Question, finding, evidence, forecast/model qualifiers |
| Scenario explanation | Completed hypothetical experiment | Source checkpoint, intervention, baseline/branch comparison, uncertainty, prominent hypothetical label |
| Half-time recap | First-half events and verified findings | Important moments and coherent narrative with references |
| Full-time recap | Entire final event log and relevant investigations | Score/result, defining developments, revised/superseded interpretations when relevant |
| Broadcast overlay | Verified narrative/forecast | Structured placement data, headline, timestamp, metric values, refs and presentation profile |

## 14.2 Personalization rules

At least **two genuinely differentiated presentation modes** must be demonstrable: a plain-language viewer mode and a more tactically detailed analyst/studio mode. Additional audience profiles may be implemented if meaningful and validated. Profiles can change explanation depth, terminology, length, chart emphasis, pacing and locale conventions, **not factual values, match event identities, model assumptions or uncertainty**. The same validated underlying claim object should feed both modes; test factual equivalence between them.

## 14.3 Narrative quality principles

Narratives should explain **why the development matters under the model**, not merely repeat timestamps and scores. Prioritize grounded significance, balanced uncertainty and football-readable language over dramatic unsupported claims. A deterministic fallback is preferable to a confident fabrication. If a hypothesis is later contradicted, later recaps should explain the revision rather than erasing the earlier published assessment.

# 15. Security, licensing and responsible claims

## 15.1 Synthetic data and branding

Generate and clearly label fictional fixtures and player/team identities unless the user supplies licensed assets. Do not imply licensing, sponsorship, endorsement or official Premier League analysis simply because this is a hackathon associated with the Premier League. Use only authorized code, audio, imagery, trademarks, footage and datasets. Record open-source licences and attribution obligations. The actual licence choice for the repository remains a project-owner decision if not otherwise established.

## 15.2 User access and cloud safety

Judge access must be functional without personal credentials or payment. If write operations are exposed publicly, protect shared demo integrity: use demo sessions, rate limits, bounded compute budgets and/or isolated synthetic fixtures. Keep admin settings, cloud endpoints and credentials away from browser code. Logs should avoid exposing secrets or unnecessary user data.

## 15.3 Claims permitted by evidence

Use wording such as “synthetic model forecasts,” “model-attributed forecast change,” “scenario estimate under specified assumptions,” and “verified against the synthetic event log.” Avoid unqualified claims such as “accurately predicts real Premier League results,” “proves the tactical cause,” “uses live official PL data,” or “Azure/Foundry-integrated” without corresponding actual integration evidence.

# 16. Evaluation and acceptance criteria

## 16.1 Multi-layer quality plan

| Test layer | Minimum acceptance expectation | Evidence artifact |
|:---|:---|:---|
| Data and reducer | Deterministic replay, schema validation, legal actions, event uniqueness, snapshot equivalence | Automated unit/property tests and sample traces |
| Probability engine | W/D/L valid and normalized; held-out synthetic evaluation; known sample metadata | Evaluation output, reliability/Brier/log-loss report |
| Scenario engine | No authoritative history mutation; reproducible branch; correct intervention labels | Baseline/branch fixtures, checksums and comparisons |
| Attribution | Source states correct; contributions + residual reconcile; uncertainty reported | Method version, sample test cases and reconciliation metrics |
| Agent workflow | Actual Foundry/Framework use if claimed, budgets, handoffs, genuine tool choices | Correlated traces and successful failure-recovery runs |
| Verification | Known injected false numeric/event claims blocked; valid ones accepted | Negative/positive validation test report |
| Narratives | Each exposed factual claim grounded; two presentation modes numerically equivalent | Claim matrix and profile comparison tests |
| Frontend | Four integrated workspaces; historical/live cursor rules; mobile/keyboard usability | Browser E2E evidence and screenshot review |
| Reliability | Queue retry/dedup, degraded AI operation, stream resumption, stable public access | Fault-injection and deployment tests |
| Submission | Public repo, real sub-two-minute video, working URL, complete portal entry | URLs and confirmation evidence |

## 16.2 Quantitative thresholds — finalization policy

Do **not invent achieved scores**. Structural properties such as unique event sequence, no illicit historical mutation and valid probability range should have **zero allowed violating test fixtures**. Floating-point tolerances (for example probability sum and attribution reconciliation) must be defined explicitly alongside numerical method and sample size. Latency p95, attribution residual, expected agent tool count, scenario sample sizes and statistical plausibility bands are **TO SPECIFY** after local/cloud profiling. Publishing any benchmark requires the model/config version, dataset seed set, sample size, date and method.

## 16.3 Baselines for measuring agentic contribution

Run three comparable configurations on the **same held-out synthetic match/event suite**:

1. **Template baseline:** Deterministic detection and rule-based/template commentary.
2. **Single-LLM baseline:** Same input evidence, one model explanation, no adaptive investigation.
3. **Full Trajectan:** Supervised three-agent investigation, tool selection, evidence review and validated output.

Compare factual accuracy, verified evidence coverage, relevance, investigation utility, recovery from insufficient evidence, latency, token/cost footprint and narrative suitability. Report improvements and regressions fairly. A more complex agent workflow is justified only by actual benefits; if it does not improve a measured dimension, say so and investigate.

## 16.4 Judging proof package

Prepare evidence showing both functional and architectural claims: a reproducible seeded match, saved match-state and attribution records, visible adaptive agent trace, a failure/rejection example, an approved scenario comparison, two tailored presentations of the same verified evidence, a complete recap and a functioning public Azure-backed experience. Provide links and methods to reproduce, not only static slides.

# 17. Development execution and Codex handoff

## 17.1 Execution stance

**Actual coding and detailed build supervision occur in a separate Development & Progress chat/tool workflow.** This document should be attached or read there at the start. The October 9 plan advocated delegated, verifiable stages, concise checkpoints and escalation only for architecture changes, paid infrastructure, rights/licensing, removal of approved scope or material new requirements. Keep that governance approach, while recognizing its original dates are obsolete.

**Priority:** A functioning integrated vertical slice early; then deepen sophistication across all approved capabilities. Distinguish **implementation sequencing** from **permanent feature removal**. Maintain version-control checkpoints and verify the public deployment well before the final submission cutoff where feasible.

## 17.2 Recommended implementation workstreams

| Stage | Deliverable | Exit evidence |
|:---|:---|:---|
| **1. Foundation** | Repository structure, environment/config, Pydantic schemas, migrations, seed runner, automated tests, app skeleton | Clean local install and deterministic seeded playback |
| **2. Football intelligence** | Event reducer, snapshots, possessions, metrics, Monte Carlo, controlled scenarios and attribution prototype | Mathematical invariants, replay tests and usable forecast/branch API |
| **3. Agentic workflow** | Verified Foundry/Agent Framework path, Service Bus worker, evidence memory, tool registry, validator, narrative outputs | Real, observable investigation and negative-claim validation test |
| **4. Unified experience** | Four synchronized workspaces, original design system, responsive UX, overlays and meaningful personalization | End-to-end browser walk-through with historical/live state control |
| **5. Azure integration** | Container Apps, PostgreSQL, Service Bus, frontend hosting, monitoring, deployment scripts | Judge-accessible deployed app, logs, failover/recovery demonstrations |
| **6. Verification/submission** | Evaluations, README/architecture, seeded demo, pitch, video and upload | Independent reproduction and submitted URLs/confirmation |

These workstreams may overlap intentionally—especially frontend, tests and deployment. Do not wait until stage 5 to check that actual Foundry and Azure provisioning are viable.

## 17.3 Suggested codebase organization — design default

A single repository with `frontend/`, `backend/`, `tests/`, `infra/`, `docs/`, `scripts/` and `evals/` is a practical starting point. Backend modules should separate `domain`, `simulation`, `forecasts`, `attribution`, `scenarios`, `agents`, `validation`, `persistence`, `messaging` and `api`; actual naming can differ if responsibilities remain clear. Keep a seeded fixture/demo dataset and deterministic example output; generate TypeScript-facing API types from the verified backend contract. Use pinned dependencies and document tested versions.

## 17.4 Codex handoff expectations

A development agent should receive:

- This reference (version/commit hash) and the two original competition/execution documents.
- A task-specific implementation specification and repo state—not an instruction to infer past decisions from chat fragments.
- The approved constraints and acceptance criteria relevant to the current workstream.
- Explicit cloud-access assumptions, test accounts and credential-handling constraints.
- Permission to make routine code/style/library decisions while preserving contracts.
- A requirement to report implemented files, tests run and **their actual results**, deployment evidence, limitations, feature coverage and outstanding blockers.

**Escalate:** product architecture reversal, substituting fake Foundry calls for real ones, new paid services, changing competition licensing/rights, silently dropping approved capabilities or making scientifically stronger claims than tests support. **Do not escalate** every folder name, component prop or internal refactor.

## 17.5 Change-control principle

Changes to frozen decisions should use a simple amendment entry: decision ID, previous value, proposed new value, reason, evidence, trade-offs, approval and affected contracts. Update this document's version and the derived implementation specification together. Missing evidence should be marked `TO VERIFY`, not silently assumed successful.

# 18. Submission readiness and outstanding verification

## 18.1 Pending project-external checks

These matters are **not confirmed by the prior planning conversation or attached documents**:

- Current registration/team details, individual eligibility and hackathon platform submission state.
- Current organiser rules or any changes after the supplied 9 October reference.
- Exact Microsoft Foundry subscription, project, available deployed model, budget/quotas and API credentials.
- Agent Framework SDK interoperability and the supported live Foundry workflow for selected versions.
- Azure region/resource permissions, paid-service approval and free judge access for the entire judging period.
- Any organiser-provided starter event data or licensing terms not included in the supplied documents.
- Actual repository URL, commit history, local implementation, passing tests and published site/video URLs.
- Target prize-category selection or final pitch/video wording.

## 18.2 Implementation details intentionally not frozen

Low-level transition probabilities and coefficients; Monte Carlo budgets; forecast uncertainty display convention; factor partitions/attribution sample count; significance thresholds; snapshot cadence; exact schemas/endpoints; queue naming/topology; model deployment name/token budget; secure role configuration; UI typography licence verification; mobile component dimensions; and numerical performance targets. Future engineering work should **specify them carefully from the approved intent and measured environment**, without calling them historically owner-approved.

## 18.3 Submission checklist

| Deliverable | Required end condition | Current evidence in this master record |
|:---|:---|:---|
| Registration/eligibility | Account and participation confirmed | TO VERIFY |
| Public GitHub | Reachable and documented original code | NOT ESTABLISHED |
| Working project | Live judge-accessible application/test build | NOT ESTABLISHED |
| Foundry/Agent Framework | Actual model/agent trace in operational build | NOT ESTABLISHED |
| Seeded demonstration | Reproducible complete journey | PLANNED, not implemented |
| Demo video | Public, actual app, **under 2 minutes** | NOT ESTABLISHED |
| Pitch and submission form | English and complete; portal confirmation saved | NOT ESTABLISHED |
| Media and licensing | Rights/attribution reviewed | TO VERIFY |

# 19. AI assistant operating instructions and glossary

## 19.1 Instructions for any future AI using this reference

1. **Begin with the document version** and treat all `CONFIRMED` decisions as established context. Do not reopen them reflexively.
2. **Never infer that planning equals code.** Inspect the current repository, deployment and evaluations before reporting progress or promising a demo.
3. **Keep the architecture integrated.** The same model drives events, forecasts and scenarios; AI selects investigations and language, not authoritative mathematical answers.
4. **Distinguish source types:** committed synthetic action vs computed estimate vs hypothetical branch vs revisable AI interpretation.
5. **Use exact state/model/evidence references** in contracts and investigative outputs. Preserve immutable match events and deterministic reproducibility.
6. **Respect the three-agent workflow** and real Foundry/Agent Framework integration. If account access fails, document the blocker and fallback rather than overstating compliance.
7. **Preserve the complete approved capability set.** Sequence intelligently; do not simplify away Scenario Lab, investigations, verification, personalized broadcast or synchronized workspace without an explicit revision.
8. **Treat high-level stack choices as selected—verify.** Recheck current Microsoft documentation, pricing and SDK compatibility immediately before implementation.
9. **Make defensible claims.** Report results only from executed tests; never invent statistics, benchmark comparisons, agent traces or cloud integrations.
10. **Keep user communication decision-efficient.** Make routine implementation choices and surface only genuine trade-offs, changes of architectural intent, paid-service requests or materially unresolved external blockers.
11. **Update this reference deliberately** when product choices change, and retain a change log so future AI agents can reconcile competing instructions.
12. **Follow official hackathon rules over planning documents** for eligibility, dates, submission and IP matters.

## 19.2 Compact context for a new development chat

> **Project:** Trajectan, Microsoft × Premier League Inside the Game 2026 hackathon entry. **Product:** Autonomous, explainable match intelligence platform using synthetic, football-realistic possession-based event streams. **Fixed architecture:** Unified transparent probabilistic tactical-state model for event generation, Monte Carlo forecasts, forecast-change attribution and intervention simulations; immutable event sourcing with versioned snapshots; three Microsoft Foundry/Agent Framework agents (Investigation, Evidence & Reasoning, Narrative) in a deterministic bounded adaptive workflow; evidence-linked memory and independent deterministic claim validator. **Azure stack:** FastAPI + Container Apps + Service Bus for async work + PostgreSQL + React/TypeScript/Vite + Azure Static Web Apps + monitoring, with actual access/SDK compatibility to verify. **UI:** Four synchronized workspaces (Match Centre, Intelligence, Scenario Lab, Broadcast & Recaps); Integrated Match Command Centre with strong pitch and visible intelligence; adaptive guided exploration; navy/off-white editorial design with restrained lime/cyan. **Important:** No implementation/deployment is established by the planning reference; inspect repository and account. Competition asks ingest → interpret → explain → render → personalize, 20%-each rubric, public GitHub/working app and video <2 min. Use this master reference as governing design intent; current official rules outrank it for formal compliance.

## 19.3 Glossary

| Term | Meaning in this project |
|:---|:---|
| **Authoritative event** | Immutable synthetic football action committed to the per-match event log |
| **State sequence** | Integer identifying match state after committed event `n` |
| **Snapshot** | Versioned derived checkpoint allowing replay without restarting at event 1 |
| **Model forecast** | Home/draw/away estimates from simulated continuations of a given model state |
| **Attribution** | Decomposition/approximation of model forecast change across defined factor groups |
| **Scenario / intervention** | A hypothetical branch based on an explicit checkpoint and permitted altered setting |
| **Paired Monte Carlo** | Correlated baseline/intervention random streams to improve precision of estimated differences |
| **Significance trigger** | Detected candidate development worthy of possible deeper analysis |
| **Investigation trace** | Genuine recorded tool/workflow events, statuses, evidence refs and timings |
| **Evidence-linked memory** | Revisable hypothesis history referencing immutable events and analytical outputs |
| **Deterministic validator** | Code checks for match, numeric, provenance and schema validity before publication |
| **SSE** | Server-Sent Events: one-way server→browser stream suitable for live updates |
| **Graceful degradation** | Core match processing continues truthfully when model or background services fail |
| **Selected—verify** | Architecture agreed, operational integration not yet demonstrated |

# 20. Provenance, precedence and change log

## 20.1 Sources used for this consolidation

| ID | Source | Scope and limits |
|:---|:---|:---|
| **R1** | `Microsoft_Premier_League_Hackathon_Reference_v1.0(1).docx`, prepared 9 October 2026 | Competition/challenge/rubric/rights/deliverables summary of supplied official information; original citations S1–S3. Official rules retain priority. |
| **R2** | `Microsoft_Premier_League_Hackathon_Execution_Plan_v1.0(1).docx`, dated 9 October 2026 | Historical timeboxes, governance, delegation and stages; early dates are not new rules. |
| **R3** | Trajectan strategy and architecture decisions in the current project planning conversation through 26 October 2026 | Primary evidence of explicitly selected product, mathematical, agentic, Azure and UX choices. |
| **R4** | Competitor screenshots and reviewed public project descriptions discussed in project conversation | Self-reported claims and competitor positioning; not independently verified deployment/evaluation evidence. |

**Original official references preserved from R1:** Official rules: `https://aka.ms/insidethegame/rules`; registration/overview: `https://aka.ms/insidethegame`; challenge listing: `https://innovationstudio.microsoft.com/hackathons/insidethegamedeveloperhackathon/home/executive_challenges`. No new live source audit was performed solely to prepare this planning consolidation. Revisit these sources for deadline, eligibility and SDK-adjacent external facts at implementation/submission time.

## 20.2 Superseded early assumptions

- R1 (9 October) recorded **“no concept, architecture or scope selected.”** This was accurate then and is superseded by the decisions recorded here.
- R2 (9 October) set an **internal submit-by-25-October target** and a **23-October feature-freeze suggestion**. These are historical preferences, not current hard rules.
- R1 recommended **one primary audience** and avoidance of multi-agent complexity until justified. Subsequent deliberate decisions selected a flexible cross-context product and a three-agent workflow because that is central to Trajectan's differentiation. This document records that later resolution; it does not rewrite the earlier source.
- Selected Azure services do **not** establish available credentials, quotas, current SDK compatibility or deployed proof. Those remain external validation tasks.

## 20.3 Version log

| Version | Date | Description | State |
|:---|:---|:---|:---|
| **1.0** | **26 October 2026** | Consolidated hackathon context, competitive reasoning and all confirmed Trajectan strategic/architectural/UX decisions; separated approved intent, implementation defaults and unresolved checks | Canonical pre-implementation reference |

**End of master project reference v1.0.** Future amendments must update the version, decision register, relevant contract sections and the development handoff consistently.
