"""
Test XML and Folder Ingestion with Real Data

This script demonstrates how to use XMLLoader and FolderLoader with actual datasets.

Setup Instructions:
1. Copy your folders to test_data/:
   - Supreme Court cases: `test_data/jp/`
   - Knowledge articles: `test_data/assistme/`

2. Run this script:
   ```powershell
   python test_ingestion.py
   ```

Expected Results:
- XMLLoader will parse knowledge articles and detect schema
- FolderLoader will recursively process all HTML files from JP folder
- Progress tracking and error handling will be demonstrated
- Output will show extracted content and metadata
"""
import json
from pathlib import Path

from eva_rag.loaders.folder_loader import FolderLoader
from eva_rag.loaders.xml_loader import XMLLoader


def test_xml_ingestion():
    """Test XML ingestion with knowledge articles."""
    print("\n" + "="*80)
    print("TEST 1: XML Ingestion (Knowledge Articles)")
    print("="*80 + "\n")
    
    xml_file = Path("c:/Users/marco/Documents/_AI Dev/Marco/assistme/knowledge_articles_r2r3_en 2.xml")
    
    if not xml_file.exists():
        print(f"❌ File not found: {xml_file}")
        print("   Please copy the assistme folder to test with actual data.")
        return
    
    print(f"📄 Loading: {xml_file.name}")
    
    loader = XMLLoader(detect_schema=True)
    
    try:
        with open(xml_file, "rb") as f:
            doc = loader.load_from_stream(f)
        
        print(f"\n✅ Successfully loaded XML document")
        print(f"   Text length: {len(doc.text)} characters")
        print(f"   Page count: {doc.page_count}")
        
        # Display schema
        if "detected_schema" in doc.metadata:
            schema = doc.metadata["detected_schema"]
            print(f"\n📊 Detected Schema:")
            print(f"   Root element: {schema['root_element']}")
            print(f"   Structure type: {schema['structure_type']}")
            print(f"   Repeating elements: {', '.join(schema['repeating_elements'][:5])}...")
            print(f"   Common attributes: {', '.join(schema['common_attributes'][:5])}")
            
            if "document_count" in doc.metadata:
                print(f"   Document count: {doc.metadata['document_count']}")
        
        # Display sample content
        print(f"\n📝 Sample Content (first 500 chars):")
        print("-" * 80)
        print(doc.text[:500])
        print("-" * 80)
        
        # Save schema to file
        schema_file = "detected_schema_knowledge_articles.json"
        with open(schema_file, "w") as f:
            json.dump(doc.metadata.get("detected_schema", {}), f, indent=2)
        print(f"\n💾 Schema saved to: {schema_file}")
        
    except Exception as e:
        print(f"❌ Error loading XML: {e}")


def test_folder_ingestion():
    """Test folder ingestion with Supreme Court cases."""
    print("\n" + "="*80)
    print("TEST 2: Folder Ingestion (Supreme Court HTML Files)")
    print("="*80 + "\n")
    
    folder_path = Path("c:/Users/marco/Documents/_AI Dev/Marco/JP")
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        print("   Please copy the JP folder to test with actual data.")
        return
    
    print(f"📁 Loading from: {folder_path}")
    
    loader = FolderLoader(
        folder_path=folder_path,
        recursive=True,
        include_patterns=["*.html", "*.htm"],
        skip_patterns=["*_files", "*.css", "*.js"],
        continue_on_error=True
    )
    
    try:
        print("\n🔄 Processing files...")
        docs = loader.load_all()
        
        progress = loader.progress
        print(f"\n✅ Folder ingestion complete!")
        print(f"   Total files: {progress['total_files']}")
        print(f"   Processed: {progress['processed_files']}")
        print(f"   Failed: {progress['failed_files']}")
        print(f"   Success rate: {progress['success_rate']:.1f}%")
        
        if docs:
            print(f"\n📄 Sample Document (first loaded file):")
            sample_doc = docs[0]
            print(f"   File: {sample_doc.metadata['file_name']}")
            print(f"   Size: {sample_doc.metadata['file_size']:,} bytes")
            print(f"   Text length: {len(sample_doc.text):,} characters")
            print(f"   Page count: {sample_doc.page_count}")
            
            print(f"\n📝 Sample Content (first 300 chars):")
            print("-" * 80)
            print(sample_doc.text[:300])
            print("-" * 80)
        
        # Display failures
        if progress['failures']:
            print(f"\n⚠️  Failed Files:")
            for failure in progress['failures'][:5]:  # Show first 5
                print(f"   - {failure['file']}: {failure['error']}")
        
        # Save summary
        summary_file = "folder_ingestion_summary.json"
        with open(summary_file, "w") as f:
            json.dump(progress, f, indent=2)
        print(f"\n💾 Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"❌ Error during folder ingestion: {e}")


def main():
    """Run all ingestion tests."""
    print("\n" + "="*80)
    print("EVA-RAG: XML & Folder Ingestion Test Suite")
    print("="*80)
    
    # Test XML ingestion
    test_xml_ingestion()
    
    # Test folder ingestion
    test_folder_ingestion()
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80 + "\n")
    
    print("Next Steps:")
    print("1. Review detected schema in detected_schema_knowledge_articles.json")
    print("2. Review folder summary in folder_ingestion_summary.json")
    print("3. If files not found, copy datasets to test_data/ folder:")
    print("   - Copy 'JP' folder → test_data/jp/")
    print("   - Copy 'assistme' folder → test_data/assistme/")
    print("4. Iterate on schema detection based on actual data structure\n")


if __name__ == "__main__":
    main()
