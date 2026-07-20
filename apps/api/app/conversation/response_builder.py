"""Build natural-language responses from approved editorial fields only."""

from __future__ import annotations

from dataclasses import dataclass

from app.conversation.conversation_state import ResponseLevel
from app.conversation.editorial_retriever import RetrievedHit
from app.conversation.intelligence_loader import EnrichmentRecord, FamilyRecord, IntelligenceIndex


@dataclass(frozen=True, slots=True)
class BuiltResponse:
    text: str
    level: ResponseLevel
    practice_used: str | None
    reflection_used: str | None
    misconceptions_shown: tuple[str, ...]
    related_citations: tuple[str, ...]
    family_overview_used: bool
    fields_used: tuple[str, ...]


def _citation_label(node_id: str) -> str:
    parts = node_id.split("_")
    if len(parts) == 3 and parts[0] == "bg":
        return f"BG {parts[1]}.{parts[2]}"
    return node_id


class ResponseBuilder:
    """Assemble L1/L2/L3 from enrichment + family records — no hallucinated advice."""

    def __init__(self, index: IntelligenceIndex) -> None:
        self._index = index

    def build(
        self,
        *,
        hit: RetrievedHit,
        level: ResponseLevel,
        followup_question: str | None = None,
    ) -> BuiltResponse:
        enr = hit.enrichment
        family = hit.family
        if level == ResponseLevel.L1:
            return self._build_l1(enr, followup_question=followup_question)
        if level == ResponseLevel.L2:
            return self._build_l2(enr, family)
        return self._build_l3(enr, family)

    def _build_l1(
        self,
        enr: EnrichmentRecord,
        *,
        followup_question: str | None,
    ) -> BuiltResponse:
        # Prefer response_levels.level_1 when present
        summary = (enr.response_levels.get("level_1") or enr.summary).strip()
        practice = enr.practice[0] if enr.practice else None

        paragraphs: list[str] = []
        # Natural prose — not labeled sections
        paragraphs.append(
            f"{summary} The Gita points to this in {enr.citation}."
        )
        if practice:
            paragraphs.append(f"One small step you can take: {practice}")
        if followup_question:
            paragraphs.append(followup_question)

        # Hard cap: max 2 content paragraphs (+ optional follow-up as 3rd short line)
        content = paragraphs[:2]
        if followup_question and followup_question not in content:
            content.append(followup_question)

        text = "\n\n".join(content)
        fields = ["summary", "citation"]
        if practice:
            fields.append("practice")
        if followup_question:
            fields.append("followup")
        return BuiltResponse(
            text=text,
            level=ResponseLevel.L1,
            practice_used=practice,
            reflection_used=None,
            misconceptions_shown=(),
            related_citations=(),
            family_overview_used=False,
            fields_used=tuple(fields),
        )

    def _build_l2(
        self,
        enr: EnrichmentRecord,
        family: FamilyRecord | None,
    ) -> BuiltResponse:
        interpretation = (
            enr.response_levels.get("level_2") or enr.modern_interpretation
        ).strip()
        misconceptions = list(enr.misconceptions[:2])
        related = enr.related_verses[:2]
        related_labels = [_citation_label(r) for r in related]

        parts: list[str] = [interpretation]
        if misconceptions:
            gentle = " A common misunderstanding: " + " Another: ".join(misconceptions)
            parts[0] = parts[0].rstrip(".") + "." + gentle
        if related_labels:
            parts.append(
                "You may also find company in "
                + " and ".join(related_labels)
                + "."
            )
        if enr.reflection_question:
            parts.append(f"A question to sit with: {enr.reflection_question}")

        fields = ["modern_interpretation"]
        if misconceptions:
            fields.append("misconceptions")
        if related:
            fields.append("related_verses")
        if enr.reflection_question:
            fields.append("reflection_question")

        return BuiltResponse(
            text="\n\n".join(parts),
            level=ResponseLevel.L2,
            practice_used=None,
            reflection_used=enr.reflection_question,
            misconceptions_shown=tuple(misconceptions),
            related_citations=tuple(related_labels),
            family_overview_used=False,
            fields_used=tuple(fields),
        )

    def _build_l3(
        self,
        enr: EnrichmentRecord,
        family: FamilyRecord | None,
    ) -> BuiltResponse:
        parts: list[str] = []
        fields: list[str] = []

        if family and family.overview:
            parts.append(family.overview)
            fields.append("family.overview")
        if family and family.why_this_matters_today:
            parts.append(family.why_this_matters_today)
            fields.append("family.why_this_matters_today")

        # Sanskrit / philosophical nuance from interpretation + theme (no invented concepts)
        nuance = enr.modern_interpretation.strip()
        if nuance:
            parts.append(
                f"Going deeper with {enr.citation}: {nuance}"
            )
            fields.append("modern_interpretation")

        if family and family.theme:
            parts.append(f"The thread of this teaching family is: {family.theme}")
            fields.append("family.theme")

        # Related families via related verses' families
        related_families: list[str] = []
        for rid in enr.related_verses[:4]:
            other = self._index.enrichments.get(rid)
            if not other or not other.verse_family:
                continue
            fam = self._index.families.get(other.verse_family)
            if fam and fam.id != (family.id if family else None):
                label = fam.name
                if label not in related_families:
                    related_families.append(label)
        if related_families:
            parts.append(
                "Nearby teaching families include: " + "; ".join(related_families[:3]) + "."
            )
            fields.append("related_families")

        if family and family.family_misconceptions:
            parts.append(
                "Worth remembering: " + " ".join(family.family_misconceptions[:2])
            )
            fields.append("family_misconceptions")

        practice = enr.practice[0] if enr.practice else None
        if practice:
            parts.append(f"Practice: {practice}")
            fields.append("practice")

        return BuiltResponse(
            text="\n\n".join(parts) if parts else enr.summary,
            level=ResponseLevel.L3,
            practice_used=practice,
            reflection_used=enr.reflection_question,
            misconceptions_shown=tuple((family.family_misconceptions[:2] if family else ())),
            related_citations=tuple(_citation_label(r) for r in enr.related_verses[:3]),
            family_overview_used=bool(family and family.overview),
            fields_used=tuple(fields),
        )
