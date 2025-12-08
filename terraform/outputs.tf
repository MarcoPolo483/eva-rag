output "app_service_url" {
  description = "URL of the deployed App Service"
  value       = "https://${azurerm_linux_web_app.eva_rag.default_hostname}"
}

output "app_service_name" {
  description = "Name of the App Service"
  value       = azurerm_linux_web_app.eva_rag.name
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.eva_rag.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.eva_rag.name
}

output "cosmos_db_endpoint" {
  description = "Cosmos DB endpoint"
  value       = azurerm_cosmosdb_account.eva_rag.endpoint
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.eva_rag.vault_uri
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.eva_rag.instrumentation_key
  sensitive   = true
}

output "app_service_identity_principal_id" {
  description = "Principal ID of the App Service managed identity"
  value       = azurerm_linux_web_app.eva_rag.identity[0].principal_id
}
