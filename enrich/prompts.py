from __future__ import annotations

PASS_A_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "categories", "explanation_clean"],
        "properties": {
            "id": {"type": "string"},
            "categories": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
            "explanation_clean": {"type": "string"},
        },
    },
}

PASS_B_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "modern_text"],
        "properties": {"id": {"type": "string"}, "modern_text": {"type": "string"}},
    },
}


def pass_a_prompt(batch_path: str, taxonomy: dict[str, str]) -> str:
    lines = "\n".join(f"- {k}: {v}" for k, v in taxonomy.items())
    return f"""You are a Ukrainian paremiologist tagging proverbs by theme and cleaning their explanations.

Read this JSON file — a list of proverbs, each with `id`, `text`, `keyword`, `explanation`:
{batch_path}

The text is in 1901 Galician / pre-reform Ukrainian orthography — read past dialectal spelling to the meaning.

THEMES (use ONLY these keys):
{lines}

For EVERY proverb in the file, return an object with:
- `id`: the proverb's id, unchanged.
- `categories`: 1 to 3 theme keys from the list above, MOST relevant FIRST (the primary vehicle/target of the proverb). Use `idiom_expressive` only when no thematic reading is defensible (opaque curses/formulae).
- `explanation_clean`: the input `explanation` with OCR noise, stray whitespace, and broken hyphenation removed. If the input explanation is empty, return "".

Return one object per input id — do not skip, merge, or invent ids."""


def pass_b_prompt(batch_path: str) -> str:
    return f"""You are a Ukrainian linguist modernizing the spelling of historical proverbs.

Read this JSON file — a list of proverbs, each with `id` and `text`:
{batch_path}

The `text` is in Ivan Franko's 1901 Galician / etymological orthography. Render each into MODERN STANDARD Ukrainian spelling, preserving meaning, word order, and dialectal lexicon where it has no standard equivalent. Examples of the kind of change intended:
- богато -> багато
- archaic reflexive сї -> ся
- ѣ (yat) -> і  (e.g. дѣти -> діти)
- pre-reform hard-sign / doubled forms -> modern forms

For EVERY proverb, return an object with:
- `id`: unchanged.
- `modern_text`: the modernized spelling (never empty; if already modern, return it unchanged).

Return one object per input id — never drop or merge entries."""
