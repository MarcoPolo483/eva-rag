import { describe, it, expect } from "vitest";
import { precisionAtK, recallAtK, mrrAtK, macroAverage } from "../eval/metrics.js";

describe("Evaluation Metrics", () => {
  const relevant = { q1: ["a", "b"] };

  it("precision@k", () => {
    const p = precisionAtK({ queryId: "q1", results: [{ id: "a" }, { id: "x" }] }, relevant, 2);
    expect(p).toBe(0.5);
  });

  it("recall@k", () => {
    const r = recallAtK({ queryId: "q1", results: [{ id: "a" }, { id: "x" }] }, relevant, 2);
    expect(r).toBe(0.5);
  });

  it("mrr@k", () => {
    const m = mrrAtK({ queryId: "q1", results: [{ id: "x" }, { id: "a" }] }, relevant, 5);
    expect(m).toBe(1 / 2);
  });

  it("macroAverage", () => {
    expect(macroAverage([1, 0, 0.5])).toBeCloseTo(0.5);
  });
});