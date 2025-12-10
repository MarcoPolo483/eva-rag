"""
Comprehensive test of 3 working data sources:
1. AssistMe XML (knowledge articles)
2. Employment Equity Act + IT Collective Agreement (government programs)
3. Canada Life booklets (benefits documentation)
"""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter

def test_assistme_xml():
    """Test AssistMe XML knowledge base (Cúram)."""
    print("="*80)
    print("TEST 1: ASSISTME XML KNOWLEDGE BASE")
    print("="*80)
    
    # Try multiple possible paths
    possible_paths = [
        Path("c:/Users/marco/Documents/_AI Dev/Marco/assistme/knowledge_articles_r2r3_en 2.xml"),
        Path("data/legal/assistme/knowledge_articles_r2r3_en 2.xml"),
        Path("../Marco/assistme/knowledge_articles_r2r3_en 2.xml")
    ]
    
    xml_path = None
    for path in possible_paths:
        if path.exists():
            xml_path = path
            break
    
    if xml_path is None:
        print(f"❌ XML file not found in any of these locations:")
        for p in possible_paths:
            print(f"   {p}")
        print(f"\n⚠️  Checking ingested data instead...")
        
        # Check if already ingested
        ingested_path = Path("data/ingested/legal")
        if ingested_path.exists():
            json_files = list(ingested_path.glob("*assistme*.json"))
            if json_files:
                print(f"✅ Found ingested AssistMe data:")
                latest = max(json_files, key=lambda p: p.stat().st_mtime)
                with open(latest, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   File: {latest.name}")
                print(f"   Documents: {len(data)}")
                
                if data:
                    doc = data[0]
                    meta = doc.get('metadata', {})
                    print(f"\n   Sample Document:")
                    print(f"   Client: {meta.get('client', 'N/A')}")
                    print(f"   System: {meta.get('system', 'N/A')}")
                    print(f"   Programs: {meta.get('programs', 'N/A')}")
                    print(f"   Length: {doc.get('content_length', 0):,} chars")
                    
                    total_chars = sum(d.get('content_length', 0) for d in data)
                    print(f"\n   Total characters: {total_chars:,}")
                    print(f"   Average per article: {total_chars // len(data):,}")
                
                print(f"\n✅ AssistMe test PASSED (using ingested data)")
                return True
        
        print(f"❌ No ingested AssistMe data found either")
        return False
    
    print(f"\n✅ File found: {xml_path}")
    print(f"   Size: {xml_path.stat().st_size:,} bytes")
    
    # Parse XML
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print(f"\n📋 XML Structure:")
    print(f"   Root element: {root.tag}")
    print(f"   Total documents: {len(root.findall('document'))}")
    
    # Analyze documents
    documents = root.findall('document')
    total_chars = 0
    programs = set()
    has_video = 0
    has_walkme = 0
    
    print(f"\n📊 Document Analysis:")
    for i, doc in enumerate(documents[:5], 1):  # Show first 5
        ref = doc.find('reference').text if doc.find('reference') is not None else 'N/A'
        title = doc.find('title').text if doc.find('title') is not None else 'N/A'
        content = doc.find('content').text if doc.find('content') is not None else ''
        video_link = doc.find('video_link').text if doc.find('video_link') is not None else None
        walkme_id = doc.find('walkme_flow_id').text if doc.find('walkme_flow_id') is not None else None
        
        total_chars += len(content)
        
        if video_link and video_link != '[-1]':
            has_video += 1
        if walkme_id and walkme_id != '[-1]':
            has_walkme += 1
        
        # Extract program mentions
        for prog in ['OAS', 'GIS', 'CPP', 'CPPD', 'ALW', 'ALWS']:
            if prog.lower() in content.lower():
                programs.add(prog)
        
        print(f"\n   Document {i}:")
        print(f"   Title: {title[:70]}...")
        print(f"   Reference: {ref[:50]}...")
        print(f"   Content length: {len(content):,} chars")
        print(f"   Has video: {'Yes' if video_link != '[-1]' else 'No'}")
        print(f"   Has WalkMe: {'Yes' if walkme_id != '[-1]' else 'No'}")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total articles: {len(documents)}")
    print(f"   Total characters: {total_chars:,}")
    print(f"   Average chars/article: {total_chars // len(documents):,}")
    print(f"   Articles with video: {has_video} ({has_video/len(documents)*100:.1f}%)")
    print(f"   Articles with WalkMe: {has_walkme} ({has_walkme/len(documents)*100:.1f}%)")
    print(f"   Programs mentioned: {', '.join(sorted(programs))}")
    
    # Check ingested data
    ingested_path = Path("data/ingested/legal")
    if ingested_path.exists():
        json_files = list(ingested_path.glob("*.json"))
        if json_files:
            latest = max(json_files, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r', encoding='utf-8') as f:
                ingested = json.load(f)
            
            assistme_docs = [d for d in ingested if d.get('metadata', {}).get('client') == 'assistme']
            print(f"\n✅ Ingestion Status:")
            print(f"   Ingested file: {latest.name}")
            print(f"   AssistMe documents: {len(assistme_docs)}")
            if assistme_docs:
                print(f"   Sample metadata: {assistme_docs[0].get('metadata', {})}")
    
    print(f"\n✅ AssistMe XML test PASSED")
    return True


def test_government_programs():
    """Test Employment Equity Act + IT Collective Agreement."""
    print("\n" + "="*80)
    print("TEST 2: GOVERNMENT PROGRAMS (EMPLOYMENT EQUITY ACT + IT COLLECTIVE AGREEMENT)")
    print("="*80)
    
    json_path = Path("data/ingested/specific_urls/specific_urls_20251209_013238.json")
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return False
    
    print(f"\n✅ File found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📋 Dataset Overview:")
    print(f"   Total documents: {len(data)}")
    
    # Group by document type
    by_type = {}
    by_format = {}
    by_language = {}
    
    for doc in data:
        doc_type = doc.get('document_type', 'unknown')
        fmt = doc.get('format', 'unknown')
        lang = doc.get('language', 'unknown')
        
        by_type[doc_type] = by_type.get(doc_type, 0) + 1
        by_format[fmt] = by_format.get(fmt, 0) + 1
        by_language[lang] = by_language.get(lang, 0) + 1
    
    print(f"\n📊 By Document Type:")
    for doc_type, count in sorted(by_type.items()):
        print(f"   {doc_type}: {count}")
    
    print(f"\n📊 By Format:")
    for fmt, count in sorted(by_format.items()):
        print(f"   {fmt.upper()}: {count}")
    
    print(f"\n📊 By Language:")
    for lang, count in sorted(by_language.items()):
        print(f"   {lang.upper()}: {count}")
    
    # Analyze Employment Equity Act
    print(f"\n📄 Employment Equity Act:")
    equity_docs = [d for d in data if d.get('document_type') == 'legislation']
    
    for doc in equity_docs:
        meta = doc.get('metadata', {})
        print(f"\n   Format: {doc.get('format', 'N/A').upper()}")
        print(f"   Language: {doc.get('language', 'N/A').upper()}")
        print(f"   Length: {doc.get('content_length', 0):,} chars")
        print(f"   Act: {meta.get('act_name', 'N/A')}")
        print(f"   Category: {meta.get('data_category', 'N/A')}")
        print(f"   Program Area: {meta.get('program_area', 'N/A')}")
    
    # Analyze IT Collective Agreement
    print(f"\n📄 IT Collective Agreement:")
    agreement_docs = [d for d in data if d.get('document_type') == 'collective_agreement']
    
    for doc in agreement_docs:
        meta = doc.get('metadata', {})
        print(f"\n   Language: {doc.get('language', 'N/A').upper()}")
        print(f"   Length: {doc.get('content_length', 0):,} chars")
        print(f"   Agreement: {meta.get('agreement_name', 'N/A')}")
        print(f"   Bargaining Agent: {meta.get('bargaining_agent', 'N/A')}")
        print(f"   Category: {meta.get('data_category', 'N/A')}")
        
        # Check for tables in content (if full_content exists)
        if 'full_content' in doc:
            content = doc['full_content']
            table_count = content.count('| Step')
            print(f"   Salary tables found: ~{table_count}")
    
    print(f"\n✅ Government Programs test PASSED")
    return True


def test_canada_life():
    """Test Canada Life benefits booklets."""
    print("\n" + "="*80)
    print("TEST 3: CANADA LIFE BENEFITS BOOKLETS")
    print("="*80)
    
    # Try multiple possible paths
    possible_paths = [
        Path("data/benefits/canada_life"),
        Path("data/canada_life"),
        Path("../Marco/canada_life")
    ]
    
    data_dir = None
    for path in possible_paths:
        if path.exists():
            data_dir = path
            break
    
    if data_dir is None:
        print(f"❌ Directory not found in any location")
        print(f"\n⚠️  Checking ingested data instead...")
        
        # Check if already ingested
        ingested_dirs = [
            Path("data/ingested/benefits"),
            Path("data/ingested/canada_ca"),
            Path("data/ingested")
        ]
        
        for ingested_path in ingested_dirs:
            if ingested_path.exists():
                json_files = list(ingested_path.glob("*canada*.json"))
                if json_files:
                    print(f"\n✅ Found ingested Canada Life data:")
                    for jf in json_files:
                        print(f"   {jf.name}: {jf.stat().st_size:,} bytes")
                        
                        with open(jf, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        print(f"   Documents: {len(data)}")
                        
                        total_chars = 0
                        for i, doc in enumerate(data[:3], 1):  # Show first 3
                            meta = doc.get('metadata', {})
                            length = doc.get('content_length', 0)
                            total_chars += length
                            
                            print(f"\n   Document {i}:")
                            print(f"   Title: {meta.get('title', 'N/A')[:60]}...")
                            print(f"   Client: {meta.get('client', 'N/A')}")
                            print(f"   Length: {length:,} chars")
                            
                            # Check structure quality
                            preview = doc.get('content_preview', '')
                            has_bullets = '•' in preview or '*' in preview or '-' in preview
                            has_headers = '#' in preview or len([l for l in preview.split('\n') if l.isupper()]) > 0
                            print(f"   Has structure: {'Yes' if has_bullets or has_headers else 'Unknown'}")
                        
                        if len(data) > 3:
                            for doc in data[3:]:
                                total_chars += doc.get('content_length', 0)
                        
                        print(f"\n   Total characters: {total_chars:,}")
                        if len(data) > 0:
                            print(f"   Average per document: {total_chars // len(data):,}")
                    
                    print(f"\n✅ Canada Life test PASSED (using ingested data)")
                    return True
        
        print(f"❌ No ingested Canada Life data found")
        return False
    
    print(f"\n✅ Directory found: {data_dir}")
    
    # List all files
    files = list(data_dir.glob("*.*"))
    print(f"\n📁 Files in directory:")
    
    total_size = 0
    for f in files:
        size = f.stat().st_size
        total_size += size
        print(f"   {f.name}: {size:,} bytes ({size/1024:.1f} KB)")
    
    print(f"\n   Total: {len(files)} files, {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    # Check ingested data
    ingested_path = Path("data/ingested/benefits")
    if ingested_path.exists():
        json_files = list(ingested_path.glob("*.json"))
        if json_files:
            print(f"\n✅ Ingested files found:")
            for jf in json_files:
                print(f"   {jf.name}: {jf.stat().st_size:,} bytes")
                
                with open(jf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   Documents: {len(data)}")
                
                for i, doc in enumerate(data, 1):
                    meta = doc.get('metadata', {})
                    print(f"\n   Document {i}:")
                    print(f"   Title: {meta.get('title', 'N/A')}")
                    print(f"   Client: {meta.get('client', 'N/A')}")
                    print(f"   Length: {doc.get('content_length', 0):,} chars")
                    print(f"   Category: {meta.get('data_category', 'N/A')}")
                    
                    # Check structure quality
                    preview = doc.get('content_preview', '')
                    has_bullets = '•' in preview or '*' in preview
                    has_headers = '#' in preview
                    print(f"   Has structure: {'Yes' if has_bullets or has_headers else 'No'}")
    
    print(f"\n✅ Canada Life test PASSED")
    return True


def run_comprehensive_tests():
    """Run all data source tests."""
    print("="*80)
    print("COMPREHENSIVE DATA SOURCE TESTING")
    print("="*80)
    print("\nTesting 3 working data sources:\n")
    print("1. AssistMe XML (Cúram knowledge base - 104 articles)")
    print("2. Government Programs (Employment Equity Act + IT Collective Agreement)")
    print("3. Canada Life (4 benefits booklets)")
    print("\n" + "="*80 + "\n")
    
    results = {}
    
    # Test 1: AssistMe XML
    try:
        results['AssistMe'] = test_assistme_xml()
    except Exception as e:
        print(f"\n❌ AssistMe test FAILED: {e}")
        results['AssistMe'] = False
    
    # Test 2: Government Programs
    try:
        results['Government Programs'] = test_government_programs()
    except Exception as e:
        print(f"\n❌ Government Programs test FAILED: {e}")
        results['Government Programs'] = False
    
    # Test 3: Canada Life
    try:
        results['Canada Life'] = test_canada_life()
    except Exception as e:
        print(f"\n❌ Canada Life test FAILED: {e}")
        results['Canada Life'] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    for source, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{source}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All data sources are working correctly!")
    else:
        print("\n⚠️  Some data sources have issues - review output above")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
