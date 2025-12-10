"""Count indexed documents in Cosmos DB."""
from azure.cosmos import CosmosClient
from eva_rag.config import settings

client = CosmosClient(settings.azure_cosmos_endpoint, credential=settings.azure_cosmos_key)
db = client.get_database_client(settings.azure_cosmos_database)
container = db.get_container_client(settings.azure_cosmos_container)

# Get all documents and count by status manually
query = "SELECT c.status FROM c"
docs = list(container.query_items(query, enable_cross_partition_query=True))

status_counts = {}
for doc in docs:
    status = doc.get('status', 'unknown').lower()
    status_counts[status] = status_counts.get(status, 0) + 1

print("\n" + "="*80)
print("COSMOS DB STATUS SUMMARY")
print("="*80)
for status, count in sorted(status_counts.items()):
    print(f"   {status}: {count} documents")

# Get total
total_docs = len(docs)
indexed_docs = status_counts.get('indexed', 0)

print("\n" + "="*80)
print(f"✅ Total documents: {total_docs}")
print(f"✅ Indexed documents: {indexed_docs}")
print("="*80 + "\n")
