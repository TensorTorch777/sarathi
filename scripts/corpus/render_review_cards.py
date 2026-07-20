#!/usr/bin/env python3
"""
Render Sarathi Intelligence as end-user review cards (not raw JSON).

Examples:
  poetry run python scripts/corpus/render_review_cards.py 2.47-2.50
  poetry run python scripts/corpus/render_review_cards.py 6.5-6.10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYER1 = ROOT / "data" / "corpus" / "bhagavad_gita" / "bhagavad_gita.json"
SI_ALL = ROOT / "data" / "corpus" / "bhagavad_gita" / "sarathi_intelligence" / "ALL.generated.json"

_RANGE_RE = re.compile(
    r"^(?:BG\s*)?(\d+)\.(\d+)(?:\s*[-–—]\s*(?:BG\s*)?(?:(\d+)\.)?(\d+))?$",
    re.I,
)


def parse_spec(spec: str) -> list[tuple[int, int]]:
    """Parse '2.47-2.50' or '6.5-10' or '2.47' into (chapter, verse) list."""
    spec = spec.strip()
    m = _RANGE_RE.match(spec)
    if not m:
        raise ValueError(f"Unrecognized verse spec: {spec!r}")
    c1, v1 = int(m.group(1)), int(m.group(2))
    if m.group(4) is None:
        return [(c1, v1)]
    c2 = int(m.group(3)) if m.group(3) else c1
    v2 = int(m.group(4))
    if c1 != c2:
        raise ValueError("Cross-chapter ranges not supported; review one chapter at a time.")
    if v2 < v1:
        raise ValueError("End verse must be >= start verse")
    return [(c1, v) for v in range(v1, v2 + 1)]


def render_card(auth: dict, intel: dict) -> str:
    """End-user facing card for editorial review."""
    practices = intel.get("practice") or []
    practice_block = "\n".join(f"- {p}" for p in practices) if practices else "- _(none)_"
    topics = ", ".join(intel.get("topics") or []) or "—"
    emotions = ", ".join(intel.get("emotions") or []) or "—"
    domains = ", ".join(intel.get("life_domains") or []) or "—"
    intents = ", ".join(intel.get("user_intents") or []) or "—"
    virtues = ", ".join(intel.get("virtues") or []) or "—"
    def _fmt_related(ref: str) -> str:
        parts = ref.split("_")
        if len(parts) == 3 and parts[0] == "bg":
            return f"BG {parts[1]}.{parts[2]}"
        return ref

    related = ", ".join(_fmt_related(r) for r in (intel.get("related_verses") or [])) or "—"
    notes = intel.get("review_notes") or []
    notes_block = "\n".join(f"- {n}" for n in notes) if notes else "- _(none yet)_"
    misconceptions = intel.get("misconceptions") or []
    misconception_block = (
        "\n".join(f"- {m}" for m in misconceptions) if misconceptions else "- _(none)_"
    )
    common_queries = intel.get("common_queries") or []
    queries_block = (
        "\n".join(f"- {q}" for q in common_queries) if common_queries else "- _(none yet)_"
    )
    conf = intel.get("confidence") or {}
    overall = conf.get("overall", "—")
    sanskrit = (auth.get("sanskrit") or "").strip()
    family = intel.get("verse_family") or "—"

    return f"""### {intel.get('citation') or auth.get('citation')}

**Status:** `{intel.get('status')}` · **family:** `{family}` · **confidence:** {overall}

**Authentic Verse**
{sanskrit}

**Sarathi Summary**
{intel.get('summary') or '—'}

**Modern Interpretation**
{intel.get('modern_interpretation') or '—'}

**Topics**
{topics}

**Emotions**
{emotions}

**Life Domains**
{domains}

**User Intents**
{intents}

**Virtues**
{virtues}

**Common Queries** *(natural language people may type)*
{queries_block}

**Practice**
{practice_block}

**Reflection Question**
{intel.get('reflection_question') or '—'}

**Related Verses**
{related}

**Common Misconceptions**
{misconception_block}

**Review Notes**
{notes_block}

**Quality checks (for editors)**
| Check | Question |
| --- | --- |
| Fidelity | Does this stay faithful to the verse? |
| Clarity | Understandable without prior Sanskrit training? |
| Practicality | Is the advice useful without distorting the teaching? |
| Retrieval | Would tags + common_queries help find this verse? |
| Misconceptions | Are common misreadings gently corrected? |
| Tone | Does it sound calm and compassionate (Sarathi Voice)? |
| Editorial | Consistent with anchor-family style? |

---
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render end-user review cards")
    parser.add_argument("spec", help="Verse or range, e.g. 2.47-2.50 or 6.5-6.10")
    args = parser.parse_args(argv)

    try:
        targets = parse_spec(args.spec)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    layer1 = {n["id"]: n for n in json.loads(LAYER1.read_text())["nodes"]}
    intel = {e["node_id"]: e for e in json.loads(SI_ALL.read_text())["enrichments"]}

    print(f"# Sarathi Review Cards — {args.spec}\n")
    for chapter, verse in targets:
        node_id = f"bg_{chapter}_{verse}"
        if node_id not in layer1 or node_id not in intel:
            print(f"### BG {chapter}.{verse}\n\n_Missing from corpus._\n\n---\n")
            continue
        print(render_card(layer1[node_id], intel[node_id]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
