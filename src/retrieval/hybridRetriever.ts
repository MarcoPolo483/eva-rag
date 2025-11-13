import type { Retriever, Retrieved, VectorStore, Embeddings, SparseIndex } from "../types.js";
import { InMemoryVectorStore } from "../vector/inMemory.js";

export type HybridOptions = {
  alpha?: number; // dense weight
};

export class HybridRetriever implements Retriever {
  private alpha: number;

  constructor(
    private readonly vectorStore: VectorStore,
    private readonly embeddings: Embeddings,
    private readonly bm25: SparseIndex,
    opts: HybridOptions = {}
  ) {
    this.alpha = Math.min(1, Math.max(0, opts.alpha ?? 0.5));
  }

  async query(text: string, k: number, filter?: Record<string, unknown>): Promise<Retrieved[]> {
    const [qv] = await this.embeddings.embed([text]);
    const dense = await this.vectorStore.query(qv, k, filter);
    const sparse = await this.bm25.search(text, k);

    const denseNorm = normalize(dense.map((d) => ({ id: d.id, score: d.score })));
    const sparseNorm = normalize(sparse);

    const combined = new Map<string, { id: string; score: number }>();
    for (const d of denseNorm) combined.set(d.id, { id: d.id, score: this.alpha * d.score });
    for (const s of sparseNorm) {
      const prev = combined.get(s.id)?.score ?? 0;
      combined.set(s.id, { id: s.id, score: prev + (1 - this.alpha) * s.score });
    }

    const merged = Array.from(combined.values());
    merged.sort((a, b) => b.score - a.score);
    const top = merged.slice(0, k);

    // Optional: hydrate text/metadata if vector store provides it
    const vs = this.vectorStore as InMemoryVectorStore;
    return top.map((t) => ({
      id: t.id,
      score: t.score,
      text: typeof vs.getText === "function" ? vs.getText(t.id) : undefined
    }));
  }
}

function normalize(items: { id: string; score: number }[]): { id: string; score: number }[] {
  if (items.length === 0) return [];
  let min = Infinity,
    max = -Infinity;
  for (const it of items) {
    if (it.score < min) min = it.score;
    if (it.score > max) max = it.score;
  }
  if (max <= min) return items.map((x) => ({ ...x, score: 1 }));
  return items.map((x) => ({ ...x, score: (x.score - min) / (max - min) }));
}