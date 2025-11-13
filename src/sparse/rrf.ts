/**
 * Reciprocal Rank Fusion (RRF) for combining ranked lists.
 * Each list contributes 1 / (k + rank) to the fused score; lower rank index => higher contribution.
 */
export function rrfFuse(
  lists: Array<Array<{ id: string; score?: number }>>,
  kParam = 60,
  topK = 10
): { id: string; score: number }[] {
  const fused = new Map<string, number>();
  for (const list of lists) {
    for (let i = 0; i < list.length; i++) {
      const id = list[i].id;
      const rank = i + 1;
      const contrib = 1 / (kParam + rank);
      fused.set(id, (fused.get(id) ?? 0) + contrib);
    }
  }
  const out = Array.from(fused.entries()).map(([id, score]) => ({ id, score }));
  out.sort((a, b) => b.score - a.score);
  return out.slice(0, topK);
}