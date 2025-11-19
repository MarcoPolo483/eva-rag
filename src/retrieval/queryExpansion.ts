import { defaultStopwords } from "../util/stopwords.js";

/**
 * Pseudo-Relevance Feedback (PRF) query expansion:
 * - Take topK BM25 results
 * - Extract term frequencies from their texts via getText(id)
 * - Add top terms not in stoplist to the original query
 */
export type PRFOptions = {
  topDocs?: number;
  topTerms?: number;
  stopwords?: Set<string>;
};

export async function expandQueryPRF(
  original: string,
  search: (q: string, k: number) => Promise<{ id: string; score: number }[]>,
  getText: (id: string) => string | undefined,
  opts: PRFOptions = {}
): Promise<string> {
  const topDocs = Math.max(1, opts.topDocs ?? 5);
  const topTerms = Math.max(1, opts.topTerms ?? 5);
  const stop = opts.stopwords ?? defaultStopwords;

  const results = await search(original, topDocs);
  const tf = new Map<string, number>();
  for (const r of results) {
    const t = getText(r.id) ?? "";
    for (const w of tokenize(t)) {
      if (stop.has(w)) continue;
      tf.set(w, (tf.get(w) ?? 0) + 1);
    }
  }
  const terms = Array.from(tf.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, topTerms)
    .map(([w]) => w);

  const expanded = Array.from(new Set([...tokenize(original), ...terms])).join(" ");
  return expanded || original;
}

function tokenize(t: string): string[] {
  return t.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}