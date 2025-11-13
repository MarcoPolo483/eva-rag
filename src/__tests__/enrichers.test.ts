import { describe, it, expect } from "vitest";
import { enrichChunks, dedupeChunksByHash } from "../pipeline/enrichers.js";

describe("Enrichers", () => {
  it("adds metadata and deduplicates by hash", () => {
    const chunks = [
      { id: "a", docId: "d", text: "hello" },
      { id: "b", docId: "d", text: "hello" },
      { id: "c", docId: "d", text: "different" }
    ];
    const enriched = enrichChunks(chunks as any);
    const deduped = dedupeChunksByHash(enriched as any);
    expect(enriched[0].metadata?.hash).toBeDefined();
    expect(deduped.length).toBe(2);
  });
});