# Ukrainian Proverbs Corpus — Expansion, Phase B: full Bobkova via tesseract OCR

**Date:** 2026-06-23
**Status:** Approved (design)
**Sub-project:** 3 of 4, **Phase B** of 3 (3a Bobkova ingest done · 3b full-book · 3c archive.org)
**Repo:** `ukr-proverbs-corpus` (existing)
**Depends on:** SP1 (corpus), SP2 (enrichment), SP3a (Bobkova ingest + source-addition pattern) — all done.

---

## 1. Feasibility outcome (assessed + measured before this spec)

The Bobkova source PDF (Dropbox, 525 pages, content pp.19–516) has an embedded text layer, but
`pdftotext` output is corrupted by justification: **~44% of proverbs have intra-word spaces**
(«тяж кої»→«тяжкої», «Ж иве»→«Живе»). A measured comparison on page 25 showed **tesseract OCR of the
rendered page image is cleaner** — it reads glyphs, so there is **no spacing artifact** («Іржа»,
«Живе» come out correct); its only defects are occasional capitalization/dash errors and OCR-garbage
on the `*` separator lines (trivially droppable). A pure dictionary-based space-restoration of the
text layer was tested and **failed** on multi-fragment cases, so the OCR path is preferred.

**Decision:** extract via **tesseract**, not the text layer. tesseract-ocr 5.3.4 + `ukr` are installed.

## 2. Scope

OCR the full Bobkova book, segment + spell-check **deterministically** (zero LLM tokens), LLM-verify
only the flagged-suspect residuals, and **replace** `data/sources/bobkova.csv` with the full book
(superseding SP3a's 760), then re-ingest via the SP3a pattern — preserving all existing SP2 enrichment
and categorizing only net-new.

**Out of scope:** archive.org (3c); the text-layer/`pdftotext` path; front/back matter outside pp.19–516.

## 3. OCR (controller — token-free)

- **PDF:** download from the Dropbox URL in the WIP `sources.csv`; vendor as `data/sources/bobkova.pdf`
  (5.4 MB, committed for provenance).
- **Rasterize + OCR:** `pdftoppm -r 300 -png` per page (pp.19–516) → `tesseract <page>.png -l ukr` →
  one raw OCR text blob per page (page ref = PDF page number). Local compute (~15–25 min), **no tokens**.

## 4. Clean (deterministic first; LLM only for residuals)

**4a. Rule-based segmentation** (`expand/segment.py`, TDD) — per page, turn raw OCR text into a proverb
list: drop separator-junk lines (short lines that are mostly non-letters, e.g. «ж», «»», «.о»), drop
pure-digit page-number lines, drop ALL-CAPS section headers, join soft-wrapped continuation lines, and
emit one entry per proverb.

**4b. Dictionary spell-check / flag** (`expand/spellcheck.py`, TDD) — build a Ukrainian word set from
(i) the existing corpus `text` (~32K types) and (ii) the broad **hunspell-uk** dictionary
(`/usr/share/hunspell/uk_UA.dic`, installed non-interactively). A proverb is **clean** if all its word
tokens are known; otherwise it is **flagged** (likely tesseract error). Clean proverbs pass through
untouched — **no tokens**.

**4c. LLM-verify residuals** (controller Workflow) — only the **flagged** proverbs go to a small batched
haiku pass that fixes OCR errors (returning corrected text), preserving meaning; Bobkova is modern, so
no modernization. File-based handoff with the SP2/SP3a safeguards (coverage, id-level repair,
line-salvage). Expected: a minority of the ~4,600 (kept low by the broad dictionary).

**4d. Assemble** → the new full `data/sources/bobkova.csv` (`ref,text`), **replacing** SP3a's file.

## 5. Re-ingest (controller — reuses SP3a code unchanged)

Identical to SP3a Task 6 with the larger `bobkova.csv`:
1. `build(...)` — existing bobkova hook + `adapters/bobkova.py` → expanded base.
2. `expand/reattach.reattach(base, current_enriched_corpus)` — re-attach SP2 enrichment by
   `normalized_text`; existing entries preserved; net-new flagged.
3. Categorize net-new (~3,800) via a haiku Workflow (27-theme taxonomy, drop-invalid normalization);
   `modern_text` = cleaned `text`; `explanation` empty. (This is the main remaining LLM cost.)
4. `recompute_variant_groups(rows, 85, 8)`; export via `enrich.export`.
5. `sources.csv` Bobkova row already present (SP3a).

## 6. Components / files

```
expand/
  segment.py             # raw OCR page text -> [proverb, ...]  (rules)          [TDD, new]
  spellcheck.py          # build vocab; is_clean(proverb)/flag                   [TDD, new]
  consolidate_pages.py   # merge clean + verified-residual outputs -> bobkova.csv [TDD, new]
  reattach.py            # reused unchanged from SP3a
adapters/bobkova.py      # unchanged (reads data/sources/bobkova.csv)
build.py                 # unchanged (bobkova hook from SP3a)
data/sources/bobkova.pdf # vendored source (committed)
data/sources/bobkova.csv # REPLACED with full book (~4,000+ rows)
corpus.csv / corpus.json # re-exported, expanded
expand/REPORT.md         # updated: full-book counts + OCR/flag/audit stats
```

OCR (pdftoppm+tesseract) and the two small LLM steps (verify-residuals, categorize) are controller-run;
`segment.py`, `spellcheck.py`, `consolidate_pages.py` are TDD'd; `reattach`/`adapter`/`build` reused.

## 7. Testing

- `segment.py` — fixtures of raw OCR page text → expected proverb list (drops junk/page-numbers/headers,
  joins wrapped lines).
- `spellcheck.py` — known words pass; a proverb with a fabricated non-word is flagged; vocab loads from
  corpus + hunspell.
- `consolidate_pages.py` — clean + verified outputs merge into `(ref,text)` rows in page order, coverage
  assertion fires on a missing page.
- Re-ingest inherits SP3a's tested `reattach`/`adapter`/`build` (full suite stays green).
- LLM steps validated by coverage + a small audit recorded in `expand/REPORT.md`.

## 8. Tech stack

`pdftoppm` + `tesseract-ocr` (`ukr`) for OCR; `hunspell-uk` dictionary for spell-check; Python 3
(pandas, rapidfuzz, pytest) reusing `core/`, `enrich/`, `expand/`; Workflow tool (haiku) for
verify-residuals and categorize. **Cleanup is token-free; LLM only touches flagged residuals + net-new
categorization.**

## 9. Expected output

Bobkova grows from 760 to ~4,000+ proverbs; corpus grows from 35,865 by the net-new count
(~3,000–3,800 after dedup/variant-link). Existing SP2 enrichment preserved; net-new categorized. More
Bobkova↔Franko variant links. `expand/REPORT.md` reports OCR pages, segmented count, % flagged/LLM-fixed,
added/merged/net-new, and a sample audit.

## 10. Open items / risks

- **tesseract accuracy** on 1960s Ukrainian print: good on the page-25 sample; residual char errors are
  caught by the spell-check → LLM-verify loop. Quality is best-effort (committed data artifacts).
- **Flag rate / token cost:** the broad hunspell-uk dictionary keeps the flagged-residual set small; if
  it is unexpectedly large (> ~40%), reassess before the verify pass. Page numbers/headers handled by
  segmentation, not flagging.
- **Replace vs SP3a 760:** full re-OCR supersedes SP3a's 760 (one consistent method); overlaps dedup.
- **hunspell-uk install:** via `DEBIAN_FRONTEND=noninteractive apt-get` (the plain install hangs on a
  debconf dialog); if unavailable, fall back to corpus-only vocab (higher flag rate, still works).
- Non-determinism confined to the LLM verify/categorize steps; their outputs are committed data artifacts.
