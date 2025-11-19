import { describe, it, expect } from "vitest";

import { expandQueryPRF } from "../retrieval/queryExpansion.js";

describe("PRF Query Expansion", () => {
  it("adds salient terms from top docs", async () => {
    const corpus: Record<string, string> = {
      c1: "BM25 ranking function used in search engines",
      c2: "Cosine similarity vector space model"
    };
    const search = async (_q: string, _k: number) => [{ id: "c1", score: 1 }, { id: "c2", score: 0.5 }];
    const getText = (id: string) => corpus[id];
    const expanded = await expandQueryPRF("bm25", search, getText, { topDocs: 2, topTerms: 2 });
    expect(expanded).toMatch(/bm25/);
    expect(expanded.split(" ").length).toBeGreaterThan(1);
  });
});