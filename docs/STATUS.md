# Current integration milestone — 27 October 2026

Live authenticated Foundry inference and the actual three-role Agent Framework controller now pass, including deterministic publication validation. See `evidence/foundry-workflow.json` and `VERIFICATION.md`. Earlier statements below describe historical milestones. Azure hosting, managed-identity inference, cloud PostgreSQL and Service Bus remain unverified. No paid resources were provisioned.

# Capability status and continuation handoff

This is an implemented, locally verified application checkpoint, not completion of every D01–D28 acceptance item. Approved capabilities remain in scope.

| Capability | Current evidence | Remaining work |
|---|---|---|
| Shared model, seeded events, replay | Unit tests and working fixture playback | Broader taxonomy, empirical plausibility calibration, richer player dynamics |
| Forecasts | Monte Carlo from shared transition kernel; normalized outputs and metadata | Larger held-out evaluation and performance profiling |
| Attribution | Ordered grouped replacement, exact residual reconciliation | Broader permutation/Shapley comparisons; paired intervals and forward/reverse order comparison are implemented |
| Scenario Lab | All requested tactical/circumstance control families, paired deltas, immutable history | Scenario library and more detailed spatial outcome metrics |
| Investigation tools | Allowlisted structured plans; bounded rounds/calls/scenario variants | Live model-driven tool-selection proof and quality evaluation |
| Three Microsoft roles | Actual three-role SDK request pipeline tested with stubbed HTTP; key-override and model-alias compatibility tested | **Actual Foundry access and successful inference** |
| Evidence validation | Positive/negative/provenance/nonfinite tests; publication gate | Wider typed interpretation claims; live validation of the implemented bounded repair |
| Memory | Immutable previous findings, evidence links, favored-result supersession | Basic outcome/shot hypotheses, support/contradiction links and recap revisions implemented; richer model reasoning still needs live evaluation |
| UX | Four workspaces; browser-tested history, playback, responsive layout and exports | More chart interactions, proactive novelty triage and full accessibility audit |
| Recaps/personalization | Verified deterministic half/full/checkpoint recaps; two modes share claims | Richer AI-authored but verifiable explanations |
| Durable queue | Local restart/dedup/lease/failure tests; Service Bus adapter wired | **Real Azure queue test**, cloud fault injection, retry/dead-letter operations |
| Storage | SQLite tested; PostgreSQL SQLAlchemy driver installed | Real local PostgreSQL worker/API checks passed; **Azure PostgreSQL connectivity**, migrations and dedicated production role remain |
| Hosting | Local app, container definition, Azure template | **Paid provisioning authorization or existing resources**, actual public URL |
| Observability | Public execution traces, health endpoint, job status, container stdout | Application Insights correlation, latency/cost metrics |
| Evaluation | 20-match held-out synthetic evaluation | Shared-case template/single/multi benchmark harness implemented; real single/multi results require live inference |
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

Owner update: `agentgate` / `gpt-4.1-mini` is reported deployed successfully; Azure for Students is active. Reuse that deployment. The current runtime still has no configured Azure credentials, outbound identity or project endpoint. The owner confirms $100 credits; runtime account verification remains pending. `scripts/verify_foundry.py` is ready for a real three-role integration test after server-side configuration.

See **docs/CLOUD_HANDOFF.md**: the current runtime is still on environment revision 1 despite the owner updating the published configuration. A new task on that configuration is required for actual authentication verification.
