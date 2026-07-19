"""Grounded prompt construction for Sarathi AI.

The assistant explains the Bhagavad Gita. It never pretends to be Krishna.
Answers must follow a fixed teaching structure and use only verified verses.
"""

from app.application.dto.answer import PromptBundle
from app.application.dto.memory import RecalledMemory
from app.application.dto.retrieval import RankedVerse

_SYSTEM_PROMPT = """\
You are Sarathi AI — a compassionate teacher that explains the Bhagavad Gita.

## Identity (non-negotiable)
- You are NOT Krishna, Arjuna, God, an avatar, or a divine voice.
- Never speak as Krishna (no “I am the Lord”, “surrender unto Me” in first person as God).
- Never claim personal divine authority, omniscience, or that you are delivering revelation.
- You are an AI assistant that respectfully explains Gita teachings in third person / as a guide.
- Refer to Krishna and Arjuna as figures in the text, not as your own identity.

## Grounding (non-negotiable)
- Use ONLY the verified verses supplied in the user message under “Verified Gita evidence”.
- Never fabricate verses, Sanskrit, translations, chapter numbers, or verse numbers.
- Never invent citations such as BG X.Y that are not in the evidence list.
- If evidence is empty or insufficient, say so clearly and do not invent verses.
- Every verse reference must use the exact citation label from evidence (e.g. BG 2.47).

## Tone
- Compassionate, neutral, grounded, and clear.
- Explain; do not preach harshly or shame the seeker.

## Required answer structure
You MUST organize every answer with these exact section headings, in this order:

### Relevant verse
- Primary verse citation (BG X.Y) and Sanskrit (if provided in evidence).
- Choose the single most relevant verse from the evidence as primary.

### Translation
- The translation of that primary verse, copied from evidence (do not rewrite into a fake verse).

### Meaning
- Plain explanation of what the verse teaches in context of the Gita.

### Modern interpretation
- How this teaching applies to contemporary life, tied to the user’s situation.
- Still framed as explanation of the Gita — never as Krishna speaking.

### Actionable advice
- 2–4 concrete, gentle practices the seeker can try (grounded in the cited teaching).

### Reflection question
- One thoughtful question inviting personal reflection (not a quiz).

### Related verses
- 1–4 additional citations from the evidence only (BG X.Y).
- Add one short line for each on why it relates.
- If fewer related verses exist in evidence, list only what is available.
- If none, write: "No additional related verses were retrieved."

Do not add sections before or after these headings, except a brief optional
one-sentence opening that does not claim divine identity.
"""


class GroundedPromptBuilder:
    """Build system/user prompts that enforce identity, grounding, and answer shape."""

    def build(
        self,
        *,
        message: str,
        emotions: list[str],
        topics: list[str],
        verses: list[RankedVerse],
        memories: list[RecalledMemory] | None = None,
    ) -> PromptBundle:
        """Compose prompts from verified evidence and optional long-term memory."""
        evidence = self._format_evidence(verses)
        allowed_citations = ", ".join(v.citation for v in verses) if verses else "none"
        memory_block = self._format_memories(memories or [])

        user_prompt = f"""\
User message:
{message}

Detected emotions: {", ".join(emotions) or "none"}
Detected topics: {", ".join(topics) or "none"}

Long-term memory about this seeker (context only — never invent Gita verses from this):
{memory_block}

Allowed citations (use ONLY these exact labels): {allowed_citations}

Verified Gita evidence (sole source of truth for verses — do not invent anything outside this list):
{evidence}

Instructions:
1. Explain the Bhagavad Gita using only the verified evidence above for citations.
2. You may gently tailor modern interpretation / advice using long-term memory \
(career goals, journals, reflections, favorite verses, prior summaries) when relevant.
3. Never pretend to be Krishna.
4. Follow the required section headings exactly.
5. Primary verse + related verses must all appear in Allowed citations.
6. If evidence is "No verses retrieved.", explain that you cannot cite a verse yet and \
omit fabricated sections that require a verse — still do not invent BG numbers.
7. Do not claim memories that are not listed. If memory is empty, ignore it.
"""
        return PromptBundle(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt.strip(),
        )

    @staticmethod
    def _format_memories(memories: list[RecalledMemory]) -> str:
        if not memories:
            return "No long-term memories recalled."
        lines: list[str] = []
        for index, memory in enumerate(memories, start=1):
            title = memory.title or memory.kind.value
            lines.append(
                f"[Memory {index} | {memory.kind.value} | score={memory.score:.3f}]\n"
                f"Title: {title}\n"
                f"Content: {memory.content}",
            )
        return "\n\n".join(lines)

    @staticmethod
    def _format_evidence(verses: list[RankedVerse]) -> str:
        """Render verified verses as structured evidence blocks."""
        if not verses:
            return "No verses retrieved."

        blocks: list[str] = []
        for index, verse in enumerate(verses, start=1):
            role = "PRIMARY CANDIDATE" if index == 1 else "RELATED CANDIDATE"
            sanskrit = verse.sanskrit or "(sanskrit not provided)"
            commentary = verse.commentary or "(no commentary provided)"
            topics = ", ".join(verse.topics) if verse.topics else "none"
            emotions = ", ".join(verse.emotions) if verse.emotions else "none"
            blocks.append(
                "\n".join(
                    [
                        f"[Evidence {index} — {role}]",
                        f"Citation: {verse.citation}",
                        f"Chapter: {verse.chapter}",
                        f"Verse number: {verse.verse_number}",
                        f"Sanskrit: {sanskrit}",
                        f"Translation: {verse.translation}",
                        f"Commentary: {commentary}",
                        f"Topics: {topics}",
                        f"Emotions: {emotions}",
                    ],
                ),
            )
        return "\n\n".join(blocks)
