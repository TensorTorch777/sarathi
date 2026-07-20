"""Decide whether Sarathi should ask a single clarifying follow-up."""

from __future__ import annotations

from dataclasses import dataclass

from app.conversation.editorial_retriever import EditorialRetriever, RetrievedHit


@dataclass(frozen=True, slots=True)
class FollowupDecision:
    ask: bool
    question: str | None
    reason: str


_LOW_CONFIDENCE = 35.0  # combined score threshold


class FollowupSelector:
    """
    Ask at most one follow-up when:
      - multiple equally relevant families, OR
      - low retrieval confidence
    Never interrogate.
    """

    def __init__(self, retriever: EditorialRetriever) -> None:
        self._retriever = retriever

    def decide(
        self,
        hits: list[RetrievedHit],
        *,
        already_asked: bool,
    ) -> FollowupDecision:
        if already_asked:
            return FollowupDecision(ask=False, question=None, reason="already_asked")
        if not hits:
            return FollowupDecision(
                ask=True,
                question=(
                    "Would you share a little more about what feels hardest right now — "
                    "fear of the outcome, pressure to perform, or something else?"
                ),
                reason="no_hits",
            )

        top = hits[0]
        families = self._retriever.distinct_families(hits[:4])

        # Multiple strong families within close scores
        if len(families) >= 2 and len(hits) >= 2:
            second = hits[1]
            if abs(top.score - second.score) <= 8.0 and second.score >= _LOW_CONFIDENCE:
                names = []
                for fid in families[:2]:
                    # prefer human names from hits
                    for h in hits:
                        if h.family and h.family.id == fid:
                            names.append(h.family.name)
                            break
                    else:
                        names.append(fid)
                return FollowupDecision(
                    ask=True,
                    question=(
                        f"Are you looking more for guidance like “{names[0]}”, "
                        f"or more like “{names[1]}”?"
                    ),
                    reason="multiple_families",
                )

        if top.score < _LOW_CONFIDENCE:
            return FollowupDecision(
                ask=True,
                question=(
                    "I want to meet you carefully — is this more about fear of failing, "
                    "feeling restless, or relating to others?"
                ),
                reason="low_confidence",
            )

        return FollowupDecision(ask=False, question=None, reason="confident_direct")
