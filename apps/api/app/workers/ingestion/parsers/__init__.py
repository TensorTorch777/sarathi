"""Scripture-specific parsers for the ingestion pipeline."""

from app.workers.ingestion.parsers.base import ScriptureParser
from app.workers.ingestion.parsers.bhagavad_gita import BhagavadGitaParser
from app.workers.ingestion.parsers.mahabharata import MahabharataParser
from app.workers.ingestion.parsers.ramayana import RamayanaParser
from app.workers.ingestion.parsers.upanishad import UpanishadParser

__all__ = [
    "ScriptureParser",
    "BhagavadGitaParser",
    "UpanishadParser",
    "RamayanaParser",
    "MahabharataParser",
]
