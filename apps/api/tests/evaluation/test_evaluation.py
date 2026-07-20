"""Evaluation unit tests."""

from __future__ import annotations

from app.conversation.conversation_engine import ConversationEngine
from app.conversation.session_store import ConversationSessionStore
from app.evaluation.evaluation_report import EvaluationReportBuilder
from app.evaluation.response_evaluator import ResponseEvaluator


def test_exam_fear_evaluation_profile() -> None:
    store = ConversationSessionStore()
    engine = ConversationEngine(session_store=store, debug_dir=None)
    evaluator = ResponseEvaluator()
    result = engine.handle("I'm terrified I'll fail my exams.", write_debug=False)
    evaluation = evaluator.evaluate(
        answer=result.answer,
        intent=result.intent,
        family_id=result.family_id,
        response_level=result.response_level.value,
        confidence=result.confidence,
        verse_ids=list(result.verse_ids),
        debug=result.debug,
    )
    assert evaluation.retrieval_diagnostics["anchor"] is True
    assert evaluation.safety_score["passed"] is True
    assert evaluation.editorial_score["mean"] >= 0.85
    assert evaluation.response_level == "L1"
    assert evaluation.journey_used is True  # offer counts
    assert evaluation.overall_score >= 0.85


def test_safety_failure_lowers_score() -> None:
    evaluator = ResponseEvaluator()
    evaluation = evaluator.evaluate(
        answer="Everything will work out and you will succeed. Krishna is punishing you.",
        intent="guidance",
        family_id="karma_yoga_foundations",
        response_level="L1",
        confidence=80.0,
        verse_ids=["bg_2_47"],
        debug={"safety_checks": {"ok": True, "violations": []}},
    )
    assert evaluation.safety_score["passed"] is False
    assert evaluation.editorial_score["sarathi_voice"] == 0.0


def test_report_gates() -> None:
    builder = EvaluationReportBuilder()
    store = ConversationSessionStore()
    engine = ConversationEngine(session_store=store, debug_dir=None)
    evaluator = ResponseEvaluator()
    r = engine.handle("How do I become kinder?", write_debug=False)
    builder.add(
        evaluator.evaluate(
            answer=r.answer,
            intent=r.intent,
            family_id=r.family_id,
            response_level=r.response_level.value,
            confidence=r.confidence,
            verse_ids=list(r.verse_ids),
            debug=r.debug,
        )
    )
    builder.set_benchmark(
        {
            "golden_query_accuracy": 1.0,
            "correct_family_selection": 1.0,
            "journey_regressions": 0,
        }
    )
    report = builder.build(tests_pass=True)
    assert report.release_blocked is False
    assert report.summary["evaluation_count"] == 1


def test_conversational_use_case_includes_evaluation() -> None:
    import asyncio

    from app.application.dto.answer import GenerateAnswerQuery
    from app.application.use_cases.answer.conversational_answer import ConversationalAnswerUseCase

    store = ConversationSessionStore()
    uc = ConversationalAnswerUseCase(session_store=store)

    async def _run():
        return await uc.execute(
            GenerateAnswerQuery(message="I'm terrified I'll fail my exams.")
        )

    result = asyncio.run(_run())
    assert "evaluation" in result.stages
    ev = result.stages["evaluation"]
    assert ev["overall_score"] >= 0.8
    assert result.answer  # user answer unchanged by evaluation presence
