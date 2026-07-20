"""Editorial-priority retrieval over Sarathi Intelligence (no new embeddings)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.conversation.intelligence_loader import (
    EnrichmentRecord,
    FamilyRecord,
    IntelligenceIndex,
    status_rank,
    tier_rank,
)


@dataclass(frozen=True, slots=True)
class RetrievedHit:
    enrichment: EnrichmentRecord
    family: FamilyRecord | None
    score: float
    editorial_weight: float
    lexical_score: float


_TOKEN_RE = re.compile(r"[a-z0-9']+", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 2}


def _content_tokens(text: str) -> set[str]:
    """Tokens long enough to avoid weak collisions (fail↔failing alone)."""
    stop = {
        "the", "and", "for", "with", "that", "this", "what", "when", "how",
        "why", "are", "you", "your", "have", "from", "into", "about", "just",
        "like", "keep", "being", "will", "can", "dont", "does", "goes",
        "stay", "then", "than", "them", "they", "been", "very", "much",
        "myself", "yourself", "others", "everyone", "someone",
    }
    return {t for t in _tokens(text) if len(t) > 3 and t not in stop}


# Query cues → emotion tag boosts (deterministic, no embeddings)
_CUE_BOOSTS: list[tuple[tuple[str, ...], dict[str, float]]] = [
    (
        ("fail", "failing", "failure", "exam", "exams", "grades"),
        {"emotions": 4.0, "tags": {"fear_of_failure", "performance_pressure", "anxiety"}},
    ),
    (
        ("angry", "anger", "temper", "rage", "furious"),
        {"emotions": 4.0, "tags": {"anger"}},
    ),
    (
        ("compar", "jealous", "envy"),
        {"emotions": 3.5, "tags": {"shame", "self_doubt", "inner_conflict"}},
    ),
    (
        ("grief", "lost someone", "mourning", "bereav"),
        {"emotions": 4.0, "tags": {"grief"}},
    ),
    (
        ("kind", "grudge", "forgiv", "bitter"),
        {"emotions": 3.5, "tags": {"anger", "guilt", "shame"}},
    ),
    (
        ("calm", "everything goes wrong", "equanim"),
        {"emotions": 3.0, "tags": {"anxiety", "overwhelm", "restlessness", "fear"}},
    ),
]

# Prefer structured topics over shared emotion tags alone
_TOPIC_CUES: list[tuple[tuple[str, ...], set[str], float]] = [
    (("angry", "anger", "temper", "rage"), {"anger"}, 7.0),
    (("calm", "everything goes wrong", "equanim"), {"equanimity"}, 5.5),
    (("fail", "failing", "exam"), {"duty", "detachment", "yoga"}, 3.0),
    (("compar", "jealous", "envy"), {"self", "discipline", "mind"}, 3.0),
]

# Soft family priors for well-known life situations (editorial, not new content)
_FAMILY_CUES: list[tuple[tuple[str, ...], str, float]] = [
    (("compar", "jealous", "envy"), "self_mastery", 8.0),
    (("fail", "exam", "grades"), "karma_yoga_foundations", 3.0),
    (("calm", "everything goes wrong", "equanim"), "sthitaprajna", 6.0),
    (("angry", "anger", "temper", "rage"), "sthitaprajna", 3.0),
]


class EditorialRetriever:
    """
    Rank enrichments by editorial quality first, then lexical relevance.

    Priority:
      Approved Anchor → Approved Core → Approved → Reviewed → Generated
    """

    def __init__(self, index: IntelligenceIndex) -> None:
        self._index = index

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedHit]:
        q_tokens = _tokens(query)
        q_lower = query.lower()
        hits: list[RetrievedHit] = []

        for enr in self._index.enrichments.values():
            family = (
                self._index.families.get(enr.verse_family)
                if enr.verse_family
                else None
            )
            editorial = self._editorial_weight(enr, family)
            lexical = self._lexical_score(enr, family, q_tokens, q_lower)
            if lexical <= 0 and editorial < 40:
                # Skip weak generated noise unless somehow editorial-strong
                continue
            # Combine: editorial dominates; lexical breaks ties within band
            score = editorial + lexical
            hits.append(
                RetrievedHit(
                    enrichment=enr,
                    family=family,
                    score=score,
                    editorial_weight=editorial,
                    lexical_score=lexical,
                )
            )

        hits.sort(key=lambda h: (h.score, h.enrichment.confidence_overall), reverse=True)
        return hits[:top_k]

    def _editorial_weight(
        self,
        enr: EnrichmentRecord,
        family: FamilyRecord | None,
    ) -> float:
        s_rank = status_rank(enr.status)
        # Base by enrichment status
        base = {
            5: 50.0,  # locked
            4: 40.0,  # approved
            3: 25.0,  # reviewed
            2: 10.0,  # generated
            0: 0.0,
        }.get(s_rank, 0.0)

        if family is None:
            return base

        # Family tier boost only when enrichment is at least reviewed
        if s_rank >= 3:
            base += tier_rank(family.tier, anchor=family.anchor_family)
        # Approved family status boost
        if family.status == "approved" and s_rank >= 4:
            base += 5.0
        return base

    def _lexical_score(
        self,
        enr: EnrichmentRecord,
        family: FamilyRecord | None,
        q_tokens: set[str],
        q_lower: str,
    ) -> float:
        score = 0.0
        q_content = _content_tokens(q_lower)
        emo_set = set(enr.emotions)
        topic_set = set(enr.topics)

        # Common queries — Jaccard / multi-token only (no single-token false positives)
        for cq in enr.common_queries:
            cq_l = cq.lower()
            if cq_l == q_lower or (len(q_lower) > 24 and (cq_l in q_lower or q_lower in cq_l)):
                score += 14.0
                continue
            cq_content = _content_tokens(cq_l)
            overlap = q_content & cq_content
            if not overlap or not cq_content:
                continue
            jaccard = len(overlap) / len(q_content | cq_content)
            if len(overlap) >= 3 or jaccard >= 0.5:
                score += 12.0
            elif len(overlap) >= 2 and jaccard >= 0.35:
                score += 5.0

        # Structured fields (topics/emotions/intents) — primary lexical signal
        structured = " ".join(
            [
                " ".join(enr.topics),
                " ".join(enr.emotions),
                " ".join(enr.life_domains),
                " ".join(enr.user_intents),
                " ".join(enr.virtues),
                family.theme if family and family.theme else "",
            ]
        ).lower()
        score += len(q_content & _content_tokens(structured)) * 2.0

        # Free prose — low weight, long tokens only (avoid "calm"/"goes" collisions)
        prose = f"{enr.summary} {enr.modern_interpretation}".lower()
        prose_tokens = {t for t in _content_tokens(prose) if len(t) > 5}
        score += len(q_content & prose_tokens) * 0.5

        # Direct emotion/topic label hits in the query
        for emo in enr.emotions:
            label = emo.replace("_", " ")
            if label in q_lower or emo in q_tokens:
                score += 3.0
        for topic in enr.topics:
            label = topic.replace("_", " ")
            if label in q_lower or topic in q_tokens:
                score += 2.5

        # Deterministic cue → emotion tag boosts
        for cues, spec in _CUE_BOOSTS:
            if any(c in q_lower for c in cues):
                if emo_set & spec["tags"]:
                    score += float(spec["emotions"])

        # Topic-precision: prefer verses whose topics name the cue (not only emotions)
        for cues, topics, boost in _TOPIC_CUES:
            if any(c in q_lower for c in cues) and topic_set & topics:
                score += boost

        # Anger cascade: desire→anger→delusion when thinking collapses
        if any(c in q_lower for c in ("angry", "anger", "temper")) and any(
            w in q_lower for w in ("think", "mind", "straight", "delusion")
        ):
            if {"anger", "mind"} <= topic_set or (
                "desire" in topic_set and "anger" in topic_set
            ):
                score += 5.0

        # Adversity equanimity: calm under pressure → fear/anger + equanimity
        if any(c in q_lower for c in ("calm", "everything goes wrong")):
            if "equanimity" in topic_set and emo_set & {
                "fear",
                "anger",
                "fear_of_failure",
            }:
                score += 4.0

        # Family priors
        if family:
            for cues, family_id, boost in _FAMILY_CUES:
                if family.id == family_id and any(c in q_lower for c in cues):
                    score += boost

        return score

    def distinct_families(self, hits: list[RetrievedHit]) -> list[str]:
        seen: list[str] = []
        for hit in hits:
            fid = hit.family.id if hit.family else hit.enrichment.verse_family
            if fid and fid not in seen:
                seen.append(fid)
        return seen
