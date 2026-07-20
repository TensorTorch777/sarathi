"""Sarathi conversation engine — editorially-driven wisdom turns + journeys."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from app.conversation.conversation_state import (
    ConversationSession,
    JourneyStatus,
    ResponseLevel,
    TurnState,
)
from app.conversation.editorial_retriever import EditorialRetriever, RetrievedHit
from app.conversation.followup_selector import FollowupSelector
from app.conversation.intelligence_loader import IntelligenceIndex, get_intelligence_index
from app.conversation.intent_classifier import (
    IntentClassifier,
    wants_l2,
    wants_l3,
    wants_new_topic,
)
from app.conversation.journey_loader import JourneyCatalog, get_journey_catalog
from app.conversation.journey_renderer import (
    accepts_journey,
    declines_journey,
    render_journey_step,
    wants_continue,
    wants_exit_journey,
)
from app.conversation.journey_selector import JourneySelector
from app.conversation.response_builder import BuiltResponse, ResponseBuilder
from app.conversation.safety_checker import SafetyChecker
from app.conversation.session_store import ConversationSessionStore, default_session_store


@dataclass(frozen=True, slots=True)
class ConversationTurnResult:
    answer: str
    session_id: UUID
    intent: str
    response_level: ResponseLevel
    state: TurnState
    confidence: float
    family_id: str | None
    verse_ids: tuple[str, ...]
    citations: tuple[str, ...]
    followup_asked: bool
    safety_ok: bool
    debug: dict[str, object] = field(default_factory=dict)


_CRISIS_RESPONSE = (
    "I'm glad you reached out. I can sit with you through the Gita's wisdom, "
    "but I am not a crisis counselor. If you may be in danger of harming yourself, "
    "please contact local emergency services or a trusted person nearby right away. "
    "If you want, tell me what feels most overwhelming in this moment — "
    "and we can take one steady step with a teaching that emphasizes care without shame."
)


class ConversationEngine:
    """
    State machine:

      START → UNDERSTAND → RETRIEVE → RESPOND_L1 → WAIT
        → RESPOND_L2 / RESPOND_L3 / JOURNEY_STEP → WAIT → END

    Journeys are curated sequences of approved verses — no AI generation.
    """

    def __init__(
        self,
        *,
        index: IntelligenceIndex | None = None,
        session_store: ConversationSessionStore | None = None,
        journey_catalog: JourneyCatalog | None = None,
        debug_dir: Path | None = None,
    ) -> None:
        self._index = index or get_intelligence_index()
        self._sessions = session_store or default_session_store
        self._journeys = journey_catalog or get_journey_catalog()
        self._intent = IntentClassifier()
        self._retriever = EditorialRetriever(self._index)
        self._followups = FollowupSelector(self._retriever)
        self._journey_selector = JourneySelector(self._journeys)
        self._builder = ResponseBuilder(self._index)
        self._safety = SafetyChecker()
        self._debug_dir = debug_dir

    def handle(
        self,
        message: str,
        *,
        conversation_id: UUID | None = None,
        top_k: int = 5,
        write_debug: bool = True,
    ) -> ConversationTurnResult:
        session = self._sessions.get_or_create(conversation_id)
        session.turn_count += 1
        session.last_user_message = message

        # Journey / depth routing while WAITING
        if session.state == TurnState.WAIT:
            journey_result = self._try_journey_turn(session, message, write_debug=write_debug)
            if journey_result is not None:
                return journey_result

            if session.primary_node_id:
                if wants_new_topic(message):
                    session.reset_for_new_topic()
                elif wants_l3(message) and session.response_level in {
                    ResponseLevel.L1,
                    ResponseLevel.L2,
                }:
                    return self._respond_depth(session, ResponseLevel.L3, write_debug=write_debug)
                elif wants_l2(message) and session.response_level == ResponseLevel.L1:
                    return self._respond_depth(session, ResponseLevel.L2, write_debug=write_debug)
                elif (
                    session.journey_status
                    not in {JourneyStatus.OFFERED, JourneyStatus.ACTIVE}
                    and not wants_l2(message)
                    and not wants_l3(message)
                ):
                    # Fresh guidance question (not a journey accept/continue)
                    session.reset_for_new_topic()

        if session.state in {TurnState.START, TurnState.END}:
            if session.state == TurnState.END:
                session.reset_for_new_topic()
            else:
                session.advance(TurnState.UNDERSTAND)

        # UNDERSTAND
        if session.state != TurnState.UNDERSTAND:
            session.state = TurnState.UNDERSTAND

        intent = self._intent.classify(message)
        session.intent = intent.intent
        session.advance(TurnState.RETRIEVE)

        if intent.intent == "crisis":
            return self._crisis_turn(session, intent.intent, write_debug=write_debug)

        # RETRIEVE
        hits = self._retriever.retrieve(message, top_k=top_k)
        session.retrieved_node_ids = [h.enrichment.node_id for h in hits]
        if hits:
            session.primary_node_id = hits[0].enrichment.node_id
            session.primary_family_id = (
                hits[0].family.id if hits[0].family else hits[0].enrichment.verse_family
            )
            session.confidence = float(hits[0].score)
        else:
            session.confidence = 0.0

        session.advance(TurnState.RESPOND_L1)
        follow = self._followups.decide(hits, already_asked=session.followup_asked)
        if follow.ask:
            session.followup_asked = True

        if not hits:
            built = BuiltResponse(
                text=(
                    "I want to meet you carefully. "
                    + (follow.question or "Could you share a little more about what you need?")
                ),
                level=ResponseLevel.L1,
                practice_used=None,
                reflection_used=None,
                misconceptions_shown=(),
                related_citations=(),
                family_overview_used=False,
                fields_used=("followup",),
            )
            return self._finalize(
                session,
                built,
                hits=[],
                followup_asked=True,
                intent=intent.intent,
                write_debug=write_debug,
            )

        built = self._builder.build(
            hit=hits[0],
            level=ResponseLevel.L1,
            followup_question=follow.question if follow.ask else None,
        )
        session.response_level = ResponseLevel.L1

        # Offer journey after confident L1 (never forced)
        offer = self._journey_selector.select(
            message=message,
            intent=intent.intent,
            family_id=session.primary_family_id,
            confidence=session.confidence,
            already_offered=session.journey_status == JourneyStatus.OFFERED,
            journey_active=session.journey_status == JourneyStatus.ACTIVE,
        )
        journey_offer_text = None
        if offer.journey is not None and offer.offer_text:
            # Prefer journey offer over competing follow-up when both fire
            if follow.ask and built.text.endswith(follow.question or ""):
                # Rebuild L1 without follow-up — journey is the soft next step
                built = self._builder.build(hit=hits[0], level=ResponseLevel.L1)
                session.followup_asked = False
                followup_asked = False
            else:
                followup_asked = follow.ask
            session.journey_status = JourneyStatus.OFFERED
            session.offered_journey_id = offer.journey.id
            session.journey_select_reason = offer.reason
            journey_offer_text = offer.offer_text
            text = built.text.rstrip() + "\n\n" + offer.offer_text
            built = BuiltResponse(
                text=text,
                level=built.level,
                practice_used=built.practice_used,
                reflection_used=built.reflection_used,
                misconceptions_shown=built.misconceptions_shown,
                related_citations=built.related_citations,
                family_overview_used=built.family_overview_used,
                fields_used=tuple([*built.fields_used, "journey_offer"]),
            )
        else:
            followup_asked = follow.ask
            session.journey_select_reason = offer.reason

        return self._finalize(
            session,
            built,
            hits=hits,
            followup_asked=followup_asked,
            intent=intent.intent,
            write_debug=write_debug,
            followup_reason=follow.reason if followup_asked else None,
            journey_offer=journey_offer_text,
        )

    def _try_journey_turn(
        self,
        session: ConversationSession,
        message: str,
        *,
        write_debug: bool,
    ) -> ConversationTurnResult | None:
        # Decline offer
        if session.journey_status == JourneyStatus.OFFERED and declines_journey(message):
            session.journey_status = JourneyStatus.NONE
            session.offered_journey_id = None
            built = BuiltResponse(
                text="Of course — we can stay with this teaching. What else is on your mind?",
                level=ResponseLevel.L1,
                practice_used=None,
                reflection_used=None,
                misconceptions_shown=(),
                related_citations=(),
                family_overview_used=False,
                fields_used=("journey_declined",),
            )
            return self._finalize(
                session,
                built,
                hits=[],
                followup_asked=False,
                intent=session.intent or "guidance",
                write_debug=write_debug,
            )

        # Accept offer → step 0
        if session.journey_status == JourneyStatus.OFFERED and accepts_journey(message):
            jid = session.offered_journey_id
            if not jid or jid not in self._journeys.journeys:
                session.clear_journey()
                return None
            session.journey_status = JourneyStatus.ACTIVE
            session.active_journey_id = jid
            session.journey_step_index = 0
            session.journey_completed_steps = []
            return self._emit_journey_step(session, write_debug=write_debug)

        # Active journey controls
        if session.journey_status == JourneyStatus.ACTIVE and session.active_journey_id:
            if wants_exit_journey(message):
                title = self._journeys.journeys[session.active_journey_id].title
                session.journey_status = JourneyStatus.EXITED
                session.active_journey_id = None
                built = BuiltResponse(
                    text=(
                        f"We can leave the {title} journey here. "
                        "Ask whenever you want to continue learning together."
                    ),
                    level=ResponseLevel.L1,
                    practice_used=None,
                    reflection_used=None,
                    misconceptions_shown=(),
                    related_citations=(),
                    family_overview_used=False,
                    fields_used=("journey_exited",),
                )
                return self._finalize(
                    session,
                    built,
                    hits=[],
                    followup_asked=False,
                    intent=session.intent or "guidance",
                    write_debug=write_debug,
                )
            if wants_continue(message) or accepts_journey(message):
                journey = self._journeys.journeys[session.active_journey_id]
                # mark current complete, advance
                if session.journey_step_index not in session.journey_completed_steps:
                    session.journey_completed_steps.append(session.journey_step_index)
                nxt = session.journey_step_index + 1
                if nxt >= len(journey.steps):
                    session.journey_status = JourneyStatus.COMPLETED
                    session.active_journey_id = None
                    built = BuiltResponse(
                        text=(
                            f"That completes the {journey.title} journey. "
                            "You can ask another question whenever you like."
                        ),
                        level=ResponseLevel.L1,
                        practice_used=None,
                        reflection_used=None,
                        misconceptions_shown=(),
                        related_citations=(),
                        family_overview_used=False,
                        fields_used=("journey_completed",),
                    )
                    return self._finalize(
                        session,
                        built,
                        hits=[],
                        followup_asked=False,
                        intent=session.intent or "learning",
                        write_debug=write_debug,
                    )
                session.journey_step_index = nxt
                return self._emit_journey_step(session, write_debug=write_debug)

        return None

    def _emit_journey_step(
        self,
        session: ConversationSession,
        *,
        write_debug: bool,
    ) -> ConversationTurnResult:
        assert session.active_journey_id is not None
        journey = self._journeys.journeys[session.active_journey_id]
        step = journey.steps[session.journey_step_index]
        if session.state == TurnState.WAIT:
            session.advance(TurnState.JOURNEY_STEP)
        elif session.state != TurnState.JOURNEY_STEP:
            session.state = TurnState.JOURNEY_STEP

        text = render_journey_step(
            journey,
            step,
            step_index=session.journey_step_index,
            index=self._index,
        )
        enr = self._index.enrichments.get(step.verse)
        hit_list: list[RetrievedHit] = []
        if enr:
            family = self._index.families.get(enr.verse_family) if enr.verse_family else None
            hit_list = [
                RetrievedHit(
                    enrichment=enr,
                    family=family,
                    score=session.confidence,
                    editorial_weight=session.confidence,
                    lexical_score=0.0,
                )
            ]
            session.primary_node_id = enr.node_id
            session.primary_family_id = step.family
            session.retrieved_node_ids = [enr.node_id]

        built = BuiltResponse(
            text=text,
            level=ResponseLevel.L1,
            practice_used=step.practice or None,
            reflection_used=step.reflection or None,
            misconceptions_shown=(),
            related_citations=((enr.citation,) if enr else ()),
            family_overview_used=False,
            fields_used=("journey_step", "summary", "practice", "reflection"),
        )
        session.response_level = ResponseLevel.L1

        # Last step → mark completed before finalize so debug reflects completion
        is_last = session.journey_step_index >= len(journey.steps) - 1
        if session.journey_step_index not in session.journey_completed_steps:
            session.journey_completed_steps.append(session.journey_step_index)
        if is_last:
            session.journey_status = JourneyStatus.COMPLETED

        result = self._finalize(
            session,
            built,
            hits=hit_list,
            followup_asked=False,
            intent=session.intent or "learning",
            write_debug=write_debug,
        )
        if is_last:
            session.active_journey_id = None
            self._sessions.save(session)
        return result

    def _respond_depth(
        self,
        session: ConversationSession,
        level: ResponseLevel,
        *,
        write_debug: bool,
    ) -> ConversationTurnResult:
        assert session.primary_node_id is not None
        enr = self._index.enrichments[session.primary_node_id]
        family = self._index.families.get(enr.verse_family) if enr.verse_family else None
        hit = RetrievedHit(
            enrichment=enr,
            family=family,
            score=session.confidence,
            editorial_weight=session.confidence,
            lexical_score=0.0,
        )
        if level == ResponseLevel.L2:
            session.advance(TurnState.RESPOND_L2)
        else:
            session.advance(TurnState.RESPOND_L3)
        built = self._builder.build(hit=hit, level=level)
        session.response_level = level
        return self._finalize(
            session,
            built,
            hits=[hit],
            followup_asked=False,
            intent=session.intent or "learning",
            write_debug=write_debug,
        )

    def _crisis_turn(
        self,
        session: ConversationSession,
        intent: str,
        *,
        write_debug: bool,
    ) -> ConversationTurnResult:
        session.advance(TurnState.RESPOND_L1)
        built = BuiltResponse(
            text=_CRISIS_RESPONSE,
            level=ResponseLevel.L1,
            practice_used=None,
            reflection_used=None,
            misconceptions_shown=(),
            related_citations=(),
            family_overview_used=False,
            fields_used=("crisis_protocol",),
        )
        session.response_level = ResponseLevel.L1
        return self._finalize(
            session,
            built,
            hits=[],
            followup_asked=False,
            intent=intent,
            write_debug=write_debug,
        )

    def _finalize(
        self,
        session: ConversationSession,
        built: BuiltResponse,
        *,
        hits: list[RetrievedHit],
        followup_asked: bool,
        intent: str,
        write_debug: bool,
        followup_reason: str | None = None,
        journey_offer: str | None = None,
    ) -> ConversationTurnResult:
        allowed = {h.enrichment.citation for h in hits}
        if built.related_citations:
            allowed.update(built.related_citations)
        safety = self._safety.check(built.text, allowed_citations=allowed)
        answer = built.text if safety.ok else self._safety.fallback_message()

        if session.state in {
            TurnState.RESPOND_L1,
            TurnState.RESPOND_L2,
            TurnState.RESPOND_L3,
            TurnState.JOURNEY_STEP,
        }:
            session.advance(TurnState.WAIT)

        self._sessions.save(session)

        journey = (
            self._journeys.journeys.get(session.active_journey_id)
            if session.active_journey_id
            else None
        )
        remaining = 0
        if journey is not None:
            remaining = max(0, len(journey.steps) - session.journey_step_index - 1)

        debug: dict[str, object] = {
            "detected_intent": intent,
            "retrieved_family": session.primary_family_id,
            "retrieved_verses": list(session.retrieved_node_ids),
            "confidence": session.confidence,
            "chosen_response_level": built.level.value,
            "misconceptions_shown": list(built.misconceptions_shown),
            "practice_chosen": built.practice_used,
            "reflection_chosen": built.reflection_used,
            "safety_checks": {
                "ok": safety.ok,
                "violations": list(safety.violations),
            },
            "state": session.state.value,
            "followup_asked": followup_asked,
            "followup_reason": followup_reason,
            "fields_used": list(built.fields_used),
            "journey_selected": session.offered_journey_id or session.active_journey_id,
            "journey_reason": session.journey_select_reason,
            "journey_status": session.journey_status.value,
            "current_step": session.journey_step_index
            if session.journey_status == JourneyStatus.ACTIVE
            else None,
            "remaining_steps": remaining if session.journey_status == JourneyStatus.ACTIVE else None,
            "journey_completed_steps": list(session.journey_completed_steps),
            "journey_offer_present": journey_offer is not None,
        }
        if write_debug:
            self._write_debug(debug)

        return ConversationTurnResult(
            answer=answer if safety.ok else self._safety.fallback_message(),
            session_id=session.session_id,
            intent=intent,
            response_level=built.level,
            state=session.state,
            confidence=session.confidence,
            family_id=session.primary_family_id,
            verse_ids=tuple(session.retrieved_node_ids),
            citations=tuple(h.enrichment.citation for h in hits),
            followup_asked=followup_asked,
            safety_ok=safety.ok,
            debug=debug,
        )

    def _write_debug(self, payload: dict[str, object]) -> None:
        path = self._debug_dir
        if path is None:
            path = Path(__file__).resolve().parents[2] / "debug"
        path.mkdir(parents=True, exist_ok=True)
        out = path / "debug_response.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
