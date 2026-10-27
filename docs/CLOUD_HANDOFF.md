# Continue from the updated cloud environment

## Runtime mismatch verified

The current task is attached to observed environment revision **1**, configuration version `cecfgver_6ae0679e51e4819a8c8d6ac79be4b746`. The latest status check reported current observations but **zero secret bindings, runtime variables and outbound identities**, with the old package-manager-only network policy. Presence-only process checks confirmed that none of `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `FOUNDRY_MODEL_DEPLOYMENT` or `TRAJECTAN_FOUNDRY_KEY` exists here. No credential value was read or printed.

The owner reports that the published environment now includes the existing `agentgate` project, `gpt-4.1-mini`, a restricted network secret, custom Azure domains and $100 Azure for Students credits. Those settings have **not been applied to this running instance**. Start a new task using that updated published environment and the existing development branch/PR. Do not recreate the application or Foundry resources.

## Authentication compatibility

The adapter accepts both `FOUNDRY_MODEL` and `FOUNDRY_MODEL_DEPLOYMENT`, defaulting to the existing `gpt-4.1-mini` deployment. Without a key binding it uses `DefaultAzureCredential`. When `TRAJECTAN_FOUNDRY_KEY` is bound, it uses the installed Azure AI Projects SDK's documented `get_openai_client(api_key=...)` override through `FoundryChatClient`. The value is passed unchanged, allowing a runtime proxy placeholder; it is never logged, included in cache keys or sent to the browser.

The installed OpenAI client sends that override as **Authorization: Bearer** to the project's `/openai/v1` API. A local constructor test verifies this exact header behavior with a non-secret test placeholder. The new task must inspect the runtime's safe secret-binding metadata to confirm injection is compatible with that header and endpoint. If the binding only injects `api-key`, adapt the SDK transport to that documented mechanism before claiming success; do not weaken the secret's domain restrictions. Whether this project's inference endpoint accepts that mechanism remains **unverified until a real request passes**.

## Execute in the new task

1. Read the cloud runtime skill and call `cloud_environment.environment_status`. Confirm the observed configuration revision, ready binding/variables, and enforced network access to the exact Foundry host. Do not print credentials or dump environment variables.
2. Fetch/check out `development/trajectan-integrated-app` and read `docs/VERIFICATION.md`. Preserve the existing commits and PR targeting `main`.
3. Install `backend/requirements-azure.txt`. Run `.venv/bin/pytest -q` (the optional PostgreSQL test needs a test database).
4. Run `PYTHONPATH=backend .venv/bin/python scripts/verify_foundry.py --output /tmp/trajectan-live-foundry.json`. This executes the **actual application controller**, three native Agent Framework roles, selected tools, independent evidence review and final validation. It creates no cloud resources. It must report `complete_workflow_verified: true` and real response receipts for all three roles before describing the integration as verified.
5. Start the app and investigate the same checkpoint. Execution-specific keys prevent an old local template result from replacing the Foundry run. Failed runs can be retried as new immutable revisions (maximum revision 2 per checkpoint/config).
6. Run `evals/agent_benchmark.py --mode single --cases 3 --output /tmp/trajectan-single.json` and then `--mode multi` on the same cases; compare to `evals/template-baseline.json`. These modes refuse to substitute local inference. Review evidence before committing any live report.
7. Use `scripts/azure_preflight.sh` only with an already authorized CLI identity to inventory regions and reusable resources. Verify the Azure subscription/credits through authorized access. Obtain explicit approval for the concrete deployment budget before provisioning the Bicep resources. No deployment approval is implied by the available credit balance.
8. After approved deployment, run `scripts/smoke.py https://PUBLIC_ORIGIN` and `BASE_URL=https://PUBLIC_ORIGIN npm run test:e2e` against actual hosting. Record the accessible URL, real inference trace, and cloud persistence/queue evidence.

## Current platform limitation

The latest Docker rebuild was not executed: automatic approval review could not complete because the platform reported a usage limit. This was not a determination that Docker was unsafe. The previous checkpoint's container smoke test remains valid for that checkpoint; the newest code still needs a fresh container build. Local edits, existing verification results and repository preservation remain available. Do not bypass the approval mechanism.

The current runtime's live verification command stopped at **missing FOUNDRY_PROJECT_ENDPOINT**, before any network request. There is no live authentication success, HTTP error, Azure deployment or public URL to report from this task.
