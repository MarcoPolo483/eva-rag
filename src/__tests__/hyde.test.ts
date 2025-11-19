import { describe, it, expect } from "vitest";

import { NaiveHyDEGenerator, hydeQuery } from "../retrieval/hyde.js";
import { InMemoryVectorStore } from "../vector/inMemory.js";
import { NaiveEmbedding } from "../embeddings/naive.js";

describe("HyDE query", () => {
  it("queries vector store using hypothetical answer embedding", async () => {
    const gen = new NaiveHyDEGenerator();
    const emb = new NaiveEmbedding(8);
    const vs = new InMemoryVectorStore();
    const docs = ["This text hypothetically answers the following question: What is BM25?", "Another domain"];
    const vecs = await emb.embed(docs);
    await vs.upsert([
      { id: "a", text: docs[0], vector: vecs[0] },
      { id: "b", text: docs[1], vector: vecs[1] }
    ]);
    const res = await hydeQuery(gen, emb, vs, "What is BM25?", 1);
    expect(res[0].id).toBe("a");
  });
});