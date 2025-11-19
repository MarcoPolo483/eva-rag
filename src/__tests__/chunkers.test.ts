import { describe, it, expect } from "vitest";

import { TokenChunker } from "../chunkers/tokenChunker.js";
import { MarkdownChunker } from "../chunkers/markdownChunker.js";

describe("Chunkers", () => {
  it("TokenChunker splits with overlap", async () => {
    const chunker = new TokenChunker({ maxTokens: 5, overlap: 2 });
    const doc = { id: "x", text: "a b c d e f g h i j" };
    const chunks = await chunker.chunk(doc);
    expect(chunks.length).toBeGreaterThan(1);
    expect(chunks[0].id).toBe("x::0");
    expect(chunks[1].id).toBe("x::1");
  });

  it("MarkdownChunker splits by headings", async () => {
    const md = "# H1\nline1\nline2\n## H2\nline3\n";
    const chunker = new MarkdownChunker({ maxSectionTokens: 3 });
    const chunks = await chunker.chunk({ id: "m", text: md });
    expect(chunks.length).toBeGreaterThan(1);
    expect(chunks[0].id).toMatch(/m::m/);
  });
});