import type { Reranker, Retrieved, Embeddings } from "../types.js";

/**
 * Maximal Marginal Relevance (MMR) reranker.
 * Selects items maximizing lambda*sim(query, doc) - (1-lambda)*max_sim(doc, selected).
 */
export class MMRReranker implements Reranker {
  constructor(private readonly emb: Embeddings, private readonly lambda = 0.5) {}

  async rerank(query: string, results: Retrieved[], topK: number): Promise<Retrieved[]> {
    if (results.length <= topK) return results;
    const texts = results.map((r) => r.text ?? "");
    const [qv, ...docVecs] = await this.emb.embed([query, ...texts]);
    const selected: number[] = [];
    const remaining = new Set(results.map((_, i) => i));

    while (selected.length < Math.min(topK, results.length) && remaining.size > 0) {
      let bestIdx = -1;
      let bestScore = -Infinity;

      for (const i of remaining) {
        const simQ = cosine(qv, docVecs[i]);
        let maxSimSel = 0;
        for (const j of selected) {
          const sim = cosine(docVecs[i], docVecs[j]);
          if (sim > maxSimSel) maxSimSel = sim;
        }
        const score = this.lambda * simQ - (1 - this.lambda) * maxSimSel;
        if (score > bestScore) {
          bestScore = score;
          bestIdx = i;
        }
      }
      if (bestIdx >= 0) {
        selected.push(bestIdx);
        remaining.delete(bestIdx);
      } else break;
    }

    return selected.map((i) => results[i]);
  }
}

function cosine(a: number[], b: number[]): number {
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