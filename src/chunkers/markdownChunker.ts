import type { Chunker, Doc, Chunk } from "../types.js";

export type MarkdownChunkerOptions = {
  maxSectionTokens?: number;
};

export class MarkdownChunker implements Chunker {
  constructor(private readonly opts: MarkdownChunkerOptions = {}) {}

  async chunk(doc: Doc): Promise<Chunk[]> {
    const sections = splitByHeadings(doc.text);
    const maxTokens = Math.max(1, this.opts.maxSectionTokens ?? 400);
    const chunks: Chunk[] = [];
    let i = 0;
    for (const s of sections) {
      const tokens = s.split(/\s+/).filter(Boolean);
      for (let start = 0; start < tokens.length; start += maxTokens) {
        const text = tokens.slice(start, start + maxTokens).join(" ");
        chunks.push({ id: `${doc.id}::m${i++}`, docId: doc.id, text, metadata: doc.metadata });
      }
    }
    if (chunks.length === 0) {
      chunks.push({ id: `${doc.id}::m0`, docId: doc.id, text: doc.text, metadata: doc.metadata });
    }
    return chunks;
  }
}

function splitByHeadings(md: string): string[] {
  const lines = md.split(/\r?\n/);
  const sections: string[] = [];
  let cur: string[] = [];
  for (const line of lines) {
    if (/^#{1,6}\s+/.test(line) && cur.length > 0) {
      sections.push(cur.join("\n"));
      cur = [];
    }
    cur.push(line);
  }
  if (cur.length) sections.push(cur.join("\n"));
  return sections;
}