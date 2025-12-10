"""Detailed inspection of search results to verify relevance."""
import asyncio
from eva_rag.services.search_service import SearchService
from eva_rag.services.embedding_service import EmbeddingService
from uuid import UUID

async def inspect_search_quality():
    """Inspect actual search results for relevance."""
    search_service = SearchService()
    embedding_service = EmbeddingService()
    
    # Use same IDs as ingestion
    space_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
    
    test_queries = [
        {
            "query": "What are the EI voluntary leaving requirements?",
            "expected_content": ["Employment Insurance", "voluntary leaving", "quit", "resignation", "requirements"]
        },
        {
            "query": "IT-02 salary table step 3",
            "expected_content": ["IT-02", "salary", "step 3", "pay rate", "table"]
        },
        {
            "query": "Service Canada parental leave benefits",
            "expected_content": ["parental leave", "Service Canada", "benefits", "maternity"]
        }
    ]
    
    print("\n" + "="*100)
    print("SEARCH QUALITY INSPECTION")
    print("="*100)
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected = test["expected_content"]
        
        print(f"\n{'='*100}")
        print(f"QUERY {i}: {query}")
        print(f"EXPECTED KEYWORDS: {', '.join(expected)}")
        print(f"{'='*100}\n")
        
        # Generate embedding
        query_vector = embedding_service.generate_embedding(query)
        
        # Execute search
        results = search_service.hybrid_search(
            query=query,
            query_vector=query_vector,
            space_id=space_id,
            tenant_id=tenant_id,
            top_k=5,
        )
        
        print(f"📊 RESULTS: {len(results)} chunks returned\n")
        
        for j, result in enumerate(results, 1):
            content = result.get('content', '')
            doc_name = result.get('document_name', 'unknown')
            chunk_id = result.get('chunk_id', 'unknown')
            score = result.get('@search.score', 0)
            reranker_score = result.get('@search.rerankerScore', 'N/A')
            
            print(f"RESULT #{j}")
            print(f"   Document: {doc_name}")
            print(f"   Chunk ID: {chunk_id}")
            print(f"   Search Score: {score}")
            print(f"   Reranker Score: {reranker_score}")
            
            # Check for expected keywords
            content_lower = content.lower()
            found_keywords = [kw for kw in expected if kw.lower() in content_lower]
            missing_keywords = [kw for kw in expected if kw.lower() not in content_lower]
            
            if found_keywords:
                print(f"   ✅ Found keywords: {', '.join(found_keywords)}")
            if missing_keywords:
                print(f"   ❌ Missing keywords: {', '.join(missing_keywords)}")
            
            # Show content preview
            print(f"\n   CONTENT PREVIEW:")
            lines = content.split('\n')[:5]  # First 5 lines
            for line in lines:
                if line.strip():
                    print(f"   {line[:90]}...")
            
            print(f"\n   FULL CONTENT ({len(content)} chars):")
            print(f"   {content[:300]}...")
            
            # Relevance assessment
            if len(found_keywords) >= len(expected) // 2:
                print(f"\n   ✅ ASSESSMENT: Potentially relevant ({len(found_keywords)}/{len(expected)} keywords)")
            else:
                print(f"\n   ❌ ASSESSMENT: NOT RELEVANT ({len(found_keywords)}/{len(expected)} keywords)")
            
            print(f"\n{'-'*100}\n")
        
        # Overall query assessment
        total_relevant = sum(1 for r in results if any(kw.lower() in r.get('content', '').lower() for kw in expected))
        print(f"\n🎯 QUERY SUMMARY: {total_relevant}/{len(results)} results appear relevant")
        print(f"{'='*100}\n")

if __name__ == "__main__":
    asyncio.run(inspect_search_quality())
