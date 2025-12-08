# Staging Environment
environment         = "staging"
location           = "eastus"
app_service_sku    = "P1v2"
cosmos_db_throughput = 400

allowed_ip_addresses = [
  # Add your IP addresses here
  # "1.2.3.4",
]

tags = {
  Project     = "EVA Suite"
  Component   = "RAG Engine"
  Environment = "Staging"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}
