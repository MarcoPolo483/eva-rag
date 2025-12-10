#!/usr/bin/env python3
"""
Re-index documents that are already EMBEDDED but not yet INDEXED in Azure AI Search.

This script handles the migration after Azure AI Search integration was added.
Uses existing services to query and update documents.

Usage:
    python reindex_documents_simple.py [--limit N] [--dry-run]
"""
import os
import sys
import argparse
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv

from eva_rag.services.metadata_service import MetadataService
from eva_rag.services.chunk_service import ChunkService
from eva_rag.services.search_service import SearchService
from eva_rag.models.chunk import DocumentChunk
from eva_rag.config import Settings


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Re-index EMBEDDED documents in Azure AI Search")
    parser.add_argument("--limit", type=int, help="Limit number of documents to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed without actually indexing")
    args = parser.parse_args()

    # Load environment
    load_dotenv()
    settings = Settings()

    print("=" * 80)
    print("EVA-RAG: Re-index EMBEDDED Documents")
    print("=" * 80)
    print()

    # Initialize services
    print("🔗 Initializing services...")
    try:
        metadata_service = MetadataService()
        chunk_service = ChunkService()
        search_service = SearchService()
        print("   ✅ All services initialized")
    except Exception as e:
        print(f"   ❌ Error initializing services: {e}")
        sys.exit(1)

    print()

    # Query documents with status=EMBEDDED
    print(f"📊 Finding documents with status=EMBEDDED...")
    
    try:
        # Query Cosmos DB for EMBEDDED documents
        query = "SELECT * FROM c WHERE c.status = 'EMBEDDED'"
        
        # Use metadata_service _get_container() to get container
        container = metadata_service._get_container()
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if args.limit:
            documents = documents[:args.limit]
        
        total_docs = len(documents)
        print(f"   Found: {total_docs} documents")
        
    except Exception as e:
        print(f"   ❌ Error querying documents: {e}")
        sys.exit(1)

    if total_docs == 0:
        print("\n✅ No documents need re-indexing")
        return

    if args.dry_run:
        print(f"\n🔍 DRY RUN MODE - Would re-index {total_docs} documents:")
        for doc in documents[:10]:  # Show first 10
            print(f"   - {doc.get('file_name')} (ID: {doc.get('id')})")
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
        doc_id = doc.get("id")
        filename = doc.get("file_name", "unknown")
        tenant_id = doc.get("tenant_id", "default")
        space_id = doc.get("space_id", "default")

        print(f"[{idx}/{total_docs}] Processing: {filename}")
        print(f"   Document ID: {doc_id}")
        print(f"   Tenant: {tenant_id}, Space: {space_id}")

        try:
            # Get chunks for this document using ChunkService
            chunks = chunk_service.get_chunks_by_document(
                document_id=doc_id,
                space_id=space_id,
                tenant_id=tenant_id
            )

            if not chunks:
                print(f"   ⚠️ No chunks found - skipping")
                continue

            # Filter chunks that have embeddings
            chunks_with_embeddings = [c for c in chunks if c.embedding is not None and len(c.embedding) > 0]

            if not chunks_with_embeddings:
                print(f"   ⚠️ No chunks with embeddings found - skipping")
                continue

            print(f"   Found: {len(chunks_with_embeddings)} chunks with embeddings")

            # Index in Azure AI Search
            print(f"   📤 Indexing {len(chunks_with_embeddings)} chunks...")
            indexed_count = search_service.index_chunks(chunks_with_embeddings)

            if indexed_count == len(chunks_with_embeddings):
                print(f"   ✅ Indexed: {indexed_count} chunks")
                
                # Update document status to INDEXED
                doc['status'] = 'INDEXED'
                doc['indexed_at'] = datetime.now(timezone.utc).isoformat()
                container = metadata_service._get_container()
                container.upsert_item(doc)
                
                success_count += 1
                total_chunks_indexed += indexed_count
            else:
                print(f"   ⚠️ Partial success: {indexed_count}/{len(chunks_with_embeddings)} chunks indexed")
                error_count += 1

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
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
        print("1. Run: python test_search_integration.py")
        print("2. Try actual queries via POST /api/v1/rag/search")
        print()


if __name__ == "__main__":
    main()
