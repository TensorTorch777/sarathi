"""Answer generation adapters — local Gemma via Ollama, plus test template."""

import re
from collections.abc import AsyncIterator

from app.application.dto.answer import PromptBundle
from app.core.config import Settings
from app.infrastructure.llm.ollama import OllamaClient

_CITATION_LINE = re.compile(r"Citation:\s*(BG\s*\d+\s*[.:]\s*\d+)", re.IGNORECASE)
_TRANSLATION_LINE = re.compile(r"Translation:\s*(.+)")
_SANSKRIT_LINE = re.compile(r"Sanskrit:\s*(.+)")
_COMMENTARY_LINE = re.compile(r"Commentary:\s*(.+)")


class OllamaAnswerGenerator:
    """Generate grounded answers with a local Gemma model through Ollama."""

    def __init__(self, settings: Settings, client: OllamaClient | None = None) -> None:
        self._settings = settings
        self._client = client or OllamaClient(settings)

    async def generate(self, prompt: PromptBundle) -> str:
        """Return a completion from the local chat model."""
        return await self._client.complete(
            system=prompt.system_prompt,
            user=prompt.user_prompt,
            temperature=0.4,
        )

    async def generate_stream(self, prompt: PromptBundle) -> AsyncIterator[str]:
        """Stream completion deltas from the local chat model."""
        async for delta in self._client.complete_stream(
            system=prompt.system_prompt,
            user=prompt.user_prompt,
            temperature=0.4,
        ):
            yield delta


class TemplateAnswerGenerator:
    """Deterministic structured answer for unit tests (no model runtime)."""

    async def generate(self, prompt: PromptBundle) -> str:
        """Build the required teaching sections from evidence in the prompt."""
        return self._build(prompt)

    async def generate_stream(self, prompt: PromptBundle) -> AsyncIterator[str]:
        """Yield the full template answer as a single delta (tests / offline)."""
        yield await self.generate(prompt)

    def _build(self, prompt: PromptBundle) -> str:
        """Build the required teaching sections from evidence in the prompt."""
        entries = self._parse_evidence(prompt.user_prompt)
        if not entries:
            return (
                "### Relevant verse\n"
                "No verified verse was retrieved, so Sarathi AI cannot cite the Gita yet.\n\n"
                "### Translation\n"
                "Unavailable without retrieved evidence.\n\n"
                "### Meaning\n"
                "Please rephrase your question so relevant verses can be found.\n\n"
                "### Modern interpretation\n"
                "Without a grounded verse, I will not invent chapter or verse numbers.\n\n"
                "### Actionable advice\n"
                "- Take a quiet breath and restate your concern in one sentence.\n"
                "- Ask again with the feeling or theme you want help with.\n\n"
                "### Reflection question\n"
                "What part of your situation most needs clarity right now?\n\n"
                "### Related verses\n"
                "No additional related verses were retrieved."
            )

        primary = entries[0]
        related = entries[1:4]
        related_lines = (
            "\n".join(
                f"- {item['citation']}: relates to the same teaching thread as the primary verse."
                for item in related
            )
            if related
            else "No additional related verses were retrieved."
        )
        meaning = primary["commentary"]
        if meaning.startswith("(no commentary"):
            meaning = (
                f"This verse ({primary['citation']}) teaches a principle from the Bhagavad Gita "
                "that can steady the mind when life feels uncertain."
            )

        return "\n".join(
            [
                "### Relevant verse",
                f"{primary['citation']}",
                primary["sanskrit"],
                "",
                "### Translation",
                primary["translation"],
                "",
                "### Meaning",
                meaning,
                "",
                "### Modern interpretation",
                (
                    "In everyday life, this teaching invites you to act with care while releasing "
                    "anxious clinging to outcomes you cannot fully control. "
                    "Sarathi AI explains the Gita here as a guide — not as Krishna speaking."
                ),
                "",
                "### Actionable advice",
                "- Name one duty you can perform today with full attention.",
                "- After acting, pause and consciously release attachment to the result.",
                "- When worry returns, return to the breath and the cited teaching.",
                "",
                "### Reflection question",
                "Where in your life are you confusing effort with control over outcomes?",
                "",
                "### Related verses",
                related_lines,
            ],
        ).strip()

    @staticmethod
    def _parse_evidence(user_prompt: str) -> list[dict[str, str]]:
        """Extract citation/translation pairs from the prompt evidence blocks."""
        entries: list[dict[str, str]] = []
        current: dict[str, str] = {}

        for line in user_prompt.splitlines():
            cite_match = _CITATION_LINE.search(line)
            if cite_match:
                if current.get("citation") and current.get("translation"):
                    entries.append(current)
                citation = re.sub(
                    r"BG\s*(\d+)\s*[.:]\s*(\d+)",
                    r"BG \1.\2",
                    cite_match.group(1),
                    flags=re.IGNORECASE,
                )
                current = {
                    "citation": citation,
                    "sanskrit": "",
                    "translation": "",
                    "commentary": "",
                }
                continue

            if not current:
                continue

            sanskrit_match = _SANSKRIT_LINE.search(line)
            if sanskrit_match:
                current["sanskrit"] = sanskrit_match.group(1).strip()
                continue

            translation_match = _TRANSLATION_LINE.search(line)
            if translation_match:
                current["translation"] = translation_match.group(1).strip()
                continue

            commentary_match = _COMMENTARY_LINE.search(line)
            if commentary_match:
                current["commentary"] = commentary_match.group(1).strip()

        if current.get("citation") and current.get("translation"):
            entries.append(current)
        return entries
