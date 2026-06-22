# Enrichment Report — ukr-proverbs-corpus (Sub-project 2)

Generated 2026-06-22. Enrichment engine: Claude Code agents (Workflow), file-based batch I/O.

## Coverage

All **35,165** entries enriched (100% coverage on both passes), via batched LLM passes plus
repair rounds. Enriched fields are committed **data artifacts** (LLM output is not
byte-reproducible — see the spec §2).

| Field | Source pass | Model |
|---|---|---|
| `category` (1–3 theme keys) | Pass A | haiku |
| `explanation` (cleaned in place) | Pass A | haiku |
| `modern_text` | Pass B | sonnet |
| `variant_group` (tuned) | local recompute | — |

## Process notes

- Initial full run (235 A + 352 B batches, run concurrently) hit a session usage limit at
  ~6.1M tokens. Completed batches persisted to disk; the run was finished with **id-level
  repair rounds** (re-running only missing/invalid ids), one pass at a time.
- **Category validity:** agents occasionally emitted theme keys outside the 27-key taxonomy
  (~3%). Fixed two ways: (a) 320 all-invalid records re-run with a stricter "use only these
  keys" prompt; (b) a deterministic normalization at merge time drops any remaining
  out-of-taxonomy key (a valid primary tag survived in ~all cases). Final `idiom_expressive`
  fallback was needed for **0** records.
- **Malformed JSON:** a few Pass-B batches contained unescaped `"` inside `modern_text`
  (Ukrainian „…" quotation). Recovered losslessly with a line-level salvage parser; no data lost.

## Variant tuning

The SP1 `variant_group` linking (rapidfuzz `token_set_ratio ≥ 85`) was recomputed and **capped**:
groups with more than 8 members are dissolved (set to no group), removing the long tail of
over-linked clusters flagged in the SP1 final review. Result: **3,431 → 3,413** variant groups.
Threshold and cap are tunable (`enrich/tune_variants.py`).

## Category distribution (entries per theme; multi-label, so sum > 35,165)

emotion_mood 4965 · wisdom_folly 3689 · idiom_expressive 3524 · work_labor 2812 ·
social_relations 2543 · animals 2392 · poverty_wealth 2340 · fate_luck 2293 ·
conflict_enmity 2210 · speech_lying 2200 · appearance_reputation 1942 · religion_god 1934 ·
food_hunger 1846 · body_health 1643 · time_seasons 1409 · trade_money 1351 ·
family_kinship 1301 · marriage_gender 1260 · class_power 1150 · death_illness 1140 ·
justice_truth 1135 · home_household 890 · nature_weather 771 · travel_distance 629 ·
ethnic_local 564 · drink_alcohol 528 · friendship_love 453

## Quality audit (independent sample, n = 40)

- **modern_text:** 31 good · 7 minor · 2 wrong → **~95% acceptable**. The two WRONG cases were
  an un-modernized archaic future construction and a dropped prefix; minor cases are mostly
  retained dialectal reflexive `ся`. Overall fidelity is high.
- **category:** 28 good · 6 partial · 6 wrong → **~85% acceptable**, ~15% clear misses. Misses
  cluster where the proverb's theme falls outside the 27-key taxonomy (e.g. loss/misfortune,
  order/disorder) or where a secondary tag is over-eager.

## Known limitations

- **Categorization is best-effort, single-pass.** ~15% of tags are debatable or wrong; a future
  verification/second-vote pass (or a few added themes) would raise precision. The primary tag
  is reliable far more often than secondary tags.
- **modern_text** retains some dialectal forms (e.g. reflexive `ся`) where there is no clean
  standard equivalent; this is intentional, not an error.
- Fields are LLM-generated; regenerating requires Claude Code (not a deterministic build).
