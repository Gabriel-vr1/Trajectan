#!/usr/bin/env bash
# Read-only inventory for an already authorized Azure CLI identity.
# Never logs in, provisions resources, changes roles, or prints access tokens.
set -euo pipefail
command -v az >/dev/null || { echo 'Azure CLI is unavailable. Use an authorized Azure Cloud Shell or configured server runtime.' >&2; exit 2; }
az account show --query '{subscription:name,subscriptionId:id,state:state}' --output json
az resource list --query "[?type=='Microsoft.CognitiveServices/accounts' || type=='Microsoft.CognitiveServices/accounts/projects' || type=='Microsoft.App/containerApps' || type=='Microsoft.DBforPostgreSQL/flexibleServers' || type=='Microsoft.ServiceBus/namespaces' || type=='Microsoft.Web/staticSites'].{name:name,type:type,region:location,resourceGroup:resourceGroup}" --output json
