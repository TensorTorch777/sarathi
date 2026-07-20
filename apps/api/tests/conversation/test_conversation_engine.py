"""Conversation engine unit tests (v0.6.0-product-alpha)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.conversation.conversation_engine import ConversationEngine
from app.conversation.conversation_state import ResponseLevel, TurnState
from app.conversation.intent_classifier import IntentClassifier, wants_l2, wants_l3
from app.conversation.safety_checker import SafetyChecker
from app.conversation.session_store import ConversationSessionStore


@pytest.fixture
def store() -> ConversationSessionStore:
    s = ConversationSessionStore()
    yield s
    s.clear()


@pytest.fixture
def engine(store: ConversationSessionStore, tmp_path) -> ConversationEngine:
    return ConversationEngine(session_store=store, debug_dir=tmp_path)


class TestIntentClassifier:
    def test_guidance_exam_fear(self) -> None:
        result = IntentClassifier().classify("I'm terrified I'll fail my exams.")
        assert result.intent == "guidance"

    def test_crisis(self) -> None:
        result = IntentClassifier().classify("I want to die and can't go on")
        assert result.intent == "crisis"

    def test_learning(self) -> None:
        result = IntentClassifier().classify("Teach me the philosophy behind this")
        assert result.intent == "learning"

    def test_depth_cues(self) -> None:
        assert wants_l2("Can you explain why?")
        assert wants_l3("Teach me the philosophy behind this")


class TestRetrievalPriority:
    def test_approved_anchor_preferred_for_exam_fear(self, engine: ConversationEngine) -> None:
        result = engine.handle("I'm terrified I'll fail my exams.", write_debug=False)
        assert result.verse_ids
        # Should land in karma yoga / self mastery anchors
        assert result.family_id in {
            "karma_yoga_foundations",
            "self_mastery",
            "sthitaprajna",
            "devotional_character",
        }
        # Top hit should be approved
        top = engine._index.enrichments[result.verse_ids[0]]
        assert top.status in {"approved", "locked"}


class TestProgressiveDisclosure:
    def test_l1_then_l2_then_l3(self, engine: ConversationEngine) -> None:
        cid = uuid4()
        r1 = engine.handle(
            "I'm terrified I'll fail my exams.",
            conversation_id=cid,
            write_debug=False,
        )
        assert r1.response_level == ResponseLevel.L1
        assert r1.state == TurnState.WAIT
        assert "BG" in r1.answer or "Gita" in r1.answer

        r2 = engine.handle("Can you explain why?", conversation_id=cid, write_debug=False)
        assert r2.response_level == ResponseLevel.L2
        assert r2.state == TurnState.WAIT
        assert r2.verse_ids[0] == r1.verse_ids[0]

        r3 = engine.handle(
            "Teach me the philosophy behind this.",
            conversation_id=cid,
            write_debug=False,
        )
        assert r3.response_level == ResponseLevel.L3
        assert r3.state == TurnState.WAIT

    def test_no_l3_on_first_turn(self, engine: ConversationEngine) -> None:
        r = engine.handle("I'm terrified I'll fail my exams.", write_debug=False)
        assert r.response_level == ResponseLevel.L1


class TestSafety:
    def test_rejects_promises(self) -> None:
        result = SafetyChecker().check("Everything will work out and you will succeed.")
        assert result.ok is False
        assert "promises" in result.violations

    def test_rejects_guilt(self) -> None:
        result = SafetyChecker().check("You should be ashamed of yourself.")
        assert result.ok is False

    def test_accepts_calm_guidance(self) -> None:
        result = SafetyChecker().check(
            "Your responsibility is to act with integrity, not to control the outcome. "
            "The Gita points to this in BG 2.47."
        )
        assert result.ok is True


class TestFollowupAndDebug:
    def test_debug_written(self, engine: ConversationEngine, tmp_path) -> None:
        engine.handle("How do I become kinder?", write_debug=True)
        debug_file = tmp_path / "debug_response.json"
        assert debug_file.exists()
        text = debug_file.read_text()
        assert "detected_intent" in text
        assert "chosen_response_level" in text

    def test_state_machine_no_skip(self, store: ConversationSessionStore) -> None:
        session = store.get_or_create(None)
        session.advance(TurnState.UNDERSTAND)
        with pytest.raises(ValueError):
            session.advance(TurnState.RESPOND_L3)
