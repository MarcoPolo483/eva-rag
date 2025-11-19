import { describe, it, expect } from "vitest";

import { BM25Index } from "../sparse/bm25.js";

describe("BM25Index", () => {
  it("ranks documents by term relevance", async () => {
    const bm = new BM25Index();
    await bm.add([
      { id: "c1", docId: "d1", text: "search engines use bm25 ranking", metadata: {} },
      { id: "c2", docId: "d2", text: "vector similarity cosine distance", metadata: {} }
    ]);
    const res = await bm.search("bm25 ranking", 2);
    expect(res[0].id).toBe("c1");
    expect(res[0].score).toBeGreaterThan(0);
  });
});