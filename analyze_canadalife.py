"""
Analyze Canada Life benefit booklet content for RAG readiness
"""

from pathlib import Path
from src.eva_rag.loaders.factory import LoaderFactory

CANADALIFE_FOLDER = Path(r"c:\Users\marco\Documents\_AI Dev\Marco\canadalife")

def analyze_content():
    """Analyze extracted content from Canada Life documents."""
    
    print("=" * 100)
    print("CANADA LIFE BENEFIT BOOKLETS - CONTENT ANALYSIS")
    print("=" * 100)
    print()
    
    files = sorted(CANADALIFE_FOLDER.glob("*.*"))
    
    for file_path in files:
        print(f"\n{'=' * 100}")
        print(f"📄 {file_path.name}")
        print(f"{'=' * 100}")
        
        try:
            loader = LoaderFactory.get_loader(str(file_path))
            
            with open(file_path, "rb") as f:
                doc = loader.load(f, file_path.name)
            
            print(f"\n📊 Document Statistics:")
            print(f"   File Size: {file_path.stat().st_size / 1024:.2f} KB")
            print(f"   Pages: {doc.page_count}")
            print(f"   Characters: {len(doc.text):,}")
            print(f"   Words (approx): {len(doc.text.split()):,}")
            print(f"   Lines: {doc.text.count(chr(10)):,}")
            
            print(f"\n📋 Metadata:")
            for key, value in doc.metadata.items():
                if isinstance(value, str) and len(value) > 80:
                    value = value[:77] + "..."
                print(f"   {key}: {value}")
            
            print(f"\n📖 Content Preview (first 1000 characters):")
            print("   " + "-" * 96)
            preview = doc.text[:1000].replace('\n', '\n   ')
            print(f"   {preview}")
            print("   " + "-" * 96)
            
            # Extract key sections (if visible)
            text_lower = doc.text.lower()
            
            sections_found = []
            keywords = [
                'table of contents', 'introduction', 'coverage', 'benefits',
                'eligibility', 'claims', 'dental', 'health', 'vision',
                'prescription', 'drug', 'deductible', 'co-payment',
                'exclusions', 'limitations', 'emergency', 'contact'
            ]
            
            for keyword in keywords:
                if keyword in text_lower:
                    count = text_lower.count(keyword)
                    sections_found.append((keyword, count))
            
            if sections_found:
                print(f"\n🔍 Key Topics Detected:")
                sections_found.sort(key=lambda x: x[1], reverse=True)
                for topic, count in sections_found[:10]:
                    print(f"   • {topic.title()}: {count} mentions")
            
            # Check for structured content
            has_bullets = '•' in doc.text or '◦' in doc.text
            has_tables = '[TABLE' in doc.text or '|' in doc.text
            has_sections = any(marker in doc.text for marker in ['####', '###', '##', '#'])
            
            print(f"\n✨ Content Structure:")
            print(f"   Bullet points: {'✅' if has_bullets else '❌'}")
            print(f"   Tables: {'✅' if has_tables else '❌'}")
            print(f"   Section headers: {'✅' if has_sections else '❌'}")
            
            # Estimate chunk count for RAG (500 tokens per chunk)
            estimated_tokens = len(doc.text.split()) * 1.3  # Rough token estimate
            estimated_chunks = int(estimated_tokens / 500)
            
            print(f"\n🔢 RAG Estimates:")
            print(f"   Estimated tokens: {estimated_tokens:,.0f}")
            print(f"   Estimated chunks (500 tokens): {estimated_chunks:,}")
            print(f"   Estimated queries needed: {estimated_chunks * 3:,} (3x chunks for coverage)")
            
        except Exception as e:
            print(f"\n❌ Error processing {file_path.name}: {str(e)}")
            continue
    
    print(f"\n\n{'=' * 100}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'=' * 100}")


if __name__ == "__main__":
    analyze_content()
