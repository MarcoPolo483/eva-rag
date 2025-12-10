"""
Test the WebCrawlerLoader with a limited crawl.

This script tests the canada.ca crawler with minimal depth/pages
to validate functionality before running full ingestion.

Usage:
    poetry run python test_canada_ca_crawler.py
"""
from eva_rag.loaders.web_crawler_loader import WebCrawlerLoader


def test_limited_crawl():
    """Test crawler with 1-layer depth and max 10 pages."""
    
    print("=" * 80)
    print("TESTING CANADA.CA WEB CRAWLER")
    print("=" * 80)
    print()
    print("Test Configuration:")
    print("  - Max Depth: 1 (homepage + direct links only)")
    print("  - Max Pages: 10 (limited test)")
    print("  - Language: English")
    print("  - URL: https://www.canada.ca/en.html")
    print()
    
    loader = WebCrawlerLoader(
        max_depth=1,  # Limited depth for testing
        same_domain_only=True,
        delay_seconds=0.5,
        max_pages=10,  # Only 10 pages for testing
    )
    
    start_url = "https://www.canada.ca/en.html"
    
    print("Starting test crawl...")
    print()
    
    try:
        docs = loader.load_from_url(start_url)
        
        print()
        print("=" * 80)
        print("TEST RESULTS - SUCCESS")
        print("=" * 80)
        print()
        print(f"Pages Crawled: {len(docs)}")
        print()
        
        if docs:
            print("Sample Document (First Page):")
            print("-" * 80)
            doc = docs[0]
            print(f"Source URL: {doc.metadata.get('source_url', 'N/A')}")
            print(f"Content Length: {len(doc.text):,} characters")
            print(f"Page Count: {doc.page_count}")
            print(f"Metadata: {doc.metadata}")
            print()
            print("Content Preview (first 500 chars):")
            print(doc.text[:500])
            print("...")
            print()
            
            # Statistics
            total_chars = sum(len(d.text) for d in docs)
            avg_chars = total_chars / len(docs)
            
            print("Statistics:")
            print(f"  Total Characters: {total_chars:,}")
            print(f"  Average per Page: {avg_chars:,.0f}")
            print()
            
            print("PASS: TEST PASSED - Crawler is working correctly")
            print()
            print("Next Steps:")
            print("1. Review extracted content above")
            print("2. If satisfied, run full ingestion:")
            print("   poetry run python ingest_canada_ca.py")
            
        else:
            print("WARNING: No documents extracted - check URL or connectivity")
        
    except Exception as e:
        print()
        print("=" * 80)
        print("TEST FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_limited_crawl()
