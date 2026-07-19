"""Idempotent HTML cache for Gita Supersite verse pages."""

from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import urlencode

import httpx

from app.importers.gita_supersite.constants import DEFAULT_BASE_URL, DEFAULT_FIELD_FLAGS


class GitaSupersiteDownloader:
    """
    Download verse HTML into a local cache directory.

    Idempotent: skips network when a non-empty cache file already exists.
    Never used from application request handlers — CLI / offline jobs only.
    """

    def __init__(
        self,
        cache_dir: Path,
        *,
        base_url: str = DEFAULT_BASE_URL,
        field_flags: dict[str, str] | None = None,
        timeout_seconds: float = 45.0,
        pause_seconds: float = 0.15,
        user_agent: str = "SarathiCorpusImporter/0.1 (+offline corpus build; not runtime)",
    ) -> None:
        self.cache_dir = cache_dir
        self.base_url = base_url.rstrip("/")
        self.field_flags = field_flags or dict(DEFAULT_FIELD_FLAGS)
        self.timeout_seconds = timeout_seconds
        self.pause_seconds = pause_seconds
        self.user_agent = user_agent
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cache_path(self, chapter: int, verse: int) -> Path:
        """Path for a single verse HTML cache file."""
        chapter_dir = self.cache_dir / f"chapter_{chapter:02d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        return chapter_dir / f"verse_{verse:02d}.html"

    def verse_url(self, chapter: int, verse: int) -> str:
        """Construct the legacy Drupal verse URL."""
        params = {
            **self.field_flags,
            "field_chapter_value": str(chapter),
            "field_nsutra_value": str(verse),
        }
        return f"{self.base_url}/srimad?{urlencode(params)}"

    async def fetch_verse(
        self,
        chapter: int,
        verse: int,
        *,
        force: bool = False,
    ) -> Path:
        """Return cached HTML path, downloading when missing."""
        path = self.cache_path(chapter, verse)
        if path.exists() and path.stat().st_size > 0 and not force:
            return path

        url = self.verse_url(chapter, verse)
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            path.write_text(response.text, encoding="utf-8")

        if self.pause_seconds > 0:
            await asyncio.sleep(self.pause_seconds)
        return path

    def read_cached(self, chapter: int, verse: int) -> str | None:
        """Read cache without network; None if missing."""
        path = self.cache_path(chapter, verse)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
