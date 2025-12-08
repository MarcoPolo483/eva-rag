variable "environment" {
  description = "Environment name (staging/production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "app_service_sku" {
  description = "SKU for App Service Plan"
  type        = string
  default     = "P1v2"
}

variable "cosmos_db_throughput" {
  description = "Cosmos DB throughput (RU/s)"
  type        = number
  default     = 400
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "EVA Suite"
    Component   = "RAG Engine"
    ManagedBy   = "Terraform"
  }
}

variable "allowed_ip_addresses" {
  description = "IP addresses allowed to access resources"
  type        = list(string)
  default     = []
}
