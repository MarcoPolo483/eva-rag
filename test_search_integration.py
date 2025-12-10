"""Test Azure AI Search integration end-to-end.

This script validates:
1. Azure credentials are configured
2. Search index exists and is accessible
3. Query embedding generation works
4. Hybrid search returns results
5. Performance meets < 500ms target

Run: python test_search_integration.py
"""
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from uuid import UUID, uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eva_rag.config import settings
from eva_rag.services.embedding_service import EmbeddingService
from eva_rag.services.search_service import SearchService
from eva_rag.models.search import SearchRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_env_vars() -> dict[str, bool]:
    """Check if required Azure environment variables are set."""
    required_vars = {
        "AZURE_SEARCH_ENDPOINT": bool(settings.azure_search_endpoint),
        "AZURE_SEARCH_API_KEY": bool(settings.azure_search_api_key),
        "AZURE_OPENAI_ENDPOINT": bool(settings.azure_openai_endpoint),
        "AZURE_OPENAI_API_KEY": bool(settings.azure_openai_api_key),
    }
    return required_vars


async def test_search_service_init():
    """Test 1: Initialize SearchService and check index."""
    logger.info("=" * 80)
    logger.info("TEST 1: SearchService Initialization")
    logger.info("=" * 80)
    
    try:
        search_service = SearchService()
        logger.info("✅ SearchService initialized successfully")
        
        # Try to create index (should be idempotent)
        search_service.create_index_if_not_exists()
        logger.info("✅ Search index exists or was created")
        
        return search_service, True
    except Exception as e:
        logger.error(f"❌ SearchService initialization failed: {e}")
        return None, False


async def test_embedding_service():
    """Test 2: Generate query embedding."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: EmbeddingService - Query Embedding")
    logger.info("=" * 80)
    
    try:
        embedding_service = EmbeddingService()
        logger.info("✅ EmbeddingService initialized")
        
        test_query = "What are the EI voluntary leaving requirements?"
        logger.info(f"Query: '{test_query}'")
        
        start_time = time.time()
        embedding = embedding_service.generate_embedding(test_query)
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Embedding generated in {elapsed_ms:.1f}ms")
        logger.info(f"   Dimensions: {len(embedding)}")
        logger.info(f"   First 5 values: {embedding[:5]}")
        
        if len(embedding) != 1536:
            logger.error(f"❌ Expected 1536 dimensions, got {len(embedding)}")
            return embedding_service, False
        
        return embedding_service, True
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return None, False


async def test_hybrid_search(search_service: SearchService, embedding_service: EmbeddingService):
    """Test 3: Execute hybrid search query."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Hybrid Search")
    logger.info("=" * 80)
    
    test_queries = [
        "What are the EI voluntary leaving requirements?",
        "IT-02 salary table step 3",
        "Service Canada parental leave benefits",
    ]
    
    # Create test IDs (use default test values from ingestion)
    space_id = UUID("00000000-0000-0000-0000-000000000000")
    tenant_id = UUID("00000000-0000-0000-0000-000000000000")
    
    results_summary = []
    
    for query in test_queries:
        logger.info(f"\nQuery: '{query}'")
        
        try:
            start_time = time.time()
            
            # Generate query embedding
            query_vector = embedding_service.generate_embedding(query)
            
            # Execute hybrid search
            results = search_service.hybrid_search(
                query=query,
                query_vector=query_vector,
                space_id=str(space_id),
                tenant_id=str(tenant_id),
                top_k=5,
            )
            elapsed_ms = (time.time() - start_time) * 1000
            
            logger.info(f"✅ Search completed in {elapsed_ms:.1f}ms")
            logger.info(f"   Results: {len(results)} chunks")
            
            if results:
                for i, result in enumerate(results[:3], 1):
                    logger.info(f"   {i}. Score: {result.get('@search.score', 0):.3f}")
                    logger.info(f"      Document: {result.get('document_name', 'N/A')}")
                    logger.info(f"      Content: {result.get('content', '')[:100]}...")
            else:
                logger.warning("   ⚠️ No results found (index might be empty)")
            
            results_summary.append({
                "query": query,
                "elapsed_ms": elapsed_ms,
                "result_count": len(results),
                "within_target": elapsed_ms < 500,
            })
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            results_summary.append({
                "query": query,
                "elapsed_ms": 0,
                "result_count": 0,
                "within_target": False,
                "error": str(e),
            })
    
    # Performance summary
    logger.info("\n" + "-" * 80)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("-" * 80)
    
    for summary in results_summary:
        status = "✅" if summary["within_target"] else "❌"
        logger.info(
            f"{status} {summary['query'][:40]:40} | "
            f"{summary['elapsed_ms']:6.1f}ms | "
            f"{summary['result_count']:2} results"
        )
    
    avg_latency = sum(s["elapsed_ms"] for s in results_summary) / len(results_summary)
    all_within_target = all(s["within_target"] for s in results_summary)
    
    logger.info("-" * 80)
    logger.info(f"Average latency: {avg_latency:.1f}ms (target: < 500ms)")
    
    if all_within_target:
        logger.info("✅ All queries within performance target")
        return True
    else:
        logger.warning("⚠️ Some queries exceeded 500ms target")
        return False


async def test_empty_index_behavior(search_service: SearchService, embedding_service: EmbeddingService):
    """Test 4: Check behavior with empty index."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Empty Index Behavior")
    logger.info("=" * 80)
    
    try:
        # Query that should return no results
        query = "nonexistent test query xyz123"
        query_vector = embedding_service.generate_embedding(query)
        
        results = search_service.hybrid_search(
            query=query,
            query_vector=query_vector,
            space_id=str(uuid4()),
            tenant_id=str(uuid4()),
            top_k=5,
        )
        
        logger.info(f"✅ Empty query handled gracefully: {len(results)} results")
        return True
    except Exception as e:
        logger.error(f"❌ Empty index test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("EVA-RAG Azure AI Search Integration Test")
    logger.info("=" * 80)
    
    # Check environment variables
    logger.info("\n📋 ENVIRONMENT CHECK")
    logger.info("-" * 80)
    env_vars = check_env_vars()
    for var_name, is_set in env_vars.items():
        status = "✅" if is_set else "❌"
        logger.info(f"{status} {var_name}")
    
    if not all(env_vars.values()):
        logger.error("\n❌ Missing required environment variables!")
        logger.error("   Copy .env.example to .env and configure Azure credentials")
        return False
    
    # Run tests
    all_passed = True
    
    # Test 1: SearchService initialization
    search_service, test1_passed = await test_search_service_init()
    all_passed = all_passed and test1_passed
    
    if not test1_passed:
        logger.error("\n❌ SearchService initialization failed - cannot continue")
        return False
    
    # Test 2: EmbeddingService
    embedding_service, test2_passed = await test_embedding_service()
    all_passed = all_passed and test2_passed
    
    if not test2_passed:
        logger.warning("\n⚠️ EmbeddingService test failed - skipping search tests")
        return False
    
    # Test 3: Hybrid search
    test3_passed = await test_hybrid_search(search_service, embedding_service)
    all_passed = all_passed and test3_passed
    
    # Test 4: Empty index behavior
    test4_passed = await test_empty_index_behavior(search_service, embedding_service)
    all_passed = all_passed and test4_passed
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
        logger.info("\nNext steps:")
        logger.info("1. Run ingestion to index existing documents")
        logger.info("2. Test search with real queries")
        logger.info("3. Implement cross-encoder reranking")
    else:
        logger.warning("⚠️ SOME TESTS FAILED")
        logger.warning("\nTroubleshooting:")
        logger.warning("1. Check Azure credentials in .env")
        logger.warning("2. Verify Azure AI Search service is running")
        logger.warning("3. Check network connectivity to Azure")
        logger.warning("4. Review error logs above")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
