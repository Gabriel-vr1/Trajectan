# Deployment preparation

No Azure resources were created. No public app URL exists from this execution. Deployment requires authorized existing resources or explicit approval for paid provisioning.

## Local production bundle

`./scripts/dev.sh` serves the built React bundle and FastAPI from one origin on port 8000. Persistent local data defaults to `trajectan.db`. For independent test fixtures, choose a fresh `DATABASE_URL`. Do not delete an existing database containing wanted investigations.

## Container

```bash
docker build -f infra/Dockerfile -t trajectan:local .
docker run --rm -p 8000:8000 -v trajectan-data:/data trajectan:local
```

The image runs as UID 10001. Python and Node versions are pinned by major release; direct package versions and npm lockfile are committed. `backend/requirements-azure.lock` records the tested full Python environment. A proxy environment can supply its trust bundle using `--secret id=proxy_ca,src=/path/to/ca-bundle.pem`; TLS verification stays enabled and the bundle is not copied into the image.

## Azure checklist and template limits

`infra/main.bicep` describes Container Apps, Log Analytics, Service Bus, PostgreSQL Flexible Server and Static Web Apps. It is an **unapplied template**, successfully compiled locally with Bicep 0.48.1. Run `az deployment group what-if` only against an owner-approved subscription/resource group before provisioning. Region availability, quotas, price and live resource API behavior remain unverified. The template creates paid services.

Before deploying:

1. Supply an image in an authorized registry. Configure registry identity if it is private.
2. Approve the PostgreSQL connectivity design. The template permits only an explicitly supplied application egress IP range; its loopback default deliberately blocks external clients. For production prefer private VNet integration and stable egress. Do not open a global firewall to make a demo work.
3. Use a dedicated least-privilege PostgreSQL app role after initial database bootstrap; the template's bootstrap login is not a final production permission model.
4. Grant the Container App identity **Azure Service Bus Data Sender** and **Azure Service Bus Data Receiver** at the queue/namespace scope. Assign the appropriate Foundry inference role on the existing project/resource. The template does not grant broad roles automatically.
5. Supply `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL` only for a verified existing deployment. Environment-bound identities and network rules must permit the Foundry, identity, PostgreSQL and Service Bus endpoints.
6. Link the Static Web App's `/api` backend to Container Apps through the supported Standard-plan backend integration, then deploy `frontend/dist`. The config file is copied into the build. Until that link is verified, the Container App can serve both frontend and API on the same origin. Avoid CORS workarounds or browser credentials.
7. Verify `/api/health`, persistence across restart, actual Service Bus send/receive, all three Foundry roles, rejected claims, SSE reconnect, scenario results and two browser audience modes.
8. Record actual URLs and role/inference traces in `docs/VERIFICATION.md`. Keep judging access available through the official judging period.

The default worker runs in the API process as a separate asynchronous execution path. For larger deployments extract the same durable job handler into a dedicated worker role and add database migrations, lease heartbeats and operational telemetry before scaling. One Container App replica is configured in the template deliberately.

The public demo currently allows bounded anonymous computational requests. Add shared rate limiting and session quotas before exposing costly inference. Queue limits alone do not protect a paid model endpoint from sustained usage.

## Existing Foundry project supplied by the owner

The owner confirmed project **agentgate**, model deployment **gpt-4.1-mini**, deployment status **Succeeded**, and an active **Azure for Students** subscription. Credits, project endpoint, effective inference authorization and connectivity have not been verified by this runtime. Reuse this deployment; no additional Foundry project or model resource is needed for the implemented adapter.

The exact endpoint must be copied from the existing project's configuration (the project name alone does not establish its resource hostname). Configure it as `FOUNDRY_PROJECT_ENDPOINT`, set `FOUNDRY_MODEL=gpt-4.1-mini`, and bind an authorized managed/workload identity to the server. Permit the exact Foundry/identity hosts in the managed environment's network policy. Do not put credentials in chat, GitHub or frontend variables.

After binding the identity and endpoint, execute:

```bash
.venv/bin/pip install -r backend/requirements-azure.txt
PYTHONPATH=backend .venv/bin/python scripts/verify_foundry.py
```

This opt-in script performs real Agent Framework calls through Foundry for all three roles and independently validates the resulting claims. It uses the existing model quota and creates no cloud resources. Until this command succeeds against the real endpoint, only SDK compatibility—not live Agent Framework execution—is established. Then run a normal application investigation and retain its real trace to verify the controller integration too.
