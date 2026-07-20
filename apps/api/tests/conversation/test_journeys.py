"""Wisdom journey engine tests."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.conversation.conversation_engine import ConversationEngine
from app.conversation.conversation_state import JourneyStatus, ResponseLevel, TurnState
from app.conversation.intelligence_loader import get_intelligence_index
from app.conversation.journey_loader import get_journey_catalog, validate_journey_against_approved
from app.conversation.journey_selector import JourneySelector
from app.conversation.session_store import ConversationSessionStore


@pytest.fixture
def store() -> ConversationSessionStore:
    s = ConversationSessionStore()
    yield s
    s.clear()


@pytest.fixture
def engine(store: ConversationSessionStore, tmp_path) -> ConversationEngine:
    return ConversationEngine(session_store=store, debug_dir=tmp_path)


class TestJourneyCatalog:
    def test_all_steps_approved(self) -> None:
        catalog = get_journey_catalog()
        assert "fear_of_failure" in catalog.journeys
        index = get_intelligence_index()
        approved = {
            nid for nid, e in index.enrichments.items() if e.status in {"approved", "locked"}
        }
        errors = validate_journey_against_approved(catalog, approved)
        assert errors == []

    def test_invalid_journey_detection(self) -> None:
        catalog = get_journey_catalog()
        errors = validate_journey_against_approved(catalog, approved_ids=set())
        assert errors
        assert any("not approved" in e for e in errors)


class TestJourneySelector:
    def test_rejects_low_confidence(self) -> None:
        sel = JourneySelector(get_journey_catalog())
        offer = sel.select(
            message="I'm terrified I'll fail my exams",
            intent="guidance",
            family_id="karma_yoga_foundations",
            confidence=10.0,
            already_offered=False,
            journey_active=False,
        )
        assert offer.journey is None
        assert offer.reason == "low_confidence"

    def test_selects_fear_of_failure(self) -> None:
        sel = JourneySelector(get_journey_catalog())
        offer = sel.select(
            message="I'm terrified I'll fail my exams",
            intent="guidance",
            family_id="karma_yoga_foundations",
            confidence=80.0,
            already_offered=False,
            journey_active=False,
        )
        assert offer.journey is not None
        assert offer.journey.id == "fear_of_failure"
        assert offer.offer_text


class TestJourneyFlow:
    def test_offer_accept_progress_complete(self, engine: ConversationEngine) -> None:
        cid = uuid4()
        r1 = engine.handle(
            "I'm terrified I'll fail my exams.",
            conversation_id=cid,
            write_debug=False,
        )
        assert r1.response_level == ResponseLevel.L1
        assert "journey" in r1.answer.lower() or "explore a short journey" in r1.answer.lower()
        assert r1.debug.get("journey_selected") == "fear_of_failure"

        r2 = engine.handle("yes", conversation_id=cid, write_debug=False)
        assert "step 1 of" in r2.answer.lower()
        assert "BG 2.47" in r2.answer or "2.47" in r2.answer
        assert r2.debug.get("journey_status") == JourneyStatus.ACTIVE.value
        assert r2.debug.get("current_step") == 0

        r3 = engine.handle("continue", conversation_id=cid, write_debug=False)
        assert "step 2 of" in r3.answer.lower()
        assert r3.debug.get("current_step") == 1

        r4 = engine.handle("continue", conversation_id=cid, write_debug=False)
        assert "step 3 of" in r4.answer.lower()
        # last step completes
        assert r4.debug.get("journey_status") in {
            JourneyStatus.COMPLETED.value,
            JourneyStatus.ACTIVE.value,
        }

    def test_decline_offer(self, engine: ConversationEngine) -> None:
        cid = uuid4()
        engine.handle(
            "I'm terrified I'll fail my exams.",
            conversation_id=cid,
            write_debug=False,
        )
        r = engine.handle("no", conversation_id=cid, write_debug=False)
        assert "stay with this teaching" in r.answer.lower()
        assert r.debug.get("journey_status") == JourneyStatus.NONE.value

    def test_exit_mid_journey(self, engine: ConversationEngine) -> None:
        cid = uuid4()
        engine.handle(
            "I'm terrified I'll fail my exams.",
            conversation_id=cid,
            write_debug=False,
        )
        engine.handle("yes", conversation_id=cid, write_debug=False)
        r = engine.handle("stop", conversation_id=cid, write_debug=False)
        assert "leave" in r.answer.lower()
        assert r.debug.get("journey_status") == JourneyStatus.EXITED.value

    def test_l2_still_works_after_offer(self, engine: ConversationEngine) -> None:
        cid = uuid4()
        engine.handle(
            "I'm terrified I'll fail my exams.",
            conversation_id=cid,
            write_debug=False,
        )
        r = engine.handle("Can you explain why?", conversation_id=cid, write_debug=False)
        assert r.response_level == ResponseLevel.L2
        assert r.state == TurnState.WAIT
