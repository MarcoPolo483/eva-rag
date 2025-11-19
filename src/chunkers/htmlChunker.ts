import type { Chunker, Doc, Chunk } from "../types.js";

import { TokenChunker } from "./tokenChunker.js";

/**
 * HtmlChunker strips simple HTML tags and entities, then delegates to TokenChunker.
 * It is robust enough for well-formed HTML fragments and emails.
 */
export type HtmlChunkerOptions = {
  maxTokens?: number;
  overlap?: number;
  stripScripts?: boolean;
  stripStyles?: boolean;
};

export class HtmlChunker implements Chunker {
  private readonly tokenChunker: TokenChunker;
  private readonly opts: HtmlChunkerOptions;

  constructor(opts: HtmlChunkerOptions = {}) {
    this.opts = opts;
    this.tokenChunker = new TokenChunker({ maxTokens: opts.maxTokens, overlap: opts.overlap });
  }

  async chunk(doc: Doc): Promise<Chunk[]> {
    const text = this.cleanHtml(doc.text, this.opts);
    return this.tokenChunker.chunk({ ...doc, text });
  }

  private cleanHtml(html: string, opts: HtmlChunkerOptions): string {
    let s = html;
    if (opts.stripScripts !== false) {
      s = s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ");
    }
    if (opts.stripStyles !== false) {
      s = s.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ");
    }
    // Remove tags
    s = s.replace(/<\/?[^>]+>/g, " ");
    // Decode a few common entities
    s = s
      .replace(/&nbsp;/gi, " ")
      .replace(/&amp;/gi, "&")
      .replace(/&lt;/gi, "<")
      .replace(/&gt;/gi, ">")
      .replace(/&quot;/gi, '"')
      .replace(/&#39;/gi, "'");
    // Collapse whitespace
    s = s.replace(/\s+/g, " ").trim();
    return s;
  }
}