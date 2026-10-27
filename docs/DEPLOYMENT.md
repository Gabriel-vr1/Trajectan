# Reproducible deployment

Real runtime inference and three-agent execution are verified; Azure hosting is **not deployed**. Read [cost proposal](AZURE_COSTS.md) before paid provisioning. The scripts never log in, upgrade the subscription or copy the runtime's restricted key to Azure.

## Existing production bundle

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements-azure.txt
npm ci --prefix frontend
npm run build --prefix frontend
PYTHONPATH=backend .venv/bin/uvicorn trajectan.api:app --host 0.0.0.0 --port 8000
```

Without Foundry configuration, this is clearly labelled deterministic development mode. Variables are read from the server process; `.env` files are not loaded automatically.

## Verify existing Foundry

With the environment's existing non-secret endpoint/model and restricted key binding:

```bash
PYTHONPATH=backend .venv/bin/python scripts/verify_foundry.py --output live-foundry.local.json
```

The real `FoundryChatClient` and three `Agent` objects use Azure AI Projects' documented `api_key`, `base_url` and `http_client` overrides. Key mode derives the matching HTTPS Azure OpenAI resource host from the project endpoint, uses the v1 Responses API, and preserves the inherited proxy and TLS trust. The Projects default custom logging transport bypassed the runtime proxy; the supported default OpenAI HTTP client resolves that failure. Keys remain server-side and are never logged. Entra mode remains available for the deployed managed identity.

Successful evidence is in `docs/evidence/foundry-workflow.json`. Rejected, deferred and transport-failure runs are also retained; they must not be presented as published success. The final deterministic validator has not been weakened.

## Build and publish the image locally

This runtime cannot download Docker Hub images under its restricted network policy. GitHub Actions builds and smoke-tests the production image. With Docker available on the owner's workstation:

```bash
docker build -f infra/Dockerfile -t PUBLIC_REGISTRY/trajectan:COMMIT_SHA .
docker push PUBLIC_REGISTRY/trajectan:COMMIT_SHA
docker inspect --format='{{index .RepoDigests 0}}' PUBLIC_REGISTRY/trajectan:COMMIT_SHA
```

The final GitHub Actions run also uploads `production-image-and-template` with `trajectan-image.tar.gz` and the compiled template. Download that artifact and use `docker load --input trajectan-image.tar.gz` to reuse the tested image; tag it for your authorized registry and push it, then record its resulting registry digest. The CI image ID is not a registry manifest digest.

Choose an existing authorized registry and make the **image readable by Azure**, or separately review registry authentication and its costs. The deployment script requires the tested public image's `@sha256:` digest. It does not create a registry or turn on an admin registry account. A public source repository does not imply its GHCR package is public.

For builds in a managed proxy environment, mount the CA using `--secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt`. Keep TLS verification enabled. The non-root image runs as UID 10001; database state belongs in PostgreSQL for cloud deployments.

## Authenticated local Azure CLI — read-only checks first

These commands work from the repository with Python 3 and the user's already authenticated Azure CLI, including Windows PowerShell (`python` may be `py -3`). Do not assume that this Codex runtime shares the user's local identity.

```text
az account show --query "{name:name,id:id,state:state}" --output json
python scripts/azure_preflight.py --resource-group rg-trajectan-hackathon --location spaincentral --output azure-preflight.local.json
az resource list --resource-type Microsoft.CognitiveServices/accounts --query "[].{name:name,resourceGroup:resourceGroup,region:location}" --output table
```

Review inherited subscription/resource-group policies, allowed locations, Container Apps quota, provider registration, PostgreSQL B1ms SKU/capacity and exact existing Foundry resource group. Resource-group location alone proves no service eligibility. Missing permissions or unsupported checks are recorded as unverified, not success. Preflight never auto-registers providers, logs in, changes roles or provisions resources.

If required providers/CLI extensions are absent, install/register only the named prerequisites in the approved account; then repeat the affected read-only checks. The remote ARM validation/what-if gate must pass. Do not region-hop or upgrade the subscription to work around an eligibility failure without review.

## Private deployment parameters and plan

Copy `infra/parameters.example.json` to `trajectan.local.json` using your editor or OS copy command. Populate the actual image digest, existing Foundry resource group, and two distinct strong database passwords. Keep `deployApi` and `deployStaticWebApp` false in the input. This file is gitignored; restrict its file permissions and never attach or publish it. Azure receives passwords only through secure parameters, with no literal credentials in shell command arguments.

Use the subscription ID returned by the read-only account command:

```text
python scripts/deploy_azure.py plan --subscription YOUR_SUBSCRIPTION_ID --parameters trajectan.local.json
```

This runs ARM validation and both infrastructure/API what-if phases without creating resources. Review the [concrete $12 / first 72 hours proposal](AZURE_COSTS.md), actual regional/account prices and what-if outputs with the owner before applying. The estimate must fit the remaining portion of the $15 project ceiling.

## Apply — only after explicit financial/configuration approval

```text
python scripts/deploy_azure.py apply --subscription YOUR_SUBSCRIPTION_ID --parameters trajectan.local.json --approved-estimate-usd 12 --approved-hours 72
```

Stages:

1. Create the Consumption environment, VNet/delegated subnets, private DNS, PostgreSQL B1ms/32 GiB, Service Bus Basic queue, narrow queue roles, managed identity, capped Log Analytics and manual bootstrap job.
2. Execute the bootstrap job inside the VNet and require confirmed success. It creates `trajectanapp` with only database/schema access. The API is not exposed before bootstrap succeeds.
3. Assign Foundry User (`53ca6127-db72-4b80-b1b0-d745d6d5456d`) at the **existing agentgate project's scope**. Confirm this scope against your account's actual project resource.
4. Deploy the single API/frontend replica with application database credentials, managed identity, existing model and a persistent 100-call inference admission limit. This is an application limit, not an Azure billing cap.

RBAC propagation may take time. If an actual Azure error occurs, retain sanitized evidence, diagnose that failure and avoid blindly repeating the deployment. No automated deletion or destructive rollback is included. A partial failed deployment can still accrue charges.

## Deployment acceptance — actual origin required

The script prints the Container Apps origin only after ARM deployment. Then run:

```text
python scripts/smoke.py https://ACTUAL_ORIGIN
```

```bash
BASE_URL=https://ACTUAL_ORIGIN npm run test:e2e --prefix frontend
```

PowerShell equivalent:

```powershell
$env:BASE_URL = 'https://ACTUAL_ORIGIN'
npm run test:e2e --prefix frontend
```

Also inspect `/api/health` and a real investigation trace: require PostgreSQL connectivity, Service Bus send/receive, successful managed-identity inference for all three roles and passed publication validation. Verify the investigation survives a replica restart; test SSE resume, scenarios and both narrative profiles. `configured-unverified` is not cloud integration success. Adaptive agents may legitimately defer/reject a checkpoint; distinguish this from transport/authentication failure.

Record the actual URL, deployment IDs, image digest, smoke results and queue/database/identity evidence in `docs/VERIFICATION.md`. Cloud failures, performance at 0.5 vCPU and restart persistence remain unverified until these checks execute. Keep judging access available for the required period under a separately confirmed funded plan; the initial 72-hour estimate alone does not establish this.

Separate Static Web Apps remains optional and disabled in the initial proposal. Its Standard-plan backend linkage and frontend publication need additional verification and approval before any claim of successful SWA hosting.
