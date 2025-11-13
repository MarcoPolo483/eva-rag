import type { Chunk } from "../types.js";
import { hashText } from "../util/hash.js";

/**
 * Adds standard metadata to chunks: hash, charCount, tokenApprox
 */
export function enrichChunks(chunks: Chunk[]): Chunk[] {
  return chunks.map((c) => {
    const charCount = c.text.length;
    const tokenApprox = Math.max(1, Math.ceil(charCount / 4)); // naive heuristic
    const hash = hashText(c.text);
    return {
      ...c,
      metadata: { ...(c.metadata ?? {}), charCount, tokenApprox, hash }
    };
  });
}

/**
 * Deduplicate chunks by metadata.hash (computed by enrichChunks).
 */
export function dedupeChunksByHash(chunks: Chunk[]): Chunk[] {
  const seen = new Set<string>();
  const out: Chunk[] = [];
  for (const c of chunks) {
    const h = String((c.metadata as any)?.hash ?? hashText(c.text));
    if (seen.has(h)) continue;
    seen.add(h);
    out.push(c);
  }
  return out;
}