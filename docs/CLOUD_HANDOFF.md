# Final integration handoff — 27 October 2026

Continue from branch `integration/final-microsoft-deployment`, based on merged `main` commit `4405db45fa84307bb0b7942d5264db772cdfe86a`. Read the committed **TRAJECTAN_MASTER_REFERENCE.md** (approved design intent), **VERIFICATION.md**, **DEPLOYMENT.md**, and **AZURE_COSTS.md**. Preserve the existing application.

## Actual runtime and Microsoft integration

The new runtime uses configuration version `cecfgver_6ae0c6df96b0819a8a0ae09323b299b0` (spec revision 1). Unlike the prior runtime, observations are current, network enforcement is active, and the Foundry endpoint/model variables and restricted key binding are **ready**. Revision number alone does not establish that configuration is stale.

A genuine authenticated Responses API call to the existing `gpt-4.1-mini` returned **Trajectan inference verified.**, response `resp_02a9df0bdf17add1016ae0f8252d0081948ad09d6ee9f37882`, 16 input + 7 output tokens. The key remains restricted to `agentgate-foundry-gvr0710.openai.azure.com`.

The native Microsoft Agent Framework 1.23.0 / Foundry 1.15.0 workflow executed Investigation → selected analytical tools → Evidence & Reasoning → Narrative → deterministic validation → **published**. The latest verifier reports both `live_inference_observed: true` and `complete_workflow_verified: true`. `docs/evidence/foundry-workflow.json` contains genuine receipts, token usage, timings, tools, handoffs, verified claims and validation. `foundry-api.json` additionally records actual HTTP API/worker execution if present.

Two concrete compatibility fixes were required:

1. Resource API keys use the matching Azure OpenAI v1 endpoint. Azure AI Projects documents both `api_key` and `base_url` overrides; the existing Foundry adapter now uses those while preserving native `FoundryChatClient`/`Agent` execution.
2. Projects' default custom logging transport attempted direct DNS and bypassed the required proxy. Its documented `http_client` override now supplies OpenAI's default asynchronous client, preserving proxy routing, network-secret injection and TLS verification.

Real triage deferral and narrative rejection evidence are retained separately. The Narrative instruction was clarified to copy the complete verified claim set after the deterministic validator correctly rejected omitted facts. Validation requirements were not relaxed.

## Verification and spending protection

Local regression: **41 passed, 1 skipped** (PostgreSQL URL absent). TypeScript/Vite build and **4 browser journeys** pass. Native SDK serialization tests use stubbed HTTP and remain distinct from the real inference reports. Local smoke uses SQLite/local queue and truthfully reports development fallback. See VERIFICATION.md for final CI/container evidence.

The live three-case benchmark published 3/3 validated single-model outputs and 2/3 multi-agent outputs; one multi-agent review rejected evidence. This small test does not demonstrate an advantage for the multi-agent system. State hashes match the template suite.

Public Azure configuration includes a persistent global 100-request inference admission allowance, 60,000-byte input bound, 1,200 output-token limit and zero SDK automatic retries. Admissions survive process restarts/configuration changes and are not refunded on failure. This does not enforce an Azure spending cap.

## Deployment route and unresolved gates

This runtime has **no Azure deployment identity, no identity manifest and no Azure CLI**. The user's authenticated local CLI is the deployment route. No paid resources have been created; no public URL exists.

The prepared template uses the existing resource group, a Consumption Container App (one 0.5-vCPU/1-GiB replica serving UI/API), Service Bus Basic, private PostgreSQL B1ms/32 GiB, private DNS/VNet, narrow managed-identity roles, Log Analytics and a short bootstrap job creating the application database role. Separate Standard Static Web Apps remains optional and initially disabled. The existing Foundry project/model is reused.

Review the **$12 / first 72 hours** estimate, leaving $3 reserved within the owner's $15 ceiling. Actual Azure for Students policy/region/SKU/quota eligibility and current account prices still require local CLI/portal verification. Resource-group location does not prove service eligibility. The judging period beyond the initial 72 hours needs a funded plan. No financial approval has been inferred merely from the credit balance.

Executable sequence, detailed in DEPLOYMENT.md:

```text
python scripts/azure_preflight.py --output azure-preflight.local.json
python scripts/deploy_azure.py plan --subscription YOUR_SUBSCRIPTION_ID --parameters trajectan.local.json
```

Only after reviewing the concrete configuration, actual quote and obtaining financial approval:

```text
python scripts/deploy_azure.py apply --subscription YOUR_SUBSCRIPTION_ID --parameters trajectan.local.json --approved-estimate-usd 12 --approved-hours 72
python scripts/smoke.py https://ACTUAL_ORIGIN
```

Supply a tested public container image by immutable digest and private local secure parameters. Apply waits for bootstrap success before exposing the API, then assigns project-scoped Foundry User and deploys the app. Managed-identity inference, Service Bus send/receive, Azure persistence across restart, public browser tests and performance at the smaller CPU allocation remain unverified until deployment. Do not replace those checks with local results.

Local Docker builds are blocked by the current network policy's Docker Hub denial, and GitHub release-asset downloads are also blocked. Do not bypass the proxy or weaken TLS. GitHub Actions can compile Bicep and build/test the container using its own permitted runner environment; consult the exact commit's CI evidence.
