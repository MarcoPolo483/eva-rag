# Resource Group
resource "azurerm_resource_group" "eva_rag" {
  name     = "eva-rag-${var.environment}"
  location = var.location
  tags     = merge(var.tags, { Environment = var.environment })
}

# App Service Plan
resource "azurerm_service_plan" "eva_rag" {
  name                = "eva-rag-${var.environment}-plan"
  location            = azurerm_resource_group.eva_rag.location
  resource_group_name = azurerm_resource_group.eva_rag.name
  os_type             = "Linux"
  sku_name            = var.app_service_sku
  tags                = azurerm_resource_group.eva_rag.tags
}

# App Service
resource "azurerm_linux_web_app" "eva_rag" {
  name                = "eva-rag-${var.environment}"
  location            = azurerm_resource_group.eva_rag.location
  resource_group_name = azurerm_resource_group.eva_rag.name
  service_plan_id     = azurerm_service_plan.eva_rag.id
  https_only          = true
  tags                = azurerm_resource_group.eva_rag.tags

  site_config {
    always_on                         = true
    ftps_state                       = "Disabled"
    http2_enabled                    = true
    minimum_tls_version              = "1.2"
    vnet_route_all_enabled           = false
    websockets_enabled               = false
    
    application_stack {
      python_version = "3.11"
    }

    health_check_path                = "/health"
    health_check_eviction_time_in_min = 5
  }

  app_settings = {
    # Application Configuration
    ENVIRONMENT                    = var.environment
    LOG_LEVEL                      = var.environment == "production" ? "INFO" : "DEBUG"
    MAX_FILE_SIZE_MB              = "50"
    SUPPORTED_LANGUAGES           = "en,fr"
    DEFAULT_CHUNK_SIZE            = "512"
    DEFAULT_CHUNK_OVERLAP         = "50"
    EMBEDDING_BATCH_SIZE          = "16"
    
    # Azure Configuration (Key Vault References)
    AZURE_STORAGE_ACCOUNT_NAME    = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/storage-account-name/)"
    AZURE_STORAGE_ACCOUNT_KEY     = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/storage-account-key/)"
    AZURE_STORAGE_CONTAINER_NAME  = "eva-rag-documents"
    
    AZURE_COSMOS_ENDPOINT         = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/cosmos-endpoint/)"
    AZURE_COSMOS_KEY              = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/cosmos-key/)"
    AZURE_COSMOS_DATABASE_NAME    = "eva-rag"
    AZURE_COSMOS_CONTAINER_NAME   = "document-metadata"
    
    AZURE_OPENAI_ENDPOINT         = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/openai-endpoint/)"
    AZURE_OPENAI_API_KEY          = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/openai-api-key/)"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
    AZURE_OPENAI_API_VERSION      = "2024-02-01"
    
    AZURE_SEARCH_ENDPOINT         = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/search-endpoint/)"
    AZURE_SEARCH_ADMIN_KEY        = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.eva_rag.vault_uri}secrets/search-admin-key/)"
    AZURE_SEARCH_INDEX_NAME       = "eva-rag-index"
    
    # Build Configuration
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    WEBSITE_HTTPLOGGING_RETENTION_DAYS = "7"
    
    # Application Insights
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.eva_rag.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.eva_rag.connection_string
  }

  identity {
    type = "SystemAssigned"
  }

  logs {
    application_logs {
      file_system_level = "Information"
    }
    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
  }
}

# Application Insights
resource "azurerm_application_insights" "eva_rag" {
  name                = "eva-rag-${var.environment}-insights"
  location            = azurerm_resource_group.eva_rag.location
  resource_group_name = azurerm_resource_group.eva_rag.name
  application_type    = "web"
  retention_in_days   = var.environment == "production" ? 90 : 30
  tags                = azurerm_resource_group.eva_rag.tags
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "eva_rag" {
  name                = "eva-rag-${var.environment}-logs"
  location            = azurerm_resource_group.eva_rag.location
  resource_group_name = azurerm_resource_group.eva_rag.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "production" ? 90 : 30
  tags                = azurerm_resource_group.eva_rag.tags
}

# Storage Account
resource "azurerm_storage_account" "eva_rag" {
  name                     = "evarag${var.environment}st"
  resource_group_name      = azurerm_resource_group.eva_rag.name
  location                 = azurerm_resource_group.eva_rag.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "production" ? "GRS" : "LRS"
  min_tls_version          = "TLS1_2"
  enable_https_traffic_only = true
  tags                     = azurerm_resource_group.eva_rag.tags

  blob_properties {
    versioning_enabled = true
    delete_retention_policy {
      days = 7
    }
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    ip_rules                   = var.allowed_ip_addresses
  }
}

# Storage Container
resource "azurerm_storage_container" "documents" {
  name                  = "eva-rag-documents"
  storage_account_name  = azurerm_storage_account.eva_rag.name
  container_access_type = "private"
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "eva_rag" {
  name                = "eva-rag-${var.environment}-cosmos"
  location            = azurerm_resource_group.eva_rag.location
  resource_group_name = azurerm_resource_group.eva_rag.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  tags                = azurerm_resource_group.eva_rag.tags

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.eva_rag.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "eva_rag" {
  name                = "eva-rag"
  resource_group_name = azurerm_cosmosdb_account.eva_rag.resource_group_name
  account_name        = azurerm_cosmosdb_account.eva_rag.name
}

# Cosmos DB Container
resource "azurerm_cosmosdb_sql_container" "metadata" {
  name                = "document-metadata"
  resource_group_name = azurerm_cosmosdb_account.eva_rag.resource_group_name
  account_name        = azurerm_cosmosdb_account.eva_rag.name
  database_name       = azurerm_cosmosdb_sql_database.eva_rag.name
  partition_key_path  = "/tenant_id"

  indexing_policy {
    indexing_mode = "consistent"

    included_path {
      path = "/*"
    }
  }
}

# Key Vault
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "eva_rag" {
  name                       = "eva-rag-${var.environment}-kv"
  location                   = azurerm_resource_group.eva_rag.location
  resource_group_name        = azurerm_resource_group.eva_rag.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = var.environment == "production"
  tags                       = azurerm_resource_group.eva_rag.tags

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = var.allowed_ip_addresses
  }
}

# Key Vault Access Policy for App Service
resource "azurerm_key_vault_access_policy" "app_service" {
  key_vault_id = azurerm_key_vault.eva_rag.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_linux_web_app.eva_rag.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}

# Key Vault Access Policy for Current User
resource "azurerm_key_vault_access_policy" "current_user" {
  key_vault_id = azurerm_key_vault.eva_rag.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "Purge"
  ]
}

# Key Vault Secrets (placeholders - update with actual values)
resource "azurerm_key_vault_secret" "storage_account_name" {
  name         = "storage-account-name"
  value        = azurerm_storage_account.eva_rag.name
  key_vault_id = azurerm_key_vault.eva_rag.id
  depends_on   = [azurerm_key_vault_access_policy.current_user]
}

resource "azurerm_key_vault_secret" "storage_account_key" {
  name         = "storage-account-key"
  value        = azurerm_storage_account.eva_rag.primary_access_key
  key_vault_id = azurerm_key_vault.eva_rag.id
  depends_on   = [azurerm_key_vault_access_policy.current_user]
}

resource "azurerm_key_vault_secret" "cosmos_endpoint" {
  name         = "cosmos-endpoint"
  value        = azurerm_cosmosdb_account.eva_rag.endpoint
  key_vault_id = azurerm_key_vault.eva_rag.id
  depends_on   = [azurerm_key_vault_access_policy.current_user]
}

resource "azurerm_key_vault_secret" "cosmos_key" {
  name         = "cosmos-key"
  value        = azurerm_cosmosdb_account.eva_rag.primary_key
  key_vault_id = azurerm_key_vault.eva_rag.id
  depends_on   = [azurerm_key_vault_access_policy.current_user]
}

# Alert Rules
resource "azurerm_monitor_metric_alert" "cpu_alert" {
  name                = "eva-rag-${var.environment}-cpu-alert"
  resource_group_name = azurerm_resource_group.eva_rag.name
  scopes              = [azurerm_service_plan.eva_rag.id]
  description         = "Alert when CPU usage exceeds 80%"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"
  tags                = azurerm_resource_group.eva_rag.tags

  criteria {
    metric_namespace = "Microsoft.Web/serverfarms"
    metric_name      = "CpuPercentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }
}

resource "azurerm_monitor_metric_alert" "memory_alert" {
  name                = "eva-rag-${var.environment}-memory-alert"
  resource_group_name = azurerm_resource_group.eva_rag.name
  scopes              = [azurerm_service_plan.eva_rag.id]
  description         = "Alert when memory usage exceeds 85%"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"
  tags                = azurerm_resource_group.eva_rag.tags

  criteria {
    metric_namespace = "Microsoft.Web/serverfarms"
    metric_name      = "MemoryPercentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 85
  }
}

resource "azurerm_monitor_metric_alert" "http_errors" {
  name                = "eva-rag-${var.environment}-http-errors"
  resource_group_name = azurerm_resource_group.eva_rag.name
  scopes              = [azurerm_linux_web_app.eva_rag.id]
  description         = "Alert when HTTP 5xx errors exceed threshold"
  severity            = 1
  frequency           = "PT5M"
  window_size         = "PT15M"
  tags                = azurerm_resource_group.eva_rag.tags

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 10
  }
}
