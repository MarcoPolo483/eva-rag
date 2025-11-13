import type { Chunker, Doc, Chunk } from "../types.js";

export type TokenChunkerOptions = {
  maxTokens?: number;
  overlap?: number;
};

export class TokenChunker implements Chunker {
  private maxTokens: number;
  private overlap: number;

  constructor(opts: TokenChunkerOptions = {}) {
    this.maxTokens = Math.max(1, opts.maxTokens ?? 200);
    this.overlap = Math.max(0, Math.min(this.maxTokens - 1, opts.overlap ?? 20));
  }

  async chunk(doc: Doc): Promise<Chunk[]> {
    const tokens = this.tokenize(doc.text);
    const chunks: Chunk[] = [];
    let idx = 0;
    let i = 0;
    while (idx < tokens.length) {
      const slice = tokens.slice(idx, idx + this.maxTokens);
      const text = slice.join(" ");
      chunks.push({ id: `${doc.id}::${i++}`, docId: doc.id, text, metadata: doc.metadata });
      if (idx + this.maxTokens >= tokens.length) break;
      idx += this.maxTokens - this.overlap;
    }
    if (chunks.length === 0) {
      chunks.push({ id: `${doc.id}::0`, docId: doc.id, text: doc.text, metadata: doc.metadata });
    }
    return chunks;
  }

  private tokenize(t: string): string[] {
    return t
      .replace(/\s+/g, " ")
      .trim()
      .split(" ")
      .filter(Boolean);
  }
}