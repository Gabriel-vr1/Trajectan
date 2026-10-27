// PAID deployment: approve the concrete estimate and what-if before applying.
// Reuse the existing resource group and Foundry resource. No subscription upgrade.
param location string = resourceGroup().location
@minLength(3)
@maxLength(24)
param prefix string
param containerImage string
@secure()
param postgresPassword string
@secure()
param appDatabasePassword string
param postgresAdmin string = 'trajectanadmin'
param foundryProjectEndpoint string
param foundryModel string = 'gpt-4.1-mini'
param foundryResourceGroup string
param foundryResourceName string
// First deploy infrastructure + bootstrap job, run it, then enable the API.
param deployApi bool = false
// Same-origin Container Apps hosting is the smallest initial deployment.
param deployStaticWebApp bool = false
param staticWebAppLocation string = 'westeurope'
@minValue(1)
@maxValue(100)
param inferenceCallLimit int = 100

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-identity'
  location: location
}
resource network 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: '${prefix}-network'
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.42.0.0/16'] }
    subnets: [
      { name: 'containers', properties: { addressPrefix: '10.42.0.0/27', delegations: [
        { name: 'containers', properties: { serviceName: 'Microsoft.App/environments' } }
      ] } }
      { name: 'postgres', properties: { addressPrefix: '10.42.1.0/28', delegations: [
        { name: 'postgres', properties: { serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers' } }
      ] } }
    ]
  }
}
resource dns 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${prefix}.postgres.database.azure.com'
  location: 'global'
}
resource dnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: dns
  name: '${prefix}-network'
  location: 'global'
  properties: { registrationEnabled: false, virtualNetwork: { id: network.id } }
}
resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' }, retentionInDays: 30, workspaceCapping: { dailyQuotaGb: json('0.1') } }
}
resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-environment'
  location: location
  properties: {
    workloadProfiles: [{ name: 'Consumption', workloadProfileType: 'Consumption' }]
    vnetConfiguration: { infrastructureSubnetId: '${network.id}/subnets/containers', internal: false }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: { customerId: logs.properties.customerId, sharedKey: logs.listKeys().primarySharedKey }
    }
  }
}
resource bus 'Microsoft.ServiceBus/namespaces@2024-01-01' = {
  name: '${prefix}-bus'
  location: location
  sku: { name: 'Basic', tier: 'Basic' }
  properties: { disableLocalAuth: true, minimumTlsVersion: '1.2', publicNetworkAccess: 'Enabled' }
}
resource queue 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: bus
  name: 'investigations'
  properties: { maxDeliveryCount: 5, lockDuration: 'PT1M' }
}
resource sender 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(queue.id, identity.id, 'sender')
  scope: queue
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39')
  }
}
resource receiver 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(queue.id, identity.id, 'receiver')
  scope: queue
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4f6a9fd2-1b19-4205-8e03-4d6969a320e3')
  }
}
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: '${prefix}-postgres'
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    administratorLogin: postgresAdmin
    administratorLoginPassword: postgresPassword
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7, geoRedundantBackup: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
    network: {
      publicNetworkAccess: 'Disabled'
      delegatedSubnetResourceId: '${network.id}/subnets/postgres'
      privateDnsZoneArmResourceId: dns.id
    }
  }
  dependsOn: [dnsLink]
}
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgres
  name: 'trajectan'
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}
var adminUrl = 'postgresql+psycopg://${postgresAdmin}:${uriComponent(postgresPassword)}@${postgres.properties.fullyQualifiedDomainName}:5432/trajectan?sslmode=require'
var appUrl = 'postgresql+psycopg://trajectanapp:${uriComponent(appDatabasePassword)}@${postgres.properties.fullyQualifiedDomainName}:5432/trajectan?sslmode=require'
resource bootstrap 'Microsoft.App/jobs@2024-03-01' = {
  name: '${prefix}-bootstrap'
  location: location
  properties: {
    environmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 120
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      secrets: [
        { name: 'admin-url', value: adminUrl }
        { name: 'app-password', value: appDatabasePassword }
      ]
    }
    template: {
      containers: [{
        name: 'bootstrap'
        image: containerImage
        command: ['python', '/app/scripts/bootstrap_postgres.py']
        resources: { cpu: json('0.5'), memory: '1Gi' }
        env: [
          { name: 'DATABASE_ADMIN_URL', secretRef: 'admin-url' }
          { name: 'APP_DATABASE_PASSWORD', secretRef: 'app-password' }
        ]
      }]
    }
  }
  dependsOn: [database]
}
resource api 'Microsoft.App/containerApps@2024-03-01' = if (deployApi) {
  name: '${prefix}-api'
  location: location
  identity: { type: 'UserAssigned', userAssignedIdentities: { '${identity.id}': {} } }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: { external: true, targetPort: 8000, transport: 'auto', allowInsecure: false }
      secrets: [{ name: 'database-url', value: appUrl }]
    }
    template: {
      containers: [{
        name: 'api'
        image: containerImage
        resources: { cpu: json('0.5'), memory: '1Gi' }
        env: [
          { name: 'DATABASE_URL', secretRef: 'database-url' }
          { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
          { name: 'FOUNDRY_PROJECT_ENDPOINT', value: foundryProjectEndpoint }
          { name: 'FOUNDRY_MODEL', value: foundryModel }
          { name: 'TRAJECTAN_INFERENCE_CALL_LIMIT', value: string(inferenceCallLimit) }
          { name: 'SERVICE_BUS_NAMESPACE', value: '${bus.name}.servicebus.windows.net' }
          { name: 'SERVICE_BUS_QUEUE', value: queue.name }
        ]
        probes: [
          { type: 'Startup', httpGet: { path: '/api/health', port: 8000 }, periodSeconds: 5, failureThreshold: 30 }
          { type: 'Liveness', httpGet: { path: '/api/health', port: 8000 }, periodSeconds: 30 }
          { type: 'Readiness', httpGet: { path: '/api/health', port: 8000 }, periodSeconds: 10 }
        ]
      }]
      // Worker/outbox processing continues without browser traffic. Do not scale
      // to zero until an independently tested Service Bus wake-up rule exists.
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
  dependsOn: [sender, receiver]
}
resource web 'Microsoft.Web/staticSites@2023-12-01' = if (deployStaticWebApp) {
  name: '${prefix}-web'
  location: staticWebAppLocation
  sku: { name: 'Standard', tier: 'Standard' }
  properties: { allowConfigFileUpdates: true }
}
output apiUrl string = deployApi ? 'https://${api!.properties.configuration.ingress.fqdn}' : ''
output webHostname string = deployStaticWebApp ? web!.properties.defaultHostname : ''
output principalId string = identity.properties.principalId
output bootstrapJob string = bootstrap.name
output serviceBusId string = bus.id
output foundryScope string = resourceId(foundryResourceGroup, 'Microsoft.CognitiveServices/accounts', foundryResourceName)
