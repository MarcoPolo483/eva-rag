import type { Embeddings, VectorStore } from "../types.js";

export interface TextGenerator {
  generateHypotheticalAnswer(query: string): Promise<string>;
}

/** Naive generator to avoid external dependencies. Replace with LLM-backed generator in production. */
export class NaiveHyDEGenerator implements TextGenerator {
  async generateHypotheticalAnswer(query: string): Promise<string> {
    return `This text hypothetically answers the following question: ${query}. It mentions key concepts and likely definitions.`;
  }
}

/**
 * HyDE query: generate a hypothetical answer, embed it, and query dense store.
 */
export async function hydeQuery(
  gen: TextGenerator,
  emb: Embeddings,
  vec: VectorStore,
  query: string,
  k: number,
  filter?: Record<string, unknown>
): Promise<{ id: string; score: number }[]> {
  const hypo = await gen.generateHypotheticalAnswer(query);
  const [hv] = await emb.embed([hypo]);
  return vec.query(hv, k, filter);
}