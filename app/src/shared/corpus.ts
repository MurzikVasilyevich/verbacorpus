export type Proverb = {
  id: string;
  text: string;
  modern_text: string;
  category: string[];
  sources: string[];
  variant_group: string;
};

export type SearchOpts = {
  q?: string; category?: string; source?: string; limit?: number; offset?: number;
};

export function searchProverbs(all: Proverb[], opts: SearchOpts): { total: number; results: Proverb[] } {
  const q = (opts.q ?? "").trim().toLowerCase();
  const limit = Math.min(Math.max(opts.limit ?? 50, 1), 200);
  const offset = Math.max(opts.offset ?? 0, 0);
  const matched = all.filter((p) => {
    if (q && !(p.text.toLowerCase().includes(q) || p.modern_text.toLowerCase().includes(q))) return false;
    if (opts.category && !p.category.includes(opts.category)) return false;
    if (opts.source && !p.sources.includes(opts.source)) return false;
    return true;
  });
  return { total: matched.length, results: matched.slice(offset, offset + limit) };
}

export function randomProverb(
  all: Proverb[],
  opts: { category?: string; source?: string },
  rnd: () => number = Math.random,
): Proverb | null {
  const pool = searchProverbs(all, { category: opts.category, source: opts.source, limit: 200000 }).results;
  if (pool.length === 0) return null;
  return pool[Math.floor(rnd() * pool.length)];
}
