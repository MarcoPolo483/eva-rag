import { describe, it, expect } from "vitest";
import { InMemoryVectorStore } from "../vector/inMemory.js";
import { snapshot, restore } from "../persistence/vectorSnapshot.js";

describe("VectorStore snapshot/restore", () => {
  it("round-trips entries", async () => {
    const vs = new InMemoryVectorStore();
    await vs.upsert([
      { id: "x", text: "hello", vector: [1, 0] },
      { id: "y", text: "world", vector: [0, 1] }
    ]);
    const snap = snapshot(vs);
    const vs2 = new InMemoryVectorStore();
    await restore(vs2, snap);
    const res = await vs2.query([1, 0], 1);
    expect(res[0].id).toBe("x");
  });
});