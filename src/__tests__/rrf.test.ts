import { describe, it, expect } from "vitest";

import { rrfFuse } from "../sparse/rrf.js";

describe("RRF fusion", () => {
  it("fuses two ranked lists preferring items appearing in both", () => {
    const a = [{ id: "d1" }, { id: "d2" }, { id: "d3" }];
    const b = [{ id: "d3" }, { id: "d1" }, { id: "d4" }];
    const fused = rrfFuse([a, b], 60, 3);
    expect(fused[0].id).toBe("d1"); // appears in both near top
    expect(fused.length).toBe(3);
  });
});