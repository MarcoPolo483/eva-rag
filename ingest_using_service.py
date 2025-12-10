#!/usr/bin/env python3
"""
Ingest documents from data-sources directory using IngestionService.

This script uses the actual IngestionService to process documents through
the complete pipeline: Upload → Extract → Chunk → Embed → Index → Store

Usage:
    python ingest_using_service.py [--limit N]
"""
import os
import sys
import argparse
from pathlib import Path
from uuid import UUID

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from eva_rag.services.ingestion_service import IngestionService


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Ingest documents using IngestionService")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    parser.add_argument("--pattern", default="*.pdf", help="File pattern to match (default: *.pdf)")
    args = parser.parse_args()

    # Load environment
    load_dotenv()

    print("=" * 80)
    print("EVA-RAG: Document Ingestion via IngestionService")
    print("=" * 80)
    print()

    # Initialize service
    print("🔗 Initializing IngestionService...")
    try:
        ingestion_service = IngestionService()
        print("   ✅ Service initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)

    # Find documents to ingest
    data_sources_dir = Path("data-sources")
    if not data_sources_dir.exists():
        print(f"❌ Directory not found: {data_sources_dir}")
        print("   Please create data-sources/ and add documents")
        sys.exit(1)

    # Find files - use absolute paths for rglob to work
    files = list(data_sources_dir.absolute().rglob(args.pattern))
    
    if args.limit:
        files = files[:args.limit]

    total_files = len(files)
    print(f"\n📁 Found {total_files} file(s) matching pattern '{args.pattern}'")
    
    if total_files == 0:
        print("   No files to ingest")
        sys.exit(0)

    print()
    print("=" * 80)
    print("PROCESSING FILES")
    print("=" * 80)
    print()

    # Process each file
    success_count = 0
    error_count = 0

    for idx, file_path in enumerate(files, 1):
        filename = file_path.name
        print(f"[{idx}/{total_files}] Processing: {filename}")
        print(f"   Path: {file_path}")

        try:
            # Read file
            with open(file_path, "rb") as f:
                file_content = f.read()
                file_size = len(file_content)

            # Ingest document - use async properly
            print(f"   📤 Ingesting ({file_size:,} bytes)...")
            
            import asyncio
            from io import BytesIO
            
            metadata = asyncio.run(
                ingestion_service.ingest_document(
                    file=BytesIO(file_content),
                    filename=filename,
                    file_size=file_size,
                    content_type=get_content_type(filename),
                    space_id=UUID("00000000-0000-0000-0000-000000000000"),
                    tenant_id=UUID("00000000-0000-0000-0000-000000000000"),
                    user_id=UUID("00000000-0000-0000-0000-000000000000"),
                    additional_metadata={
                        "source": "data-sources",
                        "ingestion_method": "ingest_using_service.py"
                    }
                )
            )

            print(f"   ✅ Success! Document ID: {metadata.id}")
            success_count += 1

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1

        print()

    # Summary
    print("=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Success: {success_count} documents")
    print(f"❌ Errors: {error_count} documents")
    print()

    if success_count > 0:
        print("🎉 Ingestion complete!")
        print()
        print("Documents have been:")
        print("1. ✅ Uploaded to Azure Storage")
        print("2. ✅ Extracted (text extraction)")
        print("3. ✅ Chunked (split into chunks)")
        print("4. ✅ Embedded (Azure OpenAI embeddings)")
        print("5. ✅ Indexed (Azure AI Search)")
        print("6. ✅ Stored (Cosmos DB metadata)")
        print()
        print("Next steps:")
        print("1. Run: python test_search_integration.py")
        print("2. Try queries via POST /api/v1/rag/search")
        print()


def get_content_type(filename: str) -> str:
    """Get MIME content type from filename extension."""
    ext = filename.lower().split(".")[-1]
    
    mime_types = {
        "pdf": "application/pdf",
        "txt": "text/plain",
        "md": "text/markdown",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "html": "text/html",
        "htm": "text/html",
        "json": "application/json",
        "xml": "application/xml",
    }
    
    return mime_types.get(ext, "application/octet-stream")


if __name__ == "__main__":
    main()
