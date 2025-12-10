#!/usr/bin/env python3
"""
Re-index documents that are already EMBEDDED but not yet INDEXED in Azure AI Search.

This script handles the migration after Azure AI Search integration was added.
It reads documents with status=EMBEDDED from Cosmos DB, retrieves their chunks
with embeddings, and indexes them in Azure AI Search.

Usage:
    python reindex_embedded_documents.py [--limit N] [--dry-run]
"""
import os
import sys
import argparse
import asyncio
from datetime import datetime, timezone
from typing import List
from uuid import UUID

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from pymongo import MongoClient

from eva_rag.services.search_service import SearchService
from eva_rag.models.chunk import DocumentChunk
from eva_rag.config import Settings


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Re-index EMBEDDED documents in Azure AI Search")
    parser.add_argument("--limit", type=int, help="Limit number of documents to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed without actually indexing")
    parser.add_argument("--tenant", help="Filter by tenant_id")
    parser.add_argument("--space", help="Filter by space_id")
    args = parser.parse_args()

    # Load environment
    load_dotenv()
    settings = Settings()

    print("=" * 80)
    print("EVA-RAG: Re-index EMBEDDED Documents")
    print("=" * 80)
    print()

    # Connect to Cosmos DB
    print("🔗 Connecting to Cosmos DB...")
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ ERROR: MONGODB_URI not found in .env")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client["eva-rag"]
    documents_collection = db["documents"]
    chunks_collection = db["chunks"]

    # Initialize Azure AI Search
    print("🔗 Connecting to Azure AI Search...")
    search_service = SearchService()

    # Build query
    query = {"status": "EMBEDDED"}
    if args.tenant:
        query["tenant_id"] = args.tenant
    if args.space:
        query["space_id"] = args.space

    # Get documents to re-index
    print(f"📊 Finding documents with status=EMBEDDED...")
    if args.limit:
        documents = list(documents_collection.find(query).limit(args.limit))
    else:
        documents = list(documents_collection.find(query))

    total_docs = len(documents)
    print(f"   Found: {total_docs} documents")

    if total_docs == 0:
        print("\n✅ No documents need re-indexing")
        return

    if args.dry_run:
        print(f"\n🔍 DRY RUN MODE - Would re-index {total_docs} documents:")
        for doc in documents[:10]:  # Show first 10
            print(f"   - {doc.get('file_name')} (ID: {doc.get('_id')})")
        if total_docs > 10:
            print(f"   ... and {total_docs - 10} more")
        return

    print()
    print("=" * 80)
    print("PROCESSING DOCUMENTS")
    print("=" * 80)
    print()

    # Process each document
    success_count = 0
    error_count = 0
    total_chunks_indexed = 0

    for idx, doc in enumerate(documents, 1):
        doc_id = str(doc.get("_id"))
        filename = doc.get("file_name", "unknown")
        tenant_id = doc.get("tenant_id", "default")
        space_id = doc.get("space_id", "default")

        print(f"[{idx}/{total_docs}] Processing: {filename}")
        print(f"   Document ID: {doc_id}")
        print(f"   Tenant: {tenant_id}, Space: {space_id}")

        try:
            # Get all chunks for this document
            chunk_docs = list(chunks_collection.find({
                "document_id": doc_id,
                "embedding": {"$exists": True, "$ne": None}
            }))

            if not chunk_docs:
                print(f"   ⚠️ No chunks with embeddings found - skipping")
                continue

            print(f"   Found: {len(chunk_docs)} chunks with embeddings")

            # Convert to DocumentChunk objects
            document_chunks: List[DocumentChunk] = []
            for chunk_doc in chunk_docs:
                doc_chunk = DocumentChunk(
                    id=chunk_doc.get("_id"),
                    document_id=doc_id,
                    space_id=space_id,
                    tenant_id=tenant_id,
                    text=chunk_doc.get("text", ""),
                    chunk_index=chunk_doc.get("chunk_index", 0),
                    page_number=chunk_doc.get("page_number"),
                    embedding=chunk_doc.get("embedding"),
                    language=chunk_doc.get("language", "EN"),
                    created_at=chunk_doc.get("created_at", datetime.now(timezone.utc)),
                    metadata=chunk_doc.get("metadata", {}),
                )
                document_chunks.append(doc_chunk)

            # Index in Azure AI Search
            print(f"   📤 Indexing {len(document_chunks)} chunks...")
            indexed_count = search_service.index_chunks(document_chunks)

            if indexed_count == len(document_chunks):
                print(f"   ✅ Indexed: {indexed_count} chunks")
                
                # Update document status to INDEXED
                documents_collection.update_one(
                    {"_id": doc.get("_id")},
                    {"$set": {
                        "status": "INDEXED",
                        "indexed_at": datetime.now(timezone.utc)
                    }}
                )
                
                success_count += 1
                total_chunks_indexed += indexed_count
            else:
                print(f"   ⚠️ Partial success: {indexed_count}/{len(document_chunks)} chunks indexed")
                error_count += 1

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1

        print()

    # Summary
    print("=" * 80)
    print("RE-INDEXING SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Success: {success_count} documents")
    print(f"❌ Errors: {error_count} documents")
    print(f"📦 Total chunks indexed: {total_chunks_indexed}")
    print()

    if success_count > 0:
        print("🎉 Re-indexing complete!")
        print()
        print("Next steps:")
        print("1. Run test_search_integration.py to verify search works")
        print("2. Try actual queries via POST /api/v1/rag/search")
        print()


if __name__ == "__main__":
    main()
