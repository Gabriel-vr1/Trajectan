# Current final integration verification — 27 October 2026

This section supersedes historical runtime/cloud limitations recorded below. Design intent is preserved in `TRAJECTAN_MASTER_REFERENCE.md`; operational claims below come from executed requests/tests.

| Check | Actual result | Evidence |
|---|---|---|
| Runtime readiness | New configuration version, enforced restricted network, key/endpoint/model ready; no deployment identity | `evidence/runtime-readiness.json` |
| Minimal authenticated Foundry request | gpt-4.1-mini responded “Trajectan inference verified.”; 16 input + 7 output tokens | `evidence/foundry-minimal.json` |
| Native three-agent controller | All three roles, selected tools, handoffs, strict validation, **published** | `evidence/foundry-workflow.json` |
| Real HTTP API + worker + Foundry | Completed investigation at seed 26 / state 306; three real responses; `inference-observed`; SQLite/local queue explicitly reported | `evidence/foundry-api.json` |
| Local backend regression | **41 passed, 1 skipped in 10.83s** before adding two deployment-gate tests; PostgreSQL URL absent | `.venv/bin/pytest -q` |
| Frontend production build | Passed TypeScript/Vite, 590 modules; 537 kB bundle advisory | `npm run build --prefix frontend` |
| Local browser integration | **4 passed in 25.7s** | `CHROMIUM_PATH=/usr/bin/chromium npm run test:e2e` |
| Local application smoke | Passed: 347 events, state 168, published investigation, completed scenario, immutable history and verified recap; deterministic development mode | `scripts/smoke.py http://127.0.0.1:8000` |
| GitHub Actions at f9d7ef5 | **Passed**: 41 backend tests, 1 skipped; Bicep compile; production image build/start; container smoke; **4 browser tests in 18.0s** | [run 40569010910](https://github.com/Gabriel-vr1/Trajectan/actions/runs/40569010910) |
| Production image in that CI run | `sha256:4e9a0d075b88846ccf1ceca172fbc112ee554c80042b7707ae7760635546b345` | CI build log; not a published registry digest |
| Python undefined/unused checks | Passed | `ruff check backend/trajectan tests scripts evals --select F` |
| Azure local preflight | Correctly blocked: Azure CLI unavailable; readiness reports no outbound identity | `scripts/azure_preflight.py` |
| Azure hosting, deployed identity, Service Bus, private PostgreSQL | **Unverified; no paid provisioning, no public URL** | Owner's local CLI and approval gates remain |

The latest persisted successful workflow has 8,727 input and 420 output tokens across three receipts. Its exact response IDs are retained in JSON. These are real authenticated responses through the configured restricted key, not test doubles. The final verifier was rerun with persistent inference admission enabled.

## Live failures and corrections retained

- Projects' default logging transport bypassed the runtime HTTP proxy and failed direct DNS. The SDK-supported default HTTP client override fixes proxy routing while retaining TLS and restricted secret injection.
- Network-key inference uses the matching Azure OpenAI resource v1 endpoint through documented Projects `base_url` and `api_key` overrides. The native `FoundryChatClient` and real Agent Framework role instances remain in use.
- An initial real Investigation deferred a routine-looking checkpoint. `foundry-deferred.json` retains this legitimate inconclusive result. The planner now receives an explicit objective to assess the pinned development's forecast impact.
- An actual narrative omitted required claims; the unchanged strict validator rejected publication, including its bounded repair. `foundry-rejected.json` retains the receipts and errors. The Narrative instruction now explicitly requires copying every verified claim, including zero-valued metrics.
- Default sandbox network isolation stalled asynchronous API tests; rerunning with supported network permission passed. npm's default cache was unwritable; a `/tmp` cache resolved installation. No package integrity/TLS checks were disabled.
- Docker Hub and GitHub release-asset hosts are outside this runtime's network policy. Local container/Bicep downloads were not repeatedly retried. Actual Bicep/container verification was executed successfully in GitHub Actions.

## Live held-out benchmark

Template, single and multi modes used identical seeds 501–503 and matching state hashes at sequence 300. The existing template suite and live single-model suite both published 3/3 validated outputs. Multi-agent published 2/3; the remaining case was rejected during evidence review. Mean live latency was 3.829s single versus 7.765s multi. Reports are in `evidence/benchmark-single.json`, `evidence/benchmark-multi.json`, and `evals/template-baseline.json`.

This is a tiny operational comparison, not a subjective relevance assessment, real-football accuracy claim or demonstrated multi-agent advantage. A rejection may be appropriate but is not counted as publication. No improvement has been inferred from architectural complexity.

## Deployment engineering and limitations

The template compiled in CI and now proposes a smaller same-origin Container App, private PostgreSQL networking, a separate short bootstrap job creating the least-privilege app login, Service Bus Basic with narrow identity roles, and optional initially disabled Static Web Apps. Deployment scripts are staged and approval-gated; their CLI test doubles do not establish Azure API compatibility, actual quota, eligibility, capacity or successful provisioning.

The $12/72-hour proposal in `AZURE_COSTS.md` is a planning estimate subject to actual regional/account rates and owner approval, within the $15 ceiling. Managed-identity Foundry calls, cloud persistence/restart recovery, Service Bus exchange, public ingress/browser access and measured performance at 0.5 vCPU remain unverified. The cloud smoke acceptance steps are in `DEPLOYMENT.md`. A funded plan for the entire judging period is still required.

---

# Historical verification record

The records below describe earlier checkpoints and are retained for provenance. Their statements about missing runtime configuration or no live inference are superseded by the current evidence above.

# Executed verification record

Checked 27 October 2026 in the Trajectan managed cloud workspace. Results below are executed checks, not projected acceptance claims.

| Check | Command / evidence | Result |
|---|---|---|
| Backend/domain/workflow/API | `.venv/bin/pytest -q` | **28 passed**, latest full run 11.76s |
| Frontend production build | `npm run build --prefix frontend` | **Passed**, TypeScript and Vite; 590 modules |
| Browser integration | `CHROMIUM_PATH=/usr/bin/chromium npm run test:e2e` in frontend | **2 passed**, 19.1s; desktop complete journey and mobile/history/reset |
| Python undefined/unused checks | `.venv/bin/ruff check backend/trajectan tests scripts evals --select F` | **Passed** |
| OpenAPI generation | `PYTHONPATH=backend .venv/bin/python scripts/export_contract.py` and openapi-typescript 7.13.0 | **Passed**, primary event/state/forecast types generated |
| Azure template compile | Bicep 0.48.1 `build infra/main.bicep` | **Passed**, no deployment performed |
| Production container | Docker build using `infra/Dockerfile`, tag `trajectan:verified` | **Passed** |
| Container startup + workflow | `.venv/bin/python scripts/smoke.py http://127.0.0.1:8001` | **Passed**: UI served, 347 events, checkpoint 168, published investigation, completed scenario, unchanged source state, validated analyst recap |
| Synthetic evaluation | `PYTHONPATH=backend .venv/bin/python evals/evaluate.py` | **Completed**, 20 held-out synthetic fixtures, 64 continuations each; full results in `evals/results.json` |
| Current competition rules | Read Microsoft's official GitHub rules through aka.ms redirect | Deadline confirmed: 28 October 2026 08:59 SAST; video under two minutes |

## Coverage

The backend suite exercises deterministic complete matches, action legality, unique IDs, event/snapshot replay, probability normalization and final-state certainty, scenario reproducibility/no-op/isolation, intervention eligibility, attribution reconciliation, false/future/cross-match/nonfinite claim rejection, audience factual equivalence, workflow terminal states and bounded rounds, memory links, durable job claiming/recovery/deduplication/failure, immutable-record conflicts, API startup/recaps and SSE resume.

The Microsoft SDK test constructs all three actual `Agent` instances with the installed `FoundryChatClient` and checks cleanup. Fake providers in negative workflow tests are **test doubles only**, not Microsoft integration evidence. Local production traces explicitly identify deterministic execution.

Screenshots in `docs/screenshots/` were generated by the passing browser tests and inspected. The production bundle currently emits a Vite advisory about a JavaScript chunk above 500kB; the build succeeds. Further code splitting is an optimization, not a verified functional failure.

## Confirmed errors fixed during verification

- Current SDK uses `agent_framework.foundry.FoundryChatClient`; older Azure connector imports were replaced and constructor/cleanup behavior was tested.
- Immutable JSON persistence comparison now canonicalizes tuple/list serialization, so valid coordinate records are not incorrectly rejected.
- Docker source ownership was corrected for the non-root runtime user. The first startup failed on restrictive copied file permissions; the corrected image passed the real smoke workflow.
- Primary frontend response types now derive from the actual FastAPI schema. Default-valued state fields are treated as present in serialized server responses.

## External limitations

No live Foundry inference, Azure Service Bus exchange, Azure PostgreSQL connection, Azure hosting or Application Insights flow was exercised. No public deployment URL, uploaded demo video or completed submission is claimed. GitHub Actions is configured; its remote result must be checked separately from these local results.

The owner reports an existing succeeded `agentgate` project / `gpt-4.1-mini` deployment and active Azure for Students subscription. This runtime's fresh readiness check still returned no Azure credential bindings, runtime variables or outbound identities. Exact endpoint, effective authorization, network reachability and credits remain required.

`PYTHONPATH=backend .venv/bin/python scripts/verify_foundry.py` was invoked without configuration and correctly stopped with a missing-project-endpoint message. It made no inference call. After configuration, it performs actual Agent Framework execution for all three roles and validates the returned claims. Its successful real output is required before describing live Microsoft AI integration as verified.

## Subsequent engineering milestone

- **36 tests passed in 50.45s** with real local PostgreSQL enabled, covering the enhanced workflow, strict complete-claim publication, cache/config isolation, paired attribution intervals, immutable retry revisions, support/contradiction memory, SDK request/response execution with stubbed HTTP, and stale job-lease fencing.
- A further **network-key/model-alias constructor test passed** after the owner reported the new environment variable names. It verifies the SDK's documented API-key override and actual Bearer header construction using a test placeholder. It is not a cloud authentication test.
- **4 browser journeys passed in 39.5s**: full intelligence/scenario/recap flow, responsive history/reset, forward/reverse attribution with uncertainty, and late-response fixture isolation.
- Updated TypeScript/Vite build passed. OpenAPI and frontend types were regenerated.
- A real local PostgreSQL 16 integration test passed. The full application then passed `scripts/smoke.py` against PostgreSQL: 347 fixture events, checkpoint 168, published investigation, completed scenario, unchanged history, verified recap. This does not establish Azure PostgreSQL connectivity.
- The template benchmark published validated results for all **3 held-out cases**, seeds 501–503, recorded in `evals/template-baseline.json`. Real single-model and three-role benchmark modes are implemented but have not run against live Foundry.
- The latest container rebuild was blocked by the platform's automatic-approval-review usage limit and **was not executed**. The earlier successful container result applies to the previous checkpoint only.
- Runtime readiness was rechecked after the owner updated the cloud configuration. This task still reports revision 1 with no Azure variables, secret bindings or identities. The live verification command correctly stopped at `Missing FOUNDRY_PROJECT_ENDPOINT`, before any network request. See `CLOUD_HANDOFF.md` for the precise new-task procedure and header compatibility check.

## Resumed runtime verification — 27 October 2026

- Foundry live verifier: **blocked before network**, missing `FOUNDRY_PROJECT_ENDPOINT`; model alias and restricted key binding also absent. Safe evidence is retained in `foundry-runtime-check.json`. No successful live inference or cloud Agent Framework execution is claimed.
- Existing commit `6b714d4` CI run `40518657349`: Python tests and frontend build passed, browser suite failed (3 passed, 1 failed). The attribution journey clicked Half-time before events loaded, selecting state zero. Checkpoint controls now remain disabled while the fixture loads. The regression deliberately delays the fixture response and asserts both disabled controls and the eventual halftime selection.
- Updated backend suite: **37 passed, 1 skipped in 20.45 seconds**. PostgreSQL integration skipped because this run did not supply `TEST_POSTGRES_URL`. Native Agent Framework SDK tests use stubbed HTTP and establish serialization/controller compatibility only.
- Frontend TypeScript/Vite production build: passed, 590 modules. The 537 kB bundle-size advisory remains.
- Fresh production Docker build: passed, image `sha256:66650c56dea0ba5b6acdc0e781436e9f493811c38e35a08a8ce93a9a4414e07b`.
- Packaged application smoke on loopback port 8004: passed, 347 events, checkpoint 168, published validated local investigation, completed scenario, unchanged historical state and verified recap. Health truthfully reports degraded/local fallback, SQLite and local durable queue, with zero inference calls.
- Azure read-only preflight: blocked because Azure CLI is unavailable. Deployment template was reviewed; paid provisioning, identity role grants, database egress and public access are still unverified and require the documented owner inputs/approval.
- The first container browser run passed 3 journeys but timed out waiting 30 seconds for attribution. The delayed-loading assertions and halftime selection passed. A direct follow-up attribution request returned HTTP 200 in 3.18 seconds, with `verified: true` and zero reconciliation residual. Stalled sandbox test processes were stopped before repeating the browser suite; no simulation samples or correctness assertions were reduced.
- Repeat browser suite against the updated production container: **4 passed in 23.1 seconds**, including delayed fixture loading, attribution intervals/order reconciliation, all four workspaces and fixture isolation. Screenshots refreshed from this passing run.
