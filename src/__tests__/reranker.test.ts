import { describe, it, expect } from "vitest";

import { SimpleReranker } from "../rerankers/simpleReranker.js";

describe("SimpleReranker", () => {
  it("applies length penalty and returns topK", async () => {
    const rr = new SimpleReranker({ lengthPenalty: 0.01 });
    const results = await rr.rerank("q", [
      { id: "a", score: 1.0, text: "short" },
      { id: "b", score: 0.99, text: "long ".repeat(100) }
    ], 1);
    expect(results[0].id).toBe("a");
  });
});