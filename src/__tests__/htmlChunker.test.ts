import { describe, it, expect } from "vitest";
import { HtmlChunker } from "../chunkers/htmlChunker.js";

describe("HtmlChunker", () => {
  it("strips tags and scripts/styles", async () => {
    const html = `
      <html><head><style>.a{}</style><script>var x=1;</script></head>
      <body><h1>Hello</h1><p>World &amp; Co.</p></body></html>
    `;
    const ch = new HtmlChunker({ maxTokens: 10, overlap: 0 });
    const chunks = await ch.chunk({ id: "d", text: html });
    expect(chunks.length).toBeGreaterThan(0);
    expect(chunks[0].text).toMatch(/Hello World & Co\./);
  });
});