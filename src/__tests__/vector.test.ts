import { describe, it, expect } from "vitest";
import { InMemoryVectorStore } from "../vector/inMemory.js";

describe("InMemoryVectorStore", () => {
  it("upserts and queries by cosine similarity", async () => {
    const vs = new InMemoryVectorStore();
    await vs.upsert([
      { id: "a", text: "aa", vector: [1, 0] },
      { id: "b", text: "bb", vector: [0, 1] }
    ]);
    const res = await vs.query([0.9, 0.1], 1);
    expect(res[0].id).toBe("a");
  });

  it("applies metadata filters", async () => {
    const vs = new InMemoryVectorStore();
    await vs.upsert([
      { id: "a", text: "aa", vector: [1, 0], metadata: { team: "x" } },
      { id: "b", text: "bb", vector: [0, 1], metadata: { team: "y" } }
    ]);
    const res = await vs.query([0, 1], 2, { team: "y" });
    expect(res[0].id).toBe("b");
    expect(res.length).toBe(1);
  });
});