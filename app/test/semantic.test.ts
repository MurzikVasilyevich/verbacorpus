import { describe, it, expect } from "vitest";
import { mapMatches, type Match } from "../src/shared/semantic";
import { type Proverb } from "../src/shared/corpus";

const P = (id: string, category: string[], sources: string[]): Proverb =>
  ({ id, text: id, modern_text: id, category, sources, variant_group: "" });
const byId = new Map<string, Proverb>([
  ["p1", P("p1", ["fate_luck"], ["Franko1901"])],
  ["p2", P("p2", ["work_labor"], ["Bobkova"])],
  ["p3", P("p3", ["work_labor"], ["Franko1901"])],
]);
const matches: Match[] = [
  { id: "p1", score: 0.9 }, { id: "p2", score: 0.7 }, { id: "p3", score: 0.3 }, { id: "zz", score: 0.95 },
];

describe("mapMatches", () => {
  it("maps, skips unknown ids, preserves order + score", () => {
    const r = mapMatches(matches, byId, {});
    expect(r.results.map((x) => x.id)).toEqual(["p1", "p2", "p3"]); // zz dropped
    expect(r.results[0].score).toBe(0.9);
    expect(r.total).toBe(3);
  });
  it("applies minScore", () => {
    expect(mapMatches(matches, byId, { minScore: 0.5 }).results.map((x) => x.id)).toEqual(["p1", "p2"]);
  });
  it("applies category + source filters", () => {
    expect(mapMatches(matches, byId, { category: "work_labor" }).results.map((x) => x.id)).toEqual(["p2", "p3"]);
    expect(mapMatches(matches, byId, { source: "Franko1901" }).results.map((x) => x.id)).toEqual(["p1", "p3"]);
  });
  it("excludeId + limit", () => {
    expect(mapMatches(matches, byId, { excludeId: "p1", limit: 1 }).results.map((x) => x.id)).toEqual(["p2"]);
    expect(mapMatches(matches, byId, { excludeId: "p1" }).total).toBe(2);
  });
});
