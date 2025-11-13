import { RAGEngine } from "../pipeline/engine.js";
import { TokenChunker } from "../chunkers/tokenChunker.js";
import { NaiveEmbedding } from "../embeddings/naive.js";
import { InMemoryVectorStore } from "../vector/inMemory.js";
import { BM25Index } from "../sparse/bm25.js";

async function main() {
  const engine = new RAGEngine({
    chunker: new TokenChunker({ maxTokens: 50, overlap: 10 }),
    embeddings: new NaiveEmbedding(32),
    vectorStore: new InMemoryVectorStore(),
    bm25: new BM25Index(),
    alpha: 0.5
  });

  await engine.ingest([
    { id: "d1", text: "# Intro\nBM25 is a ranking function used in search.\nIt uses term frequency and document frequency." },
    { id: "d2", text: "Cosine similarity compares angle between vectors in an embedding space." }
  ]);

  const res = await engine.retrieve("What is BM25?", 2);
  console.log(res.map(r => ({ id: r.id, score: r.score })));
}
void main();