"""
Analyze table structures in IT Collective Agreement
"""
import json
import re
from pathlib import Path

def analyze_tables():
    """Extract and analyze table structures from collective agreement"""
    
    # Load the ingested data (NEW file with full_content)
    json_path = Path("data/ingested/specific_urls/specific_urls_20251209_013238.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get English collective agreement
    en_doc = None
    for doc in data:
        if doc.get('document_type') == 'collective_agreement' and doc.get('language') == 'en':
            en_doc = doc
            break
    
    if not en_doc:
        print("❌ No English collective agreement found")
        return
    
    content = en_doc['full_content']
    print(f"📄 Total content length: {len(content):,} characters")
    print(f"📄 Source: {en_doc['source_url']}\n")
    
    # Search for table indicators
    table_patterns = [
        (r'(?i)\bappendix\s+[A-Z]\b', 'Appendix'),
        (r'(?i)\bschedule\s+[A-Z0-9]\b', 'Schedule'),
        (r'(?i)\btable\s+\d+', 'Table'),
        (r'(?i)pay\s+rates?', 'Pay Rates'),
        (r'(?i)salary\s+scale', 'Salary Scale'),
        (r'(?i)classification\s+level', 'Classification'),
        (r'\$\d+,\d+', 'Dollar amounts'),
        (r'IT-0[1-5]', 'IT Classification Levels'),
        (r'Step\s+\d+', 'Salary Steps'),
    ]
    
    print("=" * 80)
    print("TABLE PATTERN DETECTION")
    print("=" * 80)
    
    for pattern, name in table_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"\n✅ {name}: {len(matches)} occurrences")
            # Show first few unique matches
            unique_matches = list(set(matches))[:5]
            for match in unique_matches:
                print(f"   - {match}")
    
    # Find appendix/schedule sections
    print("\n" + "=" * 80)
    print("APPENDIX/SCHEDULE SECTIONS")
    print("=" * 80)
    
    appendix_matches = list(re.finditer(r'(?i)(appendix|schedule)\s+([A-Z0-9])', content))
    for match in appendix_matches[:10]:  # First 10
        start = match.start()
        # Get context around the match
        context_start = max(0, start - 100)
        context_end = min(len(content), start + 500)
        context = content[context_start:context_end]
        
        print(f"\n📋 Found at position {start}:")
        print("-" * 80)
        print(context)
        print("-" * 80)
    
    # Look for salary table patterns
    print("\n" + "=" * 80)
    print("SALARY TABLE PATTERNS")
    print("=" * 80)
    
    # Find sections with IT-0X classifications and dollar amounts
    salary_pattern = r'(IT-0[1-5].*?\$[\d,]+.*?(?=IT-0[1-5]|\Z))'
    salary_matches = re.finditer(salary_pattern, content, re.DOTALL)
    
    for i, match in enumerate(salary_matches):
        if i >= 3:  # Show first 3
            break
        
        text = match.group(1)[:800]  # First 800 chars
        print(f"\n💰 Salary Table Section {i+1}:")
        print("-" * 80)
        print(text)
        print("-" * 80)
    
    # Look for structured data patterns (HTML tables)
    print("\n" + "=" * 80)
    print("HTML TABLE DETECTION")
    print("=" * 80)
    
    table_tags = re.findall(r'<table[^>]*>.*?</table>', content, re.DOTALL | re.IGNORECASE)
    print(f"\n📊 Found {len(table_tags)} HTML <table> elements")
    
    if table_tags:
        for i, table in enumerate(table_tags[:3]):  # Show first 3
            print(f"\n🔍 Table {i+1} (first 1000 chars):")
            print("-" * 80)
            print(table[:1000])
            print("-" * 80)
            
            # Count rows and cells
            rows = re.findall(r'<tr[^>]*>', table, re.IGNORECASE)
            cells = re.findall(r'<t[dh][^>]*>', table, re.IGNORECASE)
            print(f"   Rows: {len(rows)}, Cells: {len(cells)}")
    
    # Look for definition list patterns (could be used for tables)
    print("\n" + "=" * 80)
    print("DEFINITION LIST PATTERNS")
    print("=" * 80)
    
    dl_tags = re.findall(r'<dl[^>]*>.*?</dl>', content, re.DOTALL | re.IGNORECASE)
    print(f"\n📝 Found {len(dl_tags)} HTML <dl> (definition list) elements")
    
    if dl_tags:
        for i, dl in enumerate(dl_tags[:2]):  # Show first 2
            print(f"\n📋 Definition List {i+1} (first 600 chars):")
            print("-" * 80)
            print(dl[:600])
            print("-" * 80)

if __name__ == "__main__":
    analyze_tables()
