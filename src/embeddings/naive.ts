import type { Embeddings } from "./embeddings.js";

export class NaiveEmbedding implements Embeddings {
  constructor(public dimensions = 32) {}

  async embed(texts: string[]): Promise<number[][]> {
    return texts.map((t) => this.hashToVector(t));
  }

  private hashToVector(t: string): number[] {
    const vec = new Array(this.dimensions).fill(0);
    const tokens = t.toLowerCase().split(/\W+/).filter(Boolean);
    for (const tok of tokens) {
      let h = 2166136261;
      for (let i = 0; i < tok.length; i++) {
        h ^= tok.charCodeAt(i);
        h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
      }
      const idx = Math.abs(h) % this.dimensions;
      vec[idx] += 1;
    }
    // L2 normalize
    const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0)) || 1;
    return vec.map((v) => v / norm);
  }
}