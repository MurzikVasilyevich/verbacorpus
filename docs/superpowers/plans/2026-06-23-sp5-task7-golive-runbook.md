# SP5 Task 7 — Semantic Search Go-Live Runbook

> Expands Task 7 of `2026-06-23-ukr-proverbs-semantic-search.md` into an executable runbook.
> Tasks 1–6 (embed pipeline, Worker `/api/semantic`+`/api/similar`, client toggle+similar) are
> **built, tested, review-clean** on branch `feat/semantic-search` (head `ba58c79`, 8 commits ahead of main).
> This runbook is the remaining go-live: create the index, embed the corpus, verify, deploy, merge.

**Controller-run.** The deploy step is confirmed with the user at execution time.

---

## Prerequisite (user action — blocks everything below)

**Enable the Workers Paid plan** in the Cloudflare dashboard:
Workers & Pages → Plans (or Account → Billing) → **Workers Paid (~$5/mo)**.
Reason: the corpus is ~41M stored vector dimensions (40,444 × 1024), which exceeds the 5M free Vectorize tier.

Verify access before proceeding:
```bash
cd app && npx wrangler whoami            # account = Miwaniza@gmail.com's Account
npx wrangler vectorize list              # must NOT error with a plan/permission message
```
If `vectorize list` errors about plan/entitlement, Workers Paid is not active yet — stop.

---

## Step 1 — Create the Vectorize index

```bash
cd app
npx wrangler vectorize create proverbs-bge-m3 --dimensions=1024 --metric=cosine
npx wrangler vectorize list              # confirm proverbs-bge-m3 appears
```
The `VECTORIZE` binding in `wrangler.jsonc` already points at `proverbs-bge-m3` (added in Task 5).

## Step 2 — Validate batch size, then embed the corpus

The Workers AI per-request array limit for `bge-m3` is undocumented (final-review item I1), so prove the batch size on a small slice before the full 40,444 run.

**2a. Smoke the embed path on ~200 rows** (temporary tiny corpus, throwaway manifest):
```bash
cd /home/dmytro/github/ukr-proverbs-corpus
head -n 201 corpus.csv > /tmp/corpus_smoke.csv
CLOUDFLARE_ACCOUNT_ID=8ed62a6f8081b1e5db4ffd78d3c6b65f \
  .venv/bin/python -c "from embed.run import build_index, _workers_ai_embed, _wrangler_upsert, _wrangler_delete; \
print(build_index('/tmp/corpus_smoke.csv', '/tmp/manifest_smoke.json', \
  embed_fn=_workers_ai_embed, upsert_fn=_wrangler_upsert, delete_fn=_wrangler_delete, batch_size=100))"
```
Expect `{'upserted': 200, 'deleted': 0, 'total': 200}` and no HTTP 400/timeout. If the embed call rejects the 100-array, lower `batch_size` (try 50, then 25) until it succeeds; note the working value.

**2b. Full run** (uses the real manifest `embed/manifest.json`, the committed incremental state):
```bash
CLOUDFLARE_ACCOUNT_ID=8ed62a6f8081b1e5db4ffd78d3c6b65f \
  .venv/bin/python -m embed.run      # main() uses batch_size=100; edit run.py main() if 2a needed smaller
```
Expect `upserted=40444 deleted=0 total=40444`. Spend ≈ $0.04 (within the free daily Neuron allowance).
Sanity-check the index is populated:
```bash
cd app && npx wrangler vectorize get-vectors proverbs-bge-m3 --ids p000001   # returns a 1024-dim vector
```

**2c. Commit the manifest** (the incremental state for future re-runs):
```bash
cd /home/dmytro/github/ukr-proverbs-corpus
git add embed/manifest.json
git commit -m "feat(embed): index manifest (40,444 vectors embedded)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01UAc9viHnNneFn7pvDg9hcU"
```

## Step 3 — Preview deploy, smoke, tune the cutoff

```bash
cd app && node build.mjs && npx wrangler versions upload    # preview URL, production untouched
```
On the preview URL:
- `GET /api/semantic?q=<a meaning phrase, e.g. «не поспішай»>` → relevant proverbs with `score`.
- `GET /api/similar/p000001` → neighbours, self excluded.
- Browser: toggle «за змістом» on, search; open a proverb → «Схожі прислів'я» appears; go offline → toggle disables.

**Tune `SEMANTIC_MIN_SCORE`** (currently `0.4` in `app/src/index.ts`): if results are too loose, raise it (0.5–0.6); if good queries return empty, lower it. Edit → `node build.mjs` → `npx wrangler versions upload` → re-check. Commit the chosen value if changed.

## Step 4 — Deploy to production (confirm with user first)

```bash
cd app && node build.mjs && npx wrangler deploy
```
Smoke the production URL (`/api/semantic`, `/api/similar/p000001`, the toggle). Note: the service worker is `v2`; users may need one reload to pick up the new client (bump `sw.js` CACHE to `v3` if the client changed since the last deploy).

## Step 5 — README + finish the branch

- Add to `README.md`: a "Semantic search" section — the two endpoints, the «за змістом»/«Схожі» features, and the embed-pipeline run command (`CLOUDFLARE_ACCOUNT_ID=… python -m embed.run`) noting it requires Workers Paid + the index. Commit.
- Merge `feat/semantic-search` → `main`; push both remotes (origin needs `gh auth switch --user MurzikVasilyevich`; dmytro is SSH) via `superpowers:finishing-a-development-branch`.

## Rollback

- App regression: `cd app && npx wrangler rollback` (or re-deploy the prior version id).
- Bad/partial embeddings: re-run `python -m embed.run` after deleting `embed/manifest.json` to force a full re-`upsert` (overwrites every vector). To wipe entirely: `npx wrangler vectorize delete proverbs-bge-m3` then recreate (Step 1) + re-embed.

## Ongoing — when the corpus grows

Re-run `CLOUDFLARE_ACCOUNT_ID=… python -m embed.run`: the manifest diff embeds only new/changed proverbs and deletes removed ids (idempotent — unchanged corpus = no-op). No index recreation needed.
