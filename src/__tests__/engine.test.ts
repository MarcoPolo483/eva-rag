import { describe, it, expect } from "vitest";

import { RAGEngine } from "../pipeline/engine.js";
import { TokenChunker } from "../chunkers/tokenChunker.js";
import { NaiveEmbedding } from "../embeddings/naive.js";
import { InMemoryVectorStore } from "../vector/inMemory.js";
import { BM25Index } from "../sparse/bm25.js";
import { SimpleReranker } from "../rerankers/simpleReranker.js";

describe("RAGEngine", () => {
  it("ingests and retrieves relevant chunks", async () => {
    const engine = new RAGEngine({
      chunker: new TokenChunker({ maxTokens: 10, overlap: 2 }),
      embeddings: new NaiveEmbedding(16),
      vectorStore: new InMemoryVectorStore(),
      bm25: new BM25Index(),
      alpha: 0.5,
      reranker: new SimpleReranker({ lengthPenalty: 0 })
    });

    await engine.ingest([
      { id: "d1", text: "BM25 search ranking and retrieval model in IR." },
      { id: "d2", text: "Embeddings and cosine similarity for dense retrieval." }
    ]);

    const res = await engine.retrieve("bm25 ranking", 2);
    expect(res.length).toBeGreaterThan(0);
    expect(res[0].id).toContain("d1");
  });
});