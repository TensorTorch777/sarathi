"""Tests for the grounded Gita prompt builder."""

from uuid import uuid4

import pytest

from app.application.dto.retrieval import RankedVerse
from app.infrastructure.answer.generator import TemplateAnswerGenerator
from app.infrastructure.answer.prompt_builder import GroundedPromptBuilder


def _verse(chapter: int, number: int, translation: str) -> RankedVerse:
    return RankedVerse(
        verse_id=uuid4(),
        chapter=chapter,
        verse_number=number,
        citation=f"BG {chapter}.{number}",
        sanskrit=f"sanskrit-{chapter}-{number}",
        translation=translation,
        transliteration=None,
        commentary="Teach detachment from outcomes.",
        topics=["karma", "duty"],
        emotions=["anxiety"],
        verified=True,
    )


def test_prompt_forbids_krishna_identity() -> None:
    builder = GroundedPromptBuilder()
    prompt = builder.build(
        message="I am anxious about results",
        emotions=["anxiety"],
        topics=["karma"],
        verses=[_verse(2, 47, "Act without attachment to fruits.")],
    )
    system = prompt.system_prompt.lower()
    assert "not krishna" in system
    assert "never speak as krishna" in system
    assert "never invent" in system or "never fabricate" in system


def test_prompt_requires_structured_sections() -> None:
    builder = GroundedPromptBuilder()
    prompt = builder.build(
        message="Help me with duty",
        emotions=["anxiety"],
        topics=["duty"],
        verses=[
            _verse(2, 47, "Act without attachment to fruits."),
            _verse(18, 66, "Take refuge and do not fear."),
        ],
    )
    system = prompt.system_prompt
    for heading in (
        "### Relevant verse",
        "### Translation",
        "### Meaning",
        "### Modern interpretation",
        "### Actionable advice",
        "### Reflection question",
        "### Related verses",
    ):
        assert heading in system

    assert "BG 2.47" in prompt.user_prompt
    assert "BG 18.66" in prompt.user_prompt
    assert "Allowed citations" in prompt.user_prompt
    assert "Act without attachment to fruits." in prompt.user_prompt


def test_prompt_with_no_verses_does_not_invent_citations() -> None:
    builder = GroundedPromptBuilder()
    prompt = builder.build(
        message="Who am I?",
        emotions=[],
        topics=[],
        verses=[],
    )
    assert "No verses retrieved." in prompt.user_prompt
    assert "Allowed citations (use ONLY these exact labels): none" in prompt.user_prompt
    assert "do not invent" in prompt.user_prompt.lower()


@pytest.mark.asyncio
async def test_template_generator_emits_required_sections() -> None:
    builder = GroundedPromptBuilder()
    prompt = builder.build(
        message="I feel anxious about duty",
        emotions=["anxiety"],
        topics=["duty"],
        verses=[
            _verse(2, 47, "You have a right to duty but not to the fruits."),
            _verse(6, 5, "Elevate yourself by your own mind."),
        ],
    )
    answer = await TemplateAnswerGenerator().generate(prompt)
    for heading in (
        "### Relevant verse",
        "### Translation",
        "### Meaning",
        "### Modern interpretation",
        "### Actionable advice",
        "### Reflection question",
        "### Related verses",
    ):
        assert heading in answer
    assert "BG 2.47" in answer
    assert "not as krishna" in answer.lower()
