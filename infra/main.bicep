// Deployment template only. Running a deployment provisions PAID resources.
// Obtain owner approval, review what-if and validate subscription/region first.
param location string = resourceGroup().location
param prefix string
param containerImage string
@secure()
param postgresPassword string
param postgresAdmin string = 'trajectanadmin'
// Exact authorized egress range; loopback default deliberately permits no remote clients.
param databaseClientStartIp string = '127.0.0.1'
param databaseClientEndIp string = '127.0.0.1'
param foundryProjectEndpoint string = ''
param foundryModel string = ''

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' }, retentionInDays: 30 }
}
resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-environment'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
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
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: '${prefix}-postgres'
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    administratorLogin: postgresAdmin
    administratorLoginPassword: postgresPassword
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7 }
    network: { publicNetworkAccess: 'Enabled' }
  }
}
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgres
  name: 'trajectan'
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}
resource firewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: postgres
  name: 'approved-application-egress'
  properties: { startIpAddress: databaseClientStartIp, endIpAddress: databaseClientEndIp }
}
resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-api'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: { external: true, targetPort: 8000, transport: 'auto', allowInsecure: false }
      secrets: [{ name: 'database-url', value: 'postgresql+psycopg://${postgresAdmin}:${uriComponent(postgresPassword)}@${postgres.properties.fullyQualifiedDomainName}:5432/trajectan?sslmode=require' }]
    }
    template: {
      containers: [{
        name: 'api'
        image: containerImage
        resources: { cpu: json('1.0'), memory: '2Gi' }
        env: [
          { name: 'DATABASE_URL', secretRef: 'database-url' }
          { name: 'FOUNDRY_PROJECT_ENDPOINT', value: foundryProjectEndpoint }
          { name: 'FOUNDRY_MODEL', value: foundryModel }
          { name: 'SERVICE_BUS_NAMESPACE', value: '${bus.name}.servicebus.windows.net' }
          { name: 'SERVICE_BUS_QUEUE', value: queue.name }
        ]
        probes: [{ type: 'Liveness', httpGet: { path: '/api/health', port: 8000 }, initialDelaySeconds: 20, periodSeconds: 30 }]
      }]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}
resource web 'Microsoft.Web/staticSites@2023-12-01' = {
  name: '${prefix}-web'
  location: location
  sku: { name: 'Standard', tier: 'Standard' }
  properties: { allowConfigFileUpdates: true }
}
output apiUrl string = 'https://${api.properties.configuration.ingress.fqdn}'
output webHostname string = web.properties.defaultHostname
output principalId string = api.identity.principalId
output serviceBusId string = bus.id
