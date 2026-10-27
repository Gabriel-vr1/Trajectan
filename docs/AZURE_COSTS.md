# Azure deployment proposal — approval required

Prepared 27 October 2026. **No paid infrastructure has been provisioned.** The existing $15 project ceiling is not an Azure spending cap. Subscription credits, service eligibility, allowed regions and current regional prices cannot be independently checked here: this runtime has neither Azure CLI nor an Azure deployment identity.

## Concrete initial configuration

`infra/main.bicep` proposes the following in the existing `rg-trajectan-hackathon`, initially `spaincentral` **only if the subscription's policy, SKU availability and quota checks pass**:

| Resource | Configuration | Planning allowance for 72 hours (USD) |
|---|---|---:|
| Container Apps | Consumption workload profile, one replica, 0.5 vCPU / 1 GiB; serves UI and API | $3.90 |
| PostgreSQL Flexible Server | B1ms, PostgreSQL 16, 32 GiB, no HA, 7-day local backup | $2.20 |
| Service Bus | Basic namespace, one queue, managed identity, no local keys | $0.10 |
| Private networking | VNet, delegated subnets, PostgreSQL private DNS, managed public ingress IP allowance | $0.60 |
| Log Analytics | 30-day retention, requested 0.1 GiB/day ingestion cap | $1.00 |
| Existing Foundry | No new model/project; 100 persisted request admissions, 60,000-byte input ceiling, 1,200 output-token limit | $3.00 |
| Bootstrap job | 0.5 vCPU / 1 GiB, manual, 120-second timeout, zero retries | $0.05 |
| Contingency | Small traffic/rounding/regional-rate differences | $1.15 |
| **Proposed approval amount** | **First 72 hours only** | **$12.00** |

**Reserve the remaining $3 of the $15 ceiling.** Do not deploy if the actual account/regional quote, existing project spend plus this estimate, or required substitutions exceed the ceiling. The allowance assumes a small demo, modest outbound traffic, no premium services, no NAT gateway/private endpoints, no registry charges, no separately paid frontend, and no unrelated project resource consumption. It does not assume any free grants remain.

These are conservative **planning allowances, not an authenticated Azure quote**. Container Apps calculation uses $0.000024/vCPU-second and $0.000003/GiB-second: 259,200 × (0.5 × 0.000024 + 1 × 0.000003) = $3.888 before grants. PostgreSQL allowance assumes compute up to $0.025/hour plus 32 GiB storage/backup allowance; actual Spain Central rates and B1ms availability must be checked. Foundry allowance assumes at most approximately 60,000 input tokens plus schema/instructions and 1,200 output tokens per admission, at approximately $0.40/$1.60 per million tokens; **the existing model's deployment type and actual Azure rates must be confirmed**. Byte bounds are deliberately conservative. Failed requests consume admissions; SDK automatic retries are disabled.

Reference sources checked during preparation:

- [Container Apps pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/) and [billing](https://learn.microsoft.com/azure/container-apps/billing). Free monthly grants are subscription-wide and must not be assumed unused.
- [PostgreSQL Flexible Server pricing](https://azure.microsoft.com/en-us/pricing/details/postgresql/flexible-server/).
- [Service Bus pricing](https://azure.microsoft.com/en-us/pricing/details/service-bus/).
- [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/) and the existing deployment's portal quote.
- [Container Apps networking](https://learn.microsoft.com/azure/container-apps/vnet-custom): /27 Container Apps subnet; separate delegated PostgreSQL subnet. No NAT gateway or private endpoint is requested.

## Cost and security decisions

The optional Standard Static Web App stays disabled initially. Container Apps already serves the built frontend at the same origin. This preserves all four workspaces and avoids a second paid host/backend link. Separate Static Web Apps hosting remains a selected deployment option, not a verified integration. Enabling it requires an updated estimate and approval.

The API remains at one replica so the durable outbox and queue consumer continue without browser requests. Scale-to-zero is deferred until an actual Service Bus wake-up path has been implemented and tested. Reducing the always-on replica from 1 vCPU/2 GiB to 0.5 vCPU/1 GiB needs a deployed load/latency smoke check; local unrestricted CPU results do not prove that cloud performance.

PostgreSQL has no public firewall access. A short manual job creates a non-superuser application login inside the private network; API secrets contain only that login. The administrator password is confined to the bootstrap job's secret. The Container App receives queue-scoped Sender/Receiver roles and a project-scoped Foundry User role. No subscription Owner role or Foundry key is given to the app. Managed-identity inference remains unverified until deployment; successful runtime key inference does not prove that role assignment works.

The inference allowance is persisted atomically in PostgreSQL and does not reset on restart, retry revision or model reconfiguration. It bounds model request admissions, not total Azure bills or anonymous simulation/HTTP/egress charges. Keep the database; deleting it would also delete the allowance history. Review cost and application health regularly and stop paid runtime before the approved period expires. Azure billing can lag, so do not wait until a displayed bill reaches $15.

**The 72-hour proposal does not fund the entire judging period.** Confirm required judge-access dates and obtain a revised funded plan before extending hosting. Stopping/deleting resources is not authorized by this document. Preserve PostgreSQL data and the existing Foundry resource; do not delete the shared resource group.

## Approval gate

Review the exact template, both phases of `deploy_azure.py plan`, private parameters, subscription, region, registry image digest, role scopes and actual pricing. Owner approval must cover the $12/72-hour configuration before `apply`. No approval has been inferred from the available $100 credit balance or from preparing these files.
