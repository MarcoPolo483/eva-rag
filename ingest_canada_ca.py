"""
Ingest canada.ca content (EN + FR) with 2-layer depth crawling.

This script crawls www.canada.ca for both English and French content,
extracting government information to support visitors, permanent residents,
citizens, and enterprises looking for assistance.

Usage:
    poetry run python ingest_canada_ca.py

Features:
- 2-layer deep crawling (homepage + direct links + their links)
- Bilingual support (EN + FR)
- Rate limiting (0.5s delay between requests)
- Duplicate prevention
- Progress tracking
"""
from pathlib import Path
import json
from datetime import datetime

from eva_rag.loaders.web_crawler_loader import WebCrawlerLoader, crawl_canada_ca


def save_documents_to_json(docs, output_file: Path):
    """Save extracted documents to JSON for inspection."""
    data = []
    for doc in docs:
        data.append({
            "source_url": doc.metadata.get('source_url', 'N/A') if doc.metadata else 'N/A',
            "content_preview": doc.text[:500] + "..." if len(doc.text) > 500 else doc.text,
            "content_length": len(doc.text),
            "page_count": doc.page_count,
            "metadata": doc.metadata,
        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Saved document metadata to: {output_file}")


def main():
    """Crawl canada.ca (EN + FR) with 2-layer depth."""
    
    print("=" * 80)
    print("🇨🇦 CANADA.CA CONTENT INGESTION")
    print("=" * 80)
    print()
    print("Use Case: Government Information Assistant")
    print("Target Users: Visitors, Permanent Residents, Citizens, Enterprises")
    print("Source: https://www.canada.ca/en.html & https://www.canada.ca/fr.html")
    print("Crawl Depth: 2 layers (homepage → direct links → their links)")
    print()
    print("⚠️  NOTE: This will take 10-30 minutes depending on site structure.")
    print("         canada.ca has ~1000s of pages. 2-layer depth is limited crawl.")
    print()
    
    # Create output directory
    output_dir = Path("data/ingested/canada_ca")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crawl English
    print("=" * 80)
    print("🇬🇧 ENGLISH (EN) CRAWL")
    print("=" * 80)
    print()
    
    en_docs = crawl_canada_ca(language="en", max_depth=2)
    
    print()
    print(f"✅ English crawl complete: {len(en_docs)} pages")
    print()
    
    # Save English results
    en_output = output_dir / f"canada_ca_en_{timestamp}.json"
    save_documents_to_json(en_docs, en_output)
    
    print()
    print("=" * 80)
    print("🇫🇷 FRENCH (FR) CRAWL")
    print("=" * 80)
    print()
    
    # Crawl French
    fr_docs = crawl_canada_ca(language="fr", max_depth=2)
    
    print()
    print(f"✅ French crawl complete: {len(fr_docs)} pages")
    print()
    
    # Save French results
    fr_output = output_dir / f"canada_ca_fr_{timestamp}.json"
    save_documents_to_json(fr_docs, fr_output)
    
    print()
    print("=" * 80)
    print("📊 INGESTION SUMMARY")
    print("=" * 80)
    print()
    print(f"English Pages:  {len(en_docs):>6}")
    print(f"French Pages:   {len(fr_docs):>6}")
    print(f"Total Pages:    {len(en_docs) + len(fr_docs):>6}")
    print()
    
    # Calculate statistics
    en_chars = sum(len(doc.text) for doc in en_docs)
    fr_chars = sum(len(doc.text) for doc in fr_docs)
    total_chars = en_chars + fr_chars
    
    print(f"English Chars:  {en_chars:>10,}")
    print(f"French Chars:   {fr_chars:>10,}")
    print(f"Total Chars:    {total_chars:>10,}")
    print()
    
    # Top domains/sections
    en_sections = {}
    for doc in en_docs:
        url = doc.metadata.get("source_url", "")
        # Extract section (e.g., /immigration/, /business/, etc.)
        parts = url.split("/")
        if len(parts) > 3:
            section = "/" + parts[3] + "/"
            en_sections[section] = en_sections.get(section, 0) + 1
    
    print("🔝 Top English Sections:")
    for section, count in sorted(en_sections.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {section:<30} {count:>4} pages")
    
    print()
    print("=" * 80)
    print("✅ INGESTION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Review extracted content in JSON files")
    print("2. Proceed to Phase 2: Chunking & Embedding")
    print("3. Index in Azure AI Search with bilingual support")
    print("4. Deploy canada.ca Q&A assistant")
    print()
    print(f"Output Directory: {output_dir.absolute()}")
    print()


if __name__ == "__main__":
    main()
