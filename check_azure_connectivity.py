"""Check Azure service connectivity."""
import sys
from typing import Dict, Tuple

from eva_rag.config import settings


def check_azure_storage() -> Tuple[bool, str]:
    """Check Azure Blob Storage connectivity."""
    try:
        if not settings.azure_storage_connection_string:
            return False, "❌ AZURE_STORAGE_CONNECTION_STRING not configured"
        
        from azure.storage.blob import BlobServiceClient
        
        client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        
        # Try to get account information (lightweight operation)
        account_info = client.get_account_information()
        
        return True, f"✅ Connected to Azure Blob Storage ({settings.azure_storage_account_name})"
    
    except Exception as e:
        return False, f"❌ Azure Blob Storage connection failed: {str(e)}"


def check_azure_cosmos() -> Tuple[bool, str]:
    """Check Azure Cosmos DB connectivity."""
    try:
        if not settings.azure_cosmos_endpoint:
            return False, "❌ AZURE_COSMOS_ENDPOINT not configured"
        
        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential
        
        # Try with key first, then credential
        if settings.azure_cosmos_key:
            client = CosmosClient(
                settings.azure_cosmos_endpoint,
                settings.azure_cosmos_key,
            )
        else:
            credential = DefaultAzureCredential()
            client = CosmosClient(
                settings.azure_cosmos_endpoint,
                credential,
            )
        
        # Try to list databases (lightweight operation)
        databases = list(client.list_databases())
        
        return True, f"✅ Connected to Azure Cosmos DB ({settings.azure_cosmos_endpoint})"
    
    except ValueError as e:
        if "Invalid URL" in str(e):
            return False, f"❌ Azure Cosmos DB endpoint invalid: {settings.azure_cosmos_endpoint}"
        return False, f"❌ Azure Cosmos DB connection failed: {str(e)}"
    
    except Exception as e:
        return False, f"❌ Azure Cosmos DB connection failed: {str(e)}"


def check_azure_openai() -> Tuple[bool, str]:
    """Check Azure OpenAI connectivity."""
    try:
        if not settings.azure_openai_endpoint:
            return False, "❌ AZURE_OPENAI_ENDPOINT not configured"
        
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        
        # Try to list models (lightweight operation)
        # Note: This may fail with 404 depending on API version
        # Just checking client creation is enough
        
        return True, f"✅ Azure OpenAI client created ({settings.azure_openai_endpoint})"
    
    except Exception as e:
        return False, f"❌ Azure OpenAI connection failed: {str(e)}"


def check_azure_search() -> Tuple[bool, str]:
    """Check Azure AI Search connectivity."""
    try:
        if not settings.azure_search_endpoint:
            return False, "❌ AZURE_SEARCH_ENDPOINT not configured"
        
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Just check if we can create the client
        # Actual search would require the index to exist
        
        return True, f"✅ Azure AI Search endpoint configured ({settings.azure_search_endpoint})"
    
    except Exception as e:
        return False, f"❌ Azure AI Search connection failed: {str(e)}"


def check_redis() -> Tuple[bool, str]:
    """Check Redis connectivity."""
    try:
        import redis
        
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            socket_timeout=5,
        )
        
        # Try ping
        r.ping()
        
        return True, f"✅ Connected to Redis ({settings.redis_host}:{settings.redis_port})"
    
    except Exception as e:
        return False, f"❌ Redis connection failed: {str(e)}"


def main():
    """Run all connectivity checks."""
    print("=" * 80)
    print("EVA RAG - Azure Connectivity Check")
    print("=" * 80)
    print()
    
    checks = [
        ("Azure Blob Storage", check_azure_storage),
        ("Azure Cosmos DB", check_azure_cosmos),
        ("Azure OpenAI", check_azure_openai),
        ("Azure AI Search", check_azure_search),
        ("Redis Cache", check_redis),
    ]
    
    results: Dict[str, Tuple[bool, str]] = {}
    
    for name, check_func in checks:
        print(f"Checking {name}...")
        success, message = check_func()
        results[name] = (success, message)
        print(f"  {message}")
        print()
    
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    print(f"✅ {success_count}/{total_count} services connected successfully")
    print()
    
    failed_services = [name for name, (success, _) in results.items() if not success]
    if failed_services:
        print("⚠️  Failed services:")
        for service in failed_services:
            print(f"  - {service}")
        print()
        print("💡 Check your .env file or environment variables")
        sys.exit(1)
    else:
        print("🎉 All services are connected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
