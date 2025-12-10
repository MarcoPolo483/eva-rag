"""
Ingest Canada Life benefit booklets into EVA-RAG

This script loads:
- PSHCP Member Booklet (PDF, 0.60 MB)
- PSDCP Member Booklet (PDF, 0.37 MB)
- 200 Questions about PSHCP & PSDCP (DOCX, 0.06 MB)
- Canada Life in EVA Domain Assistant (DOCX, 0.04 MB)
"""

from pathlib import Path
from src.eva_rag.loaders.factory import LoaderFactory

# Source folder
CANADALIFE_FOLDER = Path(r"c:\Users\marco\Documents\_AI Dev\Marco\canadalife")

def ingest_canadalife_documents():
    """Load all Canada Life benefit booklets."""
    
    print("=" * 80)
    print("CANADA LIFE BENEFIT BOOKLETS INGESTION")
    print("=" * 80)
    print()
    
    # Get all files
    files = list(CANADALIFE_FOLDER.glob("*.*"))
    print(f"Found {len(files)} files in {CANADALIFE_FOLDER}")
    print()
    
    documents = []
    
    for file_path in files:
        print(f"Processing: {file_path.name}")
        print(f"  Type: {file_path.suffix}")
        print(f"  Size: {file_path.stat().st_size / 1024:.2f} KB")
        
        try:
            # Get appropriate loader
            loader = LoaderFactory.get_loader(str(file_path))
            
            # Load document
            with open(file_path, "rb") as f:
                doc = loader.load(f, file_path.name)
            
            # Add custom metadata
            doc.metadata["source_folder"] = "canadalife"
            doc.metadata["document_category"] = "benefit_booklet"
            doc.metadata["organization"] = "Canada Life"
            
            # Determine plan type
            if "pshcp" in file_path.name.lower():
                doc.metadata["plan_type"] = "PSHCP"
                doc.metadata["plan_name"] = "Public Service Health Care Plan"
            elif "psdcp" in file_path.name.lower():
                doc.metadata["plan_type"] = "PSDCP"
                doc.metadata["plan_name"] = "Public Service Dental Care Plan"
            else:
                doc.metadata["plan_type"] = "General"
            
            documents.append(doc)
            
            print(f"  ✅ Loaded successfully")
            print(f"  Text length: {len(doc.text)} characters")
            print(f"  Pages: {doc.page_count}")
            print(f"  Metadata keys: {list(doc.metadata.keys())}")
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            print()
            continue
    
    print("=" * 80)
    print(f"SUMMARY: Loaded {len(documents)}/{len(files)} documents")
    print("=" * 80)
    print()
    
    # Display statistics
    total_chars = sum(len(doc.text) for doc in documents)
    total_pages = sum(doc.page_count for doc in documents)
    
    print("Document Statistics:")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Total pages: {total_pages}")
    print(f"  Average chars/page: {total_chars/total_pages:.0f}" if total_pages > 0 else "")
    print()
    
    # Display document details
    print("Loaded Documents:")
    for i, doc in enumerate(documents, 1):
        print(f"\n{i}. {doc.metadata.get('file_name', 'Unknown')}")
        print(f"   Plan: {doc.metadata.get('plan_type', 'N/A')}")
        print(f"   Pages: {doc.page_count}")
        print(f"   Size: {len(doc.text):,} chars")
        
        # Show first 200 chars
        preview = doc.text[:200].replace('\n', ' ')
        print(f"   Preview: {preview}...")
    
    print()
    print("=" * 80)
    print("✅ INGESTION COMPLETE")
    print("=" * 80)
    
    return documents


if __name__ == "__main__":
    # Check if folder exists
    if not CANADALIFE_FOLDER.exists():
        print(f"❌ ERROR: Folder not found: {CANADALIFE_FOLDER}")
        exit(1)
    
    # Run ingestion
    docs = ingest_canadalife_documents()
    
    # Save summary
    summary_file = Path("canadalife_ingestion_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("CANADA LIFE BENEFIT BOOKLETS - INGESTION SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        for i, doc in enumerate(docs, 1):
            f.write(f"{i}. {doc.metadata.get('file_name', 'Unknown')}\n")
            f.write(f"   Plan Type: {doc.metadata.get('plan_type', 'N/A')}\n")
            f.write(f"   Plan Name: {doc.metadata.get('plan_name', 'N/A')}\n")
            f.write(f"   Pages: {doc.page_count}\n")
            f.write(f"   Characters: {len(doc.text):,}\n")
            f.write(f"   Metadata: {doc.metadata}\n")
            f.write("\n")
        
        f.write(f"\nTotal Documents: {len(docs)}\n")
        f.write(f"Total Pages: {sum(doc.page_count for doc in docs)}\n")
        f.write(f"Total Characters: {sum(len(doc.text) for doc in docs):,}\n")
    
    print(f"\n📄 Summary saved to: {summary_file}")
