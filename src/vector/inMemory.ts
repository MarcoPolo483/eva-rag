import type { VectorStore, Vector } from "../types.js";

type Entry = { id: string; vector: Vector; metadata?: Record<string, unknown>; text: string };

export class InMemoryVectorStore implements VectorStore {
  private data = new Map<string, Entry>();

  async upsert(items: { id: string; text: string; vector: Vector; metadata?: Record<string, unknown> }[]): Promise<void> {
    for (const it of items) {
      this.data.set(it.id, { id: it.id, vector: it.vector, metadata: it.metadata, text: it.text });
    }
  }

  async query(vector: Vector, k: number, filter?: Record<string, unknown>) {
    const results: { id: string; score: number; metadata?: Record<string, unknown> }[] = [];
    for (const e of this.data.values()) {
      if (filter && !matchesFilter(e.metadata, filter)) continue;
      const s = cosine(vector, e.vector);
      results.push({ id: e.id, score: s, metadata: e.metadata });
    }
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, k);
  }

  getText(id: string): string | undefined {
    return this.data.get(id)?.text;
  }
}

function cosine(a: Vector, b: Vector): number {
  const n = Math.min(a.length, b.length);
  let dot = 0,
    na = 0,
    nb = 0;
  for (let i = 0; i < n; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  const denom = Math.sqrt(na) * Math.sqrt(nb);
  return denom ? dot / denom : 0;
}

function matchesFilter(meta: Record<string, unknown> | undefined, filter: Record<string, unknown>): boolean {
  if (!filter) return true;
  if (!meta) return false;
  for (const [k, v] of Object.entries(filter)) {
    if (meta[k] !== v) return false;
  }
  return true;
}