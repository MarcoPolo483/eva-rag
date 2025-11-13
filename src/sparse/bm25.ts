import type { SparseIndex, Chunk } from "../types.js";

type Posting = { id: string; tf: number; dl: number };

const STOP = new Set([
  "the","a","an","and","or","but","if","then","else","of","to","in","on","for","with","as","by","is","are","was","were","be","this","that","it","at","from"
]);

export class BM25Index implements SparseIndex {
  private index = new Map<string, Posting[]>();
  private docLengths = new Map<string, number>();
  private N = 0;
  private avgdl = 0;

  async add(chunks: Chunk[]): Promise<void> {
    for (const c of chunks) {
      this.N++;
      const tokens = tokenize(c.text);
      const dl = tokens.length;
      this.docLengths.set(c.id, dl);
      const freq = new Map<string, number>();
      for (const t of tokens) freq.set(t, (freq.get(t) ?? 0) + 1);
      for (const [term, tf] of freq) {
        const arr = this.index.get(term) ?? [];
        arr.push({ id: c.id, tf, dl });
        this.index.set(term, arr);
      }
    }
    // Recompute avgdl
    let sum = 0;
    for (const dl of this.docLengths.values()) sum += dl;
    this.avgdl = this.N ? sum / this.N : 0;
  }

  async search(query: string, k: number): Promise<{ id: string; score: number }[]> {
    const terms = tokenize(query);
    const scores = new Map<string, number>();
    const k1 = 1.5;
    const b = 0.75;
    for (const term of terms) {
      const postings = this.index.get(term);
      if (!postings) continue;
      const df = postings.length;
      const idf = Math.log((this.N - df + 0.5) / (df + 0.5) + 1);
      for (const p of postings) {
        const score = (idf * p.tf * (k1 + 1)) / (p.tf + k1 * (1 - b + (b * p.dl) / (this.avgdl || 1)));
        scores.set(p.id, (scores.get(p.id) ?? 0) + score);
      }
    }
    const result = Array.from(scores.entries()).map(([id, score]) => ({ id, score }));
    result.sort((a, b) => b.score - a.score);
    return result.slice(0, k);
  }
}

function tokenize(t: string): string[] {
  return t
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean)
    .filter((w) => !STOP.has(w));
}