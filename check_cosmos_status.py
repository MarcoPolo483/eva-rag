#!/usr/bin/env python3
"""Check document status in Cosmos DB"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from eva_rag.services.metadata_service import MetadataService

load_dotenv()

print("=" * 80)
print("EVA-RAG: Document Status Check")
print("=" * 80)
print()

# Initialize service
metadata_service = MetadataService()
container = metadata_service._get_container()

# Count by status
statuses = ["UPLOADED", "EXTRACTED", "CHUNKED", "EMBEDDED", "INDEXED", "FAILED"]

print("📊 Document Status Breakdown:")
print()

total = 0
for status in statuses:
    query = f"SELECT VALUE COUNT(1) FROM c WHERE c.status = '{status}'"
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    count = result[0] if result else 0
    total += count
    icon = "✅" if count > 0 else "⚪"
    print(f"   {icon} {status:12s}: {count:4d}")

print()
print(f"   TOTAL: {total}")
print()

# Show sample document
print("📄 Sample Documents (first 5):")
print()
query = "SELECT TOP 5 c.id, c.file_name, c.status, c.created_at FROM c ORDER BY c.created_at DESC"
docs = list(container.query_items(query=query, enable_cross_partition_query=True))

if docs:
    for doc in docs:
        print(f"   - {doc.get('file_name', 'unknown')[:60]:60s} | {doc.get('status', 'N/A'):10s}")
else:
    print("   (No documents found)")

print()
