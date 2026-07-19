"""
Gita Supersite (IIT Kanpur) → Sarathi Layer-1 corpus importer.

Offline / CLI only. Not used by chat or retrieval at runtime.
"""

from app.importers.gita_supersite.pipeline import GitaSupersiteImportPipeline, ImportResult

__all__ = ["GitaSupersiteImportPipeline", "ImportResult"]
