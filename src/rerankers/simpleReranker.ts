import type { Reranker, Retrieved } from "../types.js";

export type SimpleRerankerOptions = {
  lengthPenalty?: number; // small penalty to long chunks
};

export class SimpleReranker implements Reranker {
  constructor(private readonly opts: SimpleRerankerOptions = {}) {}
  async rerank(_query: string, results: Retrieved[], topK: number): Promise<Retrieved[]> {
    const penalty = this.opts.lengthPenalty ?? 0.0;
    const scored = results.map((r) => {
      const len = r.text?.length ?? 0;
      return { ...r, score: r.score - penalty * Math.sqrt(len) };
    });
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, topK);
  }
}