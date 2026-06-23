from __future__ import annotations


def apply_corrections(proverbs: list[dict], corrections: dict[str, str]) -> list[dict]:
    rids = {p["rid"] for p in proverbs}
    extra = set(corrections) - rids
    if extra:
        raise ValueError(f"corrections for unknown rids: {sorted(extra)[:5]}")
    out = []
    for p in proverbs:
        text = corrections.get(p["rid"], p["text"])
        out.append({"ref": p["ref"], "text": text})
    return out
