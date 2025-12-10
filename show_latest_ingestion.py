"""Show most recent ingestion with full details."""
from azure.cosmos import CosmosClient
from eva_rag.config import settings
from datetime import datetime

client = CosmosClient(settings.azure_cosmos_endpoint, credential=settings.azure_cosmos_key)
db = client.get_database_client(settings.azure_cosmos_database)
container = db.get_container_client(settings.azure_cosmos_container)

# Get most recent document
query = 'SELECT TOP 1 * FROM c ORDER BY c._ts DESC'
docs = list(container.query_items(query, enable_cross_partition_query=True))

if docs:
    doc = docs[0]
    print("\n" + "="*80)
    print("MOST RECENT INGESTION ATTEMPT")
    print("="*80)
    print(f"\n📄 Filename: {doc.get('filename', 'unknown')}")
    print(f"🆔 Document ID: {doc['id']}")
    print(f"📊 Status: {doc.get('status', 'unknown')}")
    print(f"📦 Chunks: {doc.get('chunk_count', 0)}")
    print(f"🔢 Embeddings: {doc.get('embedding_count', 0)}")
    print(f"📏 Size: {doc.get('size', 0):,} bytes")
    
    if doc.get('uploaded_at'):
        print(f"⬆️  Uploaded: {doc.get('uploaded_at')}")
    if doc.get('indexed_at'):
        print(f"✅ Indexed: {doc.get('indexed_at')}")
    
    print(f"\n🏷️  Metadata:")
    print(f"   - Space ID: {doc.get('space_id')}")
    print(f"   - Tenant ID: {doc.get('tenant_id')}")
    print(f"   - User ID: {doc.get('user_id')}")
    
    print("\n" + "="*80)
else:
    print("No documents found in Cosmos DB")
