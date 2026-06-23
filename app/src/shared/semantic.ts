import { type Proverb } from "./corpus";

export type Match = { id: string; score: number };
export type Scored = Proverb & { score: number };

export function mapMatches(
  matches: Match[],
  byId: Map<string, Proverb>,
  opts: { category?: string; source?: string; minScore?: number; limit?: number; excludeId?: string },
): { total: number; results: Scored[] } {
  const minScore = opts.minScore ?? 0;
  const limit = Math.min(Math.max(opts.limit ?? 50, 1), 200);
  const matched: Scored[] = [];
  for (const m of matches) {
    if (m.score < minScore) continue;
    if (m.id === opts.excludeId) continue;
    const p = byId.get(m.id);
    if (!p) continue;
    if (opts.category && !p.category.includes(opts.category)) continue;
    if (opts.source && !p.sources.includes(opts.source)) continue;
    matched.push({ ...p, score: m.score });
  }
  return { total: matched.length, results: matched.slice(0, limit) };
}
