"""Tests for speech-friendly answer conversion."""

from app.infrastructure.voice.spoken_text import answer_to_spoken, iter_speakable_sentences


def test_answer_to_spoken_strips_markdown_and_sanskrit() -> None:
    answer = """
### Relevant verse
BG 2.47
कर्मण्येवाधिकारस्ते

### Translation
You have a right to perform your duty.

### Meaning
Act without clinging to results.
"""
    spoken = answer_to_spoken(answer)
    assert "BG 2.47" in spoken or "duty" in spoken.lower()
    assert "###" not in spoken
    assert "कर्म" not in spoken


def test_iter_speakable_sentences_splits_completed_clauses() -> None:
    ready, rem = iter_speakable_sentences(
        "Act with care. Release attachment to outcomes you cannot control",
    )
    assert ready == ["Act with care."]
    assert "Release attachment" in rem
