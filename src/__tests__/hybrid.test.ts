import { describe, it, expect } from "vitest";

import { HybridRetriever } from "../retrieval/hybridRetriever.js";
import { BM25Index } from "../sparse/bm25.js";
import { InMemoryVectorStore } from "../vector/inMemory.js";
import { NaiveEmbedding } from "../embeddings/naive.js";

describe("HybridRetriever", () => {
  it("combines dense and sparse scores", async () => {
    const bm = new BM25Index();
    const vs = new InMemoryVectorStore();
    const emb = new NaiveEmbedding(8);

    // Two chunks: one matches sparse, the other matches dense
    const chunks = [
      { id: "sparse", docId: "d1", text: "bm25 ranking function", metadata: {} },
      { id: "dense", docId: "d2", text: "vector cosine space", metadata: {} }
    ];
    await bm.add(chunks);
    const vectors = await emb.embed(chunks.map((c) => c.text));
    await vs.upsert(chunks.map((c, i) => ({ id: c.id, text: c.text, vector: vectors[i] })));

    const retr = new HybridRetriever(vs, emb, bm, { alpha: 0.5 });
    const res = await retr.query("bm25 ranking", 2);
    const ids = res.map((r) => r.id);
    expect(ids).toContain("sparse");
  });
});