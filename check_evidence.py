"""Quick evidence check for ingestion results."""
from azure.cosmos import CosmosClient
from eva_rag.config import settings

client = CosmosClient(settings.azure_cosmos_endpoint, credential=settings.azure_cosmos_key)
db = client.get_database_client(settings.azure_cosmos_database)
container = db.get_container_client(settings.azure_cosmos_container)

# Query for INDEXED documents (case-sensitive enum value)
query = 'SELECT c.id, c.filename, c.status, c.chunk_count FROM c'
docs = list(container.query_items(query, enable_cross_partition_query=True))

print("\n" + "="*80)
print("COSMOS DB INGESTION EVIDENCE")
print("="*80)

indexed = [d for d in docs if d.get('status') == 'INDEXED']
indexing = [d for d in docs if d.get('status') in ['INDEXING', 'indexing']]
other = [d for d in docs if d.get('status') not in ['INDEXED', 'INDEXING', 'indexing']]

print(f"\n📊 Status Breakdown:")
print(f"   ✅ INDEXED (complete):   {len(indexed)} documents")
print(f"   ⏳ INDEXING (in progress): {len(indexing)} documents")
print(f"   ❓ Other statuses:        {len(other)} documents")
print(f"   📦 TOTAL:                {len(docs)} documents")

if indexed:
    print(f"\n✅ Successfully Indexed Documents:")
    for doc in indexed[:10]:
        chunks = doc.get('chunk_count', '?')
        print(f"   - {doc.get('filename', 'unknown')}")
        print(f"     ID: {doc['id']}")
        print(f"     Chunks: {chunks}")

if indexing:
    print(f"\n⏳ Documents Still Indexing:")
    for doc in indexing[:5]:
        print(f"   - {doc.get('filename', 'unknown')} ({doc.get('status')})")

print("\n" + "="*80)
