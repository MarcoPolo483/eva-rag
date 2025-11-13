import type { Chunker, Doc, Chunk } from "../types.js";

/**
 * SentenceChunker groups sentences by maxChars. Useful to preserve semantic boundaries.
 */
export type SentenceChunkerOptions = {
  maxChars?: number;
  minSentencesPerChunk?: number;
};

export class SentenceChunker implements Chunker {
  private readonly maxChars: number;
  private readonly minSentences: number;

  constructor(opts: SentenceChunkerOptions = {}) {
    this.maxChars = Math.max(64, opts.maxChars ?? 800);
    this.minSentences = Math.max(1, opts.minSentencesPerChunk ?? 1);
  }

  async chunk(doc: Doc): Promise<Chunk[]> {
    const sentences = splitSentences(doc.text);
    const chunks: Chunk[] = [];
    let buf: string[] = [];
    let curLen = 0;
    let i = 0;

    for (const s of sentences) {
      if (curLen + s.length + 1 > this.maxChars && buf.length >= this.minSentences) {
        chunks.push({ id: `${doc.id}::s${i++}`, docId: doc.id, text: buf.join(" "), metadata: doc.metadata });
        buf = [];
        curLen = 0;
      }
      buf.push(s);
      curLen += s.length + 1;
    }
    if (buf.length) {
      chunks.push({ id: `${doc.id}::s${i++}`, docId: doc.id, text: buf.join(" "), metadata: doc.metadata });
    }
    if (chunks.length === 0) {
      chunks.push({ id: `${doc.id}::s0`, docId: doc.id, text: doc.text, metadata: doc.metadata });
    }
    return chunks;
  }
}

function splitSentences(t: string): string[] {
  const parts = t
    .replace(/\s+/g, " ")
    .split(/(?<=[\.!\?])\s+(?=[A-Z0-9])/g);
  return parts.map((p) => p.trim()).filter(Boolean);
}