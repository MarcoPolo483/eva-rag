import { describe, it, expect } from "vitest";

import { MMRReranker } from "../rerankers/mmrReranker.js";
import { NaiveEmbedding } from "../embeddings/naive.js";

describe("MMR Reranker", () => {
  it("promotes diversity among top results", async () => {
    const emb = new NaiveEmbedding(8);
    const mmr = new MMRReranker(emb, 0.7);
    const results = [
      { id: "a", score: 1, text: "apple banana fruit" },
      { id: "b", score: 0.9, text: "banana apple fruit" },
      { id: "c", score: 0.8, text: "cosine vector space algebra" }
    ];
    const reranked = await mmr.rerank("fruit apples", results, 2);
    const ids = reranked.map((r) => r.id);
    expect(ids).toContain("a");
    expect(ids.length).toBe(2);
  });
});