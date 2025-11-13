/**
 * Simple IR metrics for RAG evaluation.
 */

export type Relevance = Record<string, Set<string> | string[]>; // queryId -> relevant docIds

export type RetrievedList = { queryId: string; results: { id: string }[] };

export function precisionAtK(retrieved: RetrievedList, relevant: Relevance, k: number): number {
  const rel = toSet(relevant[retrieved.queryId]);
  const top = retrieved.results.slice(0, k);
  const hits = top.filter((r) => rel.has(r.id)).length;
  return top.length ? hits / top.length : 0;
}

export function recallAtK(retrieved: RetrievedList, relevant: Relevance, k: number): number {
  const rel = toSet(relevant[retrieved.queryId]);
  if (rel.size === 0) return 0;
  const top = retrieved.results.slice(0, k);
  const hits = top.filter((r) => rel.has(r.id)).length;
  return hits / rel.size;
}

export function mrrAtK(retrieved: RetrievedList, relevant: Relevance, k: number): number {
  const rel = toSet(relevant[retrieved.queryId]);
  const top = retrieved.results.slice(0, k);
  for (let i = 0; i < top.length; i++) {
    if (rel.has(top[i].id)) return 1 / (i + 1);
  }
  return 0;
}

export function macroAverage(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function toSet(v: Set<string> | string[] | undefined): Set<string> {
  if (!v) return new Set();
  return v instanceof Set ? v : new Set(v);
}