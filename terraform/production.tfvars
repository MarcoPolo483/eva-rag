# Production Environment
environment         = "production"
location           = "eastus"
app_service_sku    = "P2v2"
cosmos_db_throughput = 800

allowed_ip_addresses = [
  # Add your production IP addresses here
  # "1.2.3.4",
]

tags = {
  Project     = "EVA Suite"
  Component   = "RAG Engine"
  Environment = "Production"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
  Compliance  = "Required"
}
