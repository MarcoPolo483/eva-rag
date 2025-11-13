# eva-rag (Enterprise Edition)

Retrieval-Augmented Generation toolkit for EVA 2.0:
- Document chunking: token and markdown-aware
- Sparse retrieval: BM25 with stopword filtering
- Dense retrieval: in-memory vector store (cosine similarity)
- Hybrid retriever: weighted fusion of sparse and dense with normalization
- Simple reranker hook
- Ingest + retrieve pipeline with metadata filters
- Enterprise toolchain: ESLint v9 flat config, Prettier, Vitest coverage ≥80%, Husky + lint-staged

## Install
```bash
npm ci
npm run prepare
npm run check
npm run build
```

## Quick start
```ts
import { RAGEngine, TokenChunker, NaiveEmbedding, InMemoryVectorStore, BM25Index } from "./dist/index.js";

const engine = new RAGEngine({
  chunker: new TokenChunker({ maxTokens: 64, overlap: 8 }),
  embeddings: new NaiveEmbedding(32),
  vectorStore: new InMemoryVectorStore(),
  bm25: new BM25Index(),
  alpha: 0.5 // dense weight (0..1)
});

await engine.ingest([
  { id: "doc1", text: "Azure OpenAI enables enterprise-grade AI applications..." },
  { id: "doc2", text: "BM25 is a ranking function used by search engines..." }
]);

const results = await engine.retrieve("What is BM25 in search?", 3);
console.log(results.map(r => ({ id: r.id, score: r.score.toFixed(3) })));
```

## Design
- Chunkers return { id, docId, text, metadata } chunks for indexing.
- BM25Index indexes raw text per chunk. InMemoryVectorStore stores vectors per chunk.
- HybridRetriever queries BM25 and the vector store, normalizes scores, and fuses with weight `alpha`.
- RAGEngine coordinates ingest (chunk → embed → store) and retrieve (hybrid → optional rerank).

## Coverage
- Non-executable barrels excluded from coverage.
- Thresholds: 80% statements, 80% functions, 70% branches.

## License
MIT