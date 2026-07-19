#!/usr/bin/env python3
"""
Generate Sarathi Intelligence overlays for all verses in the master corpus.

- Does NOT modify Authentic Scripture (Layer 1).
- Writes per-chapter JSON under sarathi_intelligence/.
- Status starts as ``generated`` (editorial workflow).
- Preserves existing human-tuned Chapter 2 drafts (upgrades status draft→generated).

Offline content tooling only — not a runtime service.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data" / "corpus" / "bhagavad_gita" / "bhagavad_gita.json"
SI_DIR = ROOT / "data" / "corpus" / "bhagavad_gita" / "sarathi_intelligence"
CH2_EXISTING = SI_DIR / "chapter_02.draft.json"
TAX = ROOT / "data" / "corpus" / "bhagavad_gita" / "taxonomies.json"

CHAPTER_THEMES: dict[int, dict] = {
    1: {
        "title": "Arjuna's Despair",
        "topics": ["dharma", "duty", "mind"],
        "emotions": ["grief", "fear", "confusion", "overwhelm"],
        "domains": ["family", "identity", "leadership"],
        "intents": ["seeking_guidance", "seeking_courage"],
        "virtues": ["honesty", "compassion", "humility"],
    },
    2: {
        "title": "Sankhya Yoga — Wisdom and Equanimity",
        "topics": ["wisdom", "equanimity", "karma", "self"],
        "emotions": ["grief", "anxiety", "fear", "peace"],
        "domains": ["spiritual_practice", "identity", "career"],
        "intents": ["seeking_peace", "seeking_guidance", "seeking_detachment"],
        "virtues": ["wisdom", "equanimity", "courage"],
    },
    3: {
        "title": "Karma Yoga — Action",
        "topics": ["karma", "duty", "action", "detachment"],
        "emotions": ["anxiety", "guilt", "confusion"],
        "domains": ["career", "leadership", "spiritual_practice"],
        "intents": ["seeking_guidance", "seeking_discipline", "seeking_detachment"],
        "virtues": ["discipline", "non_attachment", "perseverance"],
    },
    4: {
        "title": "Jnana-Karma-Sannyasa — Knowledge in Action",
        "topics": ["knowledge", "karma", "wisdom", "renunciation"],
        "emotions": ["confusion", "peace", "anxiety"],
        "domains": ["spiritual_practice", "identity", "studies"],
        "intents": ["seeking_meaning", "seeking_guidance"],
        "virtues": ["wisdom", "humility", "discipline"],
    },
    5: {
        "title": "Karma-Sannyasa — Renunciation and Action",
        "topics": ["renunciation", "karma", "equanimity", "liberation"],
        "emotions": ["anxiety", "peace", "confusion"],
        "domains": ["spiritual_practice", "career", "identity"],
        "intents": ["seeking_detachment", "seeking_peace"],
        "virtues": ["non_attachment", "equanimity", "wisdom"],
    },
    6: {
        "title": "Dhyana Yoga — Meditation",
        "topics": ["mind", "discipline", "yoga", "self"],
        "emotions": ["restlessness", "anxiety", "peace"],
        "domains": ["spiritual_practice", "health", "studies"],
        "intents": ["seeking_discipline", "seeking_peace"],
        "virtues": ["discipline", "self_control", "perseverance"],
    },
    7: {
        "title": "Jnana-Vijnana — Knowing the Divine",
        "topics": ["knowledge", "devotion", "wisdom", "self"],
        "emotions": ["confusion", "peace", "awe"],
        "domains": ["spiritual_practice", "identity"],
        "intents": ["seeking_meaning", "seeking_guidance"],
        "virtues": ["devotion", "wisdom", "humility"],
    },
    8: {
        "title": "Aksara-Brahma — The Imperishable",
        "topics": ["liberation", "devotion", "self", "wisdom"],
        "emotions": ["fear", "anxiety", "peace"],
        "domains": ["spiritual_practice", "grief_loss", "identity"],
        "intents": ["seeking_peace", "seeking_meaning"],
        "virtues": ["devotion", "wisdom", "courage"],
    },
    9: {
        "title": "Raja-Vidya — Royal Knowledge",
        "topics": ["devotion", "knowledge", "dharma", "liberation"],
        "emotions": ["peace", "fear", "confusion"],
        "domains": ["spiritual_practice", "identity"],
        "intents": ["seeking_meaning", "seeking_encouragement"],
        "virtues": ["devotion", "faith", "humility"],
    },
    10: {
        "title": "Vibhuti Yoga — Divine Glories",
        "topics": ["devotion", "wisdom", "self"],
        "emotions": ["peace", "confusion"],
        "domains": ["spiritual_practice", "identity"],
        "intents": ["seeking_meaning", "seeking_encouragement"],
        "virtues": ["devotion", "humility", "wisdom"],
    },
    11: {
        "title": "Visvarupa — Cosmic Form",
        "topics": ["devotion", "wisdom", "surrender"],
        "emotions": ["fear", "overwhelm", "peace"],
        "domains": ["spiritual_practice", "identity"],
        "intents": ["seeking_courage", "seeking_meaning"],
        "virtues": ["devotion", "humility", "courage"],
    },
    12: {
        "title": "Bhakti Yoga — Devotion",
        "topics": ["devotion", "equanimity", "compassion", "discipline"],
        "emotions": ["anxiety", "peace", "grief"],
        "domains": ["spiritual_practice", "relationships", "identity"],
        "intents": ["seeking_peace", "seeking_encouragement"],
        "virtues": ["devotion", "compassion", "equanimity", "patience"],
    },
    13: {
        "title": "Kshetra-Kshetrajna — Field and Knower",
        "topics": ["knowledge", "self", "wisdom", "detachment"],
        "emotions": ["confusion", "peace", "anxiety"],
        "domains": ["spiritual_practice", "identity", "studies"],
        "intents": ["seeking_meaning", "seeking_detachment"],
        "virtues": ["wisdom", "humility", "non_attachment"],
    },
    14: {
        "title": "Gunatraya — The Three Gunas",
        "topics": ["mind", "wisdom", "discipline", "liberation"],
        "emotions": ["restlessness", "anxiety", "peace"],
        "domains": ["spiritual_practice", "health", "identity"],
        "intents": ["seeking_discipline", "seeking_peace"],
        "virtues": ["self_control", "wisdom", "equanimity"],
    },
    15: {
        "title": "Purushottama — The Supreme Person",
        "topics": ["self", "liberation", "wisdom", "detachment"],
        "emotions": ["anxiety", "peace", "confusion"],
        "domains": ["spiritual_practice", "identity"],
        "intents": ["seeking_meaning", "seeking_detachment"],
        "virtues": ["wisdom", "non_attachment", "devotion"],
    },
    16: {
        "title": "Daivasura — Divine and Demonic Qualities",
        "topics": ["dharma", "discipline", "desire", "wisdom"],
        "emotions": ["anger", "fear", "guilt", "peace"],
        "domains": ["identity", "relationships", "leadership"],
        "intents": ["seeking_discipline", "seeking_guidance", "seeking_forgiveness"],
        "virtues": ["honesty", "compassion", "self_control", "humility"],
    },
    17: {
        "title": "Shraddhatraya — Three Kinds of Faith",
        "topics": ["devotion", "discipline", "dharma", "wisdom"],
        "emotions": ["confusion", "anxiety", "peace"],
        "domains": ["spiritual_practice", "identity", "health"],
        "intents": ["seeking_guidance", "seeking_discipline"],
        "virtues": ["discipline", "honesty", "devotion"],
    },
    18: {
        "title": "Moksha-Sannyasa — Liberation and Surrender",
        "topics": ["surrender", "liberation", "duty", "devotion", "renunciation"],
        "emotions": ["fear", "anxiety", "peace", "grief"],
        "domains": ["spiritual_practice", "identity", "career"],
        "intents": ["seeking_peace", "seeking_surrender", "seeking_guidance"],
        "virtues": ["devotion", "courage", "non_attachment", "humility"],
    },
}

# Fix intents/virtues/emotions that aren't in taxonomy
TAXONOMY_FIXES = {
    "emotions": {"awe": "peace", "hope": "peace", "curiosity": "confusion"},
    "virtues": {"faith": "devotion"},
    "intents": {"seeking_surrender": "seeking_peace"},
}

# High-signal verse overrides (summary + modern + related). Others use chapter templates.
OVERRIDES: dict[str, dict] = {
    "bg_3_19": {
        "summary": "Therefore, without attachment, always perform necessary action — by acting without attachment one attains the Supreme.",
        "modern_interpretation": "Keep doing what must be done; freedom grows inside action when clinging drops away.",
        "topics": ["karma", "duty", "detachment", "action"],
        "emotions": ["anxiety", "guilt"],
        "life_domains": ["career", "leadership", "spiritual_practice"],
        "user_intents": ["seeking_detachment", "seeking_discipline", "seeking_guidance"],
        "virtues": ["discipline", "non_attachment", "perseverance"],
        "practice": ["Do today's necessary task fully, then consciously release the result."],
        "reflection_question": "Which necessary action am I delaying because I am attached to how it must turn out?",
        "related_verses": ["bg_2_47", "bg_3_8", "bg_3_30"],
        "confidence": 0.9,
    },
    "bg_3_8": {
        "summary": "Perform prescribed action; action is better than inaction — even bodily maintenance needs action.",
        "modern_interpretation": "Withdrawal that abandons responsibility is not spirituality; sincere work can be yoga.",
        "topics": ["karma", "duty", "action"],
        "emotions": ["guilt", "confusion", "anxiety"],
        "life_domains": ["career", "family", "spiritual_practice"],
        "user_intents": ["seeking_guidance", "seeking_discipline"],
        "virtues": ["discipline", "honesty", "perseverance"],
        "practice": ["Choose one neglected duty and complete it today without drama."],
        "reflection_question": "Where am I calling avoidance 'spiritual'?",
        "related_verses": ["bg_2_47", "bg_3_19", "bg_3_4"],
        "confidence": 0.88,
    },
    "bg_3_30": {
        "summary": "Surrendering all actions to Me, with mind on the Self, free of desire and possessiveness — fight without fever.",
        "modern_interpretation": "Offer the work beyond ego ownership; then act without the burning anxiety of self-centered striving.",
        "topics": ["surrender", "karma", "duty", "detachment"],
        "emotions": ["anxiety", "fear", "overwhelm"],
        "life_domains": ["career", "leadership", "spiritual_practice"],
        "user_intents": ["seeking_peace", "seeking_courage", "seeking_detachment"],
        "virtues": ["devotion", "non_attachment", "courage"],
        "practice": ["Before work, silently offer it beyond ego; then begin."],
        "reflection_question": "What fever of possessiveness is heating my effort?",
        "related_verses": ["bg_2_48", "bg_3_19", "bg_18_66"],
        "confidence": 0.88,
    },
    "bg_6_5": {
        "summary": "Elevate yourself by the self; do not degrade yourself — the self is friend and enemy of the self.",
        "modern_interpretation": "Your mind can lift you or sabotage you; self-mastery is an inside job.",
        "topics": ["mind", "self", "discipline"],
        "emotions": ["hopelessness", "anxiety", "shame"],
        "life_domains": ["spiritual_practice", "identity", "health"],
        "user_intents": ["seeking_discipline", "seeking_encouragement", "seeking_courage"],
        "virtues": ["discipline", "honesty", "perseverance"],
        "practice": ["Interrupt one self-degrading habit today with one uplifting replacement."],
        "reflection_question": "In what way is my own mind currently acting as my enemy?",
        "related_verses": ["bg_6_6", "bg_2_60", "bg_6_26"],
        "confidence": 0.92,
    },
    "bg_6_6": {
        "summary": "For one who has conquered the mind, the mind is a friend; for one who has not, it remains an enemy.",
        "modern_interpretation": "An untrained mind argues against your wellbeing; a trained mind becomes ally.",
        "topics": ["mind", "discipline", "yoga"],
        "emotions": ["restlessness", "anxiety", "anger"],
        "life_domains": ["spiritual_practice", "health", "studies"],
        "user_intents": ["seeking_discipline", "seeking_peace"],
        "virtues": ["self_control", "discipline", "patience"],
        "practice": ["When the mind attacks, answer with one firm kind instruction — then act."],
        "reflection_question": "Is my mind currently friend or foe in this season of life?",
        "related_verses": ["bg_6_5", "bg_6_26", "bg_2_67"],
        "confidence": 0.9,
    },
    "bg_6_26": {
        "summary": "Wherever the restless, unsteady mind wanders, restrain it and bring it under the control of the Self.",
        "modern_interpretation": "Meditation is repeated gentle return — not never wandering.",
        "topics": ["mind", "discipline", "yoga"],
        "emotions": ["restlessness", "anxiety", "overwhelm"],
        "life_domains": ["spiritual_practice", "studies", "health"],
        "user_intents": ["seeking_discipline", "seeking_peace"],
        "virtues": ["patience", "perseverance", "self_control"],
        "practice": ["Each time attention wanders, note 'wandering' and return once — count returns, not perfection."],
        "reflection_question": "Can I treat mind-wandering as training data rather than failure?",
        "related_verses": ["bg_6_5", "bg_6_35", "bg_2_58"],
        "confidence": 0.9,
    },
    "bg_12_13": {
        "summary": "A devotee is free of hatred, friendly and compassionate, without possessiveness or ego, equal in pain and pleasure, forgiving.",
        "modern_interpretation": "Devotion shows up as character: warmth without ownership, steadiness without hardness.",
        "topics": ["devotion", "compassion", "equanimity"],
        "emotions": ["anger", "peace", "grief"],
        "life_domains": ["relationships", "family", "spiritual_practice"],
        "user_intents": ["seeking_peace", "seeking_forgiveness", "seeking_encouragement"],
        "virtues": ["compassion", "patience", "humility", "equanimity"],
        "practice": ["Choose one relationship; practice friendliness without needing to win."],
        "reflection_question": "Where is possessiveness or ego blocking my capacity to be a friend?",
        "related_verses": ["bg_12_14", "bg_12_15", "bg_2_56"],
        "confidence": 0.9,
    },
    "bg_18_66": {
        "summary": "Abandon all varieties of dharma and take refuge in Me alone; I will liberate you from all sin — do not grieve.",
        "modern_interpretation": "When systems of self-saving exhaust you, sincere surrender can reopen trust and release terror.",
        "topics": ["surrender", "devotion", "liberation"],
        "emotions": ["fear", "anxiety", "grief", "peace"],
        "life_domains": ["spiritual_practice", "identity", "grief_loss"],
        "user_intents": ["seeking_peace", "seeking_courage", "seeking_forgiveness"],
        "virtues": ["devotion", "courage", "humility"],
        "practice": ["In overwhelm, stop strategizing for two minutes and offer the burden beyond yourself."],
        "reflection_question": "What am I still trying to save alone that I could entrust more deeply?",
        "related_verses": ["bg_18_65", "bg_2_7", "bg_9_22"],
        "confidence": 0.9,
        "uncertainty_notes": "Handle with pastoral care; not an excuse to abandon ethical responsibility lightly.",
    },
    "bg_4_7": {
        "summary": "Whenever dharma declines and adharma rises, I manifest Myself.",
        "modern_interpretation": "Renewal comes when disorder peaks — hope is structural in the moral universe, not naive optimism.",
        "topics": ["dharma", "devotion", "wisdom"],
        "emotions": ["fear", "hopelessness", "peace"],
        "life_domains": ["leadership", "spiritual_practice", "identity"],
        "user_intents": ["seeking_encouragement", "seeking_courage", "seeking_meaning"],
        "virtues": ["courage", "devotion", "honesty"],
        "practice": ["In a declining situation, ask what small dharmic act you can restore today."],
        "reflection_question": "Where is dharma thinning in my life — and what would renewal look like?",
        "related_verses": ["bg_4_8", "bg_4_1", "bg_18_66"],
        "confidence": 0.88,
    },
    "bg_9_22": {
        "summary": "Those who worship Me with exclusive devotion — I carry what they lack and preserve what they have.",
        "modern_interpretation": "Sincere devoted focus is met with support; trust can coexist with responsible effort.",
        "topics": ["devotion", "surrender", "duty"],
        "emotions": ["anxiety", "fear", "peace"],
        "life_domains": ["spiritual_practice", "career", "family"],
        "user_intents": ["seeking_encouragement", "seeking_peace"],
        "virtues": ["devotion", "perseverance", "humility"],
        "practice": ["Do your part fully; then release tomorrow's provision anxiety in prayer or quiet trust."],
        "reflection_question": "Where am I exhausting myself trying to secure what only trust can hold?",
        "related_verses": ["bg_18_66", "bg_2_47", "bg_12_6"],
        "confidence": 0.85,
    },
}


def _load_tax() -> dict[str, set[str]]:
    raw = json.loads(TAX.read_text(encoding="utf-8"))
    return {
        "topics": set(raw["topics"]),
        "emotions": set(raw["emotions"]),
        "life_domains": set(raw["life_domains"]),
        "user_intents": set(raw["user_intents"]),
        "virtues": set(raw["virtues"]),
    }


def _sanitize(values: list[str], allowed: set[str], field: str) -> list[str]:
    fixes = TAXONOMY_FIXES.get(field, {})
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        v = fixes.get(value, value)
        if v in allowed and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _related(chapter: int, verse: int, max_verse: int) -> list[str]:
    ids: list[str] = []
    for delta in (-2, -1, 1, 2, 3):
        v = verse + delta
        if 1 <= v <= max_verse:
            ids.append(f"bg_{chapter}_{v}")
    return ids[:4]


def _generate_one(node: dict, chapter_sizes: dict[int, int], tax: dict[str, set[str]]) -> dict:
    chapter = node["locator"]["chapter"]
    verse = node["locator"]["verse"]
    node_id = node["id"]
    theme = CHAPTER_THEMES[chapter]
    sanskrit = " ".join((node.get("sanskrit") or "").split())
    snip = sanskrit[:60] + ("…" if len(sanskrit) > 60 else "")

    if node_id in OVERRIDES:
        o = OVERRIDES[node_id]
        return {
            "node_id": node_id,
            "citation": node["citation"],
            "status": "generated",
            "summary": o["summary"],
            "modern_interpretation": o["modern_interpretation"],
            "topics": _sanitize(o["topics"], tax["topics"], "topics"),
            "emotions": _sanitize(o["emotions"], tax["emotions"], "emotions"),
            "life_domains": _sanitize(o["life_domains"], tax["life_domains"], "life_domains"),
            "user_intents": _sanitize(o["user_intents"], tax["user_intents"], "user_intents"),
            "virtues": _sanitize(o["virtues"], tax["virtues"], "virtues"),
            "practice": o["practice"] if isinstance(o["practice"], list) else [o["practice"]],
            "reflection_question": o["reflection_question"],
            "related_verses": o["related_verses"],
            "confidence": {
                "summary": o.get("confidence", 0.88),
                "topics": o.get("confidence", 0.88) - 0.05,
                "emotions": o.get("confidence", 0.88) - 0.1,
                "overall": o.get("confidence", 0.88),
            },
            "uncertainty_notes": o.get(
                "uncertainty_notes",
                "High-priority verse override — still requires human review before approval.",
            ),
            "misconceptions": o.get("misconceptions", []),
            "review_notes": [],
            "reviewed_by": None,
            "approved_at": None,
        }

    # Keyword nudges from Devanagari / structure
    topics = list(theme["topics"][:3])
    emotions = list(theme["emotions"][:3])
    if re.search(r"कर्म|योग", sanskrit):
        for t in ("karma", "yoga", "action"):
            if t in tax["topics"] and t not in topics:
                topics.append(t)
                break
    if re.search(r"भक्ति|मद्भक्त|भज", sanskrit):
        if "devotion" in tax["topics"] and "devotion" not in topics:
            topics.insert(0, "devotion")
    if re.search(r"शोक|दुःख", sanskrit):
        for e in ("grief", "anxiety"):
            if e in tax["emotions"] and e not in emotions:
                emotions.insert(0, e)
                break
    if re.search(r"क्रोध|काम", sanskrit):
        for e in ("anger", "restlessness"):
            if e in tax["emotions"] and e not in emotions:
                emotions.insert(0, e)
                break

    topics = _sanitize(topics, tax["topics"], "topics")[:4]
    emotions = _sanitize(emotions, tax["emotions"], "emotions")[:4]
    domains = _sanitize(list(theme["domains"]), tax["life_domains"], "life_domains")[:4]
    intents = _sanitize(list(theme["intents"]), tax["user_intents"], "user_intents")[:3]
    virtues = _sanitize(list(theme["virtues"]), tax["virtues"], "virtues")[:4]

    summary = (
        f"A teaching from {theme['title']} (BG {chapter}.{verse}) "
        f"inviting reflection on {', '.join(topics[:2])}."
    )
    modern = (
        f"In modern life, this verse from Chapter {chapter} supports clarity around "
        f"{topics[0] if topics else 'dharma'} when facing "
        f"{emotions[0] if emotions else 'inner conflict'}. "
        f"(Generated coverage draft — refine against full translation in review.)"
    )
    practice = [
        f"Sit with BG {chapter}.{verse} for two minutes; note one feeling and one duty it clarifies."
    ]
    reflection = (
        f"What is Chapter {chapter}'s theme ({theme['title']}) asking of me through this verse?"
    )

    # Slightly lower confidence for generated coverage drafts
    overall = 0.62
    if verse in {1, chapter_sizes[chapter]}:
        overall = 0.58  # opening/closing often narrative — review carefully

    return {
        "node_id": node_id,
        "citation": node["citation"],
        "status": "generated",
        "summary": summary,
        "modern_interpretation": modern,
        "topics": topics,
        "emotions": emotions,
        "life_domains": domains,
        "user_intents": intents,
        "virtues": virtues,
        "practice": practice,
        "reflection_question": reflection,
        "related_verses": _related(chapter, verse, chapter_sizes[chapter]),
        "confidence": {
            "summary": overall - 0.05,
            "topics": overall,
            "emotions": overall - 0.08,
            "overall": overall,
        },
        "uncertainty_notes": (
            "Generated coverage draft from chapter theme + verse structure. "
            f"Sanskrit cue: {snip}. Requires human review before approved/locked."
        ),
        "misconceptions": [],
        "review_notes": [],
        "reviewed_by": None,
        "approved_at": None,
        "source_sanskrit_checksum": None,
    }


def _load_ch2_preserved(tax: dict[str, set[str]]) -> dict[str, dict]:
    """Keep curated Chapter 2 content; normalize status to generated."""
    if not CH2_EXISTING.exists():
        # also accept chapter_02.generated.json
        alt = SI_DIR / "chapter_02.generated.json"
        path = alt if alt.exists() else None
    else:
        path = CH2_EXISTING
    if path is None:
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for e in doc.get("enrichments", []):
        e = dict(e)
        e["status"] = "generated" if e.get("status") in {None, "draft", "generated"} else e["status"]
        e["topics"] = _sanitize(e.get("topics") or [], tax["topics"], "topics")
        e["emotions"] = _sanitize(e.get("emotions") or [], tax["emotions"], "emotions")
        e["life_domains"] = _sanitize(
            e.get("life_domains") or [], tax["life_domains"], "life_domains"
        )
        e["user_intents"] = _sanitize(
            e.get("user_intents") or [], tax["user_intents"], "user_intents"
        )
        e["virtues"] = _sanitize(e.get("virtues") or [], tax["virtues"], "virtues")
        # bump confidence object if scalar
        conf = e.get("confidence")
        if isinstance(conf, (int, float)):
            e["confidence"] = {
                "summary": conf,
                "topics": conf,
                "emotions": conf - 0.05,
                "overall": conf,
            }
        out[e["node_id"]] = e
    return out


def build_review_queue(all_enrichments: list[dict]) -> dict:
    """Priority review queue for editorial workflow."""
    high_ids = [
        "bg_2_47",
        "bg_2_48",
        "bg_2_49",
        "bg_2_50",
        "bg_2_11",
        "bg_2_14",
        "bg_2_62",
        "bg_2_63",
        "bg_3_8",
        "bg_3_19",
        "bg_3_30",
        "bg_4_7",
        "bg_6_5",
        "bg_6_6",
        "bg_6_26",
        "bg_9_22",
        "bg_12_13",
        "bg_18_66",
    ]
    by_id = {e["node_id"]: e for e in all_enrichments}
    high = [by_id[i]["citation"] for i in high_ids if i in by_id]
    # Medium: rest of chapters 2,3,6,12,18
    medium_chapters = {2, 3, 6, 12, 18}
    medium = [
        e["citation"]
        for e in all_enrichments
        if e["node_id"] not in high_ids
        and int(e["node_id"].split("_")[1]) in medium_chapters
    ]
    low = [
        e["citation"]
        for e in all_enrichments
        if e["citation"] not in high and e["citation"] not in medium
    ]
    return {
        "version": "1.0",
        "workflow": ["generated", "reviewed", "approved", "locked"],
        "instructions": (
            "Review high priority first (10–20 at a time). "
            "Paste JSON batches for editorial review. "
            "Mark reviewed → approved → locked only after human check."
        ),
        "high_priority": high,
        "medium_priority": medium,
        "low_priority": low,
        "counts": {
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "total": len(all_enrichments),
        },
    }


def main() -> None:
    if not CORPUS.exists():
        raise SystemExit(f"Master corpus missing: {CORPUS}")
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    nodes = corpus["nodes"]
    if len(nodes) != 700:
        raise SystemExit(f"Expected 700 verses in Layer 1, found {len(nodes)}")

    tax = _load_tax()
    chapter_sizes = {
        c: sum(1 for n in nodes if n["locator"]["chapter"] == c) for c in range(1, 19)
    }
    preserved = _load_ch2_preserved(tax)

    by_chapter: dict[int, list[dict]] = {c: [] for c in range(1, 19)}
    all_enrichments: list[dict] = []

    for node in nodes:
        chapter = node["locator"]["chapter"]
        node_id = node["id"]
        if node_id in preserved:
            enrichment = preserved[node_id]
            enrichment["status"] = (
                enrichment["status"]
                if enrichment["status"] in {"generated", "reviewed", "approved", "locked"}
                else "generated"
            )
        else:
            enrichment = _generate_one(node, chapter_sizes, tax)
        # attach lightweight provenance link to authentic node
        enrichment["authentic_node_id"] = node_id
        by_chapter[chapter].append(enrichment)
        all_enrichments.append(enrichment)

    SI_DIR.mkdir(parents=True, exist_ok=True)
    for chapter, enrichments in by_chapter.items():
        path = SI_DIR / f"chapter_{chapter:02d}.generated.json"
        doc = {
            "manifest": {
                "name": "Sarathi Intelligence",
                "scripture": "bhagavad_gita",
                "chapter": chapter,
                "chapter_title": CHAPTER_THEMES[chapter]["title"],
                "version": "0.2.0-generated",
                "status": "generated",
                "authentic_corpus": "../bhagavad_gita.json",
                "editorial_workflow": ["generated", "reviewed", "approved", "locked"],
                "enrichment_count": len(enrichments),
                "approval_policy": "Never auto-approve. Human review required.",
            },
            "enrichments": enrichments,
        }
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path.name} ({len(enrichments)})")

    # Combined index for tooling
    index_path = SI_DIR / "ALL.generated.json"
    index_path.write_text(
        json.dumps(
            {
                "manifest": {
                    "name": "Sarathi Intelligence",
                    "scripture": "bhagavad_gita",
                    "version": "0.2.0-generated",
                    "status": "generated",
                    "enrichment_count": len(all_enrichments),
                    "authentic_corpus": "../bhagavad_gita.json",
                    "editorial_workflow": ["generated", "reviewed", "approved", "locked"],
                },
                "enrichments": all_enrichments,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {index_path.name} ({len(all_enrichments)})")

    queue = build_review_queue(all_enrichments)
    queue_path = SI_DIR / "review_queue.json"
    queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {queue_path.name} high={queue['counts']['high']}")

    # Remove obsolete draft filename if generated exists
    if CH2_EXISTING.exists() and (SI_DIR / "chapter_02.generated.json").exists():
        CH2_EXISTING.unlink()
        print("removed chapter_02.draft.json (superseded)")


if __name__ == "__main__":
    main()
