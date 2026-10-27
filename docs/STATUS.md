# Capability status and continuation handoff

This is an implemented, locally verified application checkpoint, not completion of every D01–D28 acceptance item. Approved capabilities remain in scope.

| Capability | Current evidence | Remaining work |
|---|---|---|
| Shared model, seeded events, replay | Unit tests and working fixture playback | Broader taxonomy, empirical plausibility calibration, richer player dynamics |
| Forecasts | Monte Carlo from shared transition kernel; normalized outputs and metadata | Larger held-out evaluation and performance profiling |
| Attribution | Ordered grouped replacement, exact residual reconciliation | Factor uncertainty intervals, permutation/alternative-method comparisons, alternative group order visual comparisons |
| Scenario Lab | All requested tactical/circumstance control families, paired deltas, immutable history | Scenario library and more detailed spatial outcome metrics |
| Investigation tools | Allowlisted structured plans; bounded rounds/calls/scenario variants | Live model-driven tool-selection proof and quality evaluation |
| Three Microsoft roles | Installed SDK constructors, strict schemas, real adapter code, cleanup test | **Actual Foundry access and successful inference** |
| Evidence validation | Positive/negative/provenance/nonfinite tests; publication gate | Wider typed interpretation claims; live validation of the implemented bounded repair |
| Memory | Immutable previous findings, evidence links, favored-result supersession | Rich supported/contradicted hypotheses and narrative revision synthesis |
| UX | Four workspaces; browser-tested history, playback, responsive layout and exports | More chart interactions, proactive novelty triage and full accessibility audit |
| Recaps/personalization | Verified deterministic half/full/checkpoint recaps; two modes share claims | Richer AI-authored but verifiable explanations |
| Durable queue | Local restart/dedup/lease/failure tests; Service Bus adapter wired | **Real Azure queue test**, cloud fault injection, retry/dead-letter operations |
| Storage | SQLite tested; PostgreSQL SQLAlchemy driver installed | **Real PostgreSQL test**, migrations, dedicated app role |
| Hosting | Local app, container definition, Azure template | **Paid provisioning authorization or existing resources**, actual public URL |
| Observability | Public execution traces, health endpoint, job status, container stdout | Application Insights correlation, latency/cost metrics |
| Evaluation | 20-match held-out synthetic evaluation | Single-LLM versus full-agent benchmark with live inference |
| Submission | README, working UI, evidence images, demo script | License decision, registration confirmation, real public video and portal submission |

## Next execution sequence

1. Configure an authorized Foundry project endpoint, model deployment, Azure identity and outbound access. The current managed environment has none configured. Exercise all three roles; retain actual successful and rejected traces. Do not describe SDK construction as live inference.
2. Run the template/single-model/three-role comparison on the same evidence cases and report measured results. Evaluate the bounded retries/repair and enrich hypothesis revision based on the findings.
3. Verify existing PostgreSQL and Service Bus resources, or obtain approval for a concrete costed deployment. Validate the Bicep template, networking and least-privilege roles. No paid resources may be provisioned without the user's explicit approval.
4. Publish the production build to approved Azure hosting, run browser tests against the public URL and record evidence.
5. Record and upload a genuine video under two minutes, finalize licensing and the pitch, and confirm the portal submission.

## Local continuation

Repository `/workspace/Trajectan`, development branch `development/trajectan-integrated-app`, PR target `main`. Start with README and verification record. `scripts/dev.sh` starts the whole app. Unit/API tests: `.venv/bin/pytest -q`. Browser tests require the running app and Chromium. `docs/openapi.json` and generated frontend contracts should be regenerated together after DTO changes. The `.env.example` file contains placeholders only.

Never change synthetic model coefficients under the same published model version after this checkpoint. Persisted event/snapshot conflicts deliberately fail rather than silently replacing match history. Use a migration or explicitly separate development database when updating the model.

Owner update: `agentgate` / `gpt-4.1-mini` is reported deployed successfully; Azure for Students is active. Reuse that deployment. The current runtime still has no configured Azure credentials, outbound identity or project endpoint. Remaining credits are unverified. `scripts/verify_foundry.py` is ready for a real three-role integration test after server-side configuration.
