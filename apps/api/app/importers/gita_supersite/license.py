"""
Licensing gate for Gita Supersite imports.

The Supersite acknowledgement states that copyrights of books remain with
the original organisations. Bulk reuse of translations/commentaries into an
application requires permission from those rights holders.

Sanskrit shlokas themselves are ancient public-domain text; extracting
Devanagari verse text alone is the safest default redistributable mode.
"""

from __future__ import annotations

LICENSE_NOTICE = """
Gita Supersite content licensing (summary)
------------------------------------------
Source: https://www.gitasupersite.iitk.ac.in/ (also old.gitasupersite.in /
https://www.gitasupersite.in/)

Per the project's acknowledgement page, copyrights of the hosted books
(translations and commentaries) remain with the original publishers /
organisations. Studying on the site ≠ permission to redistribute their
texts inside Sarathi.

Safe default for Sarathi:
  --sanskrit-only   extract Devanagari shlokas + structure (Layer 1)

Including translations/commentaries requires:
  --include-copyrighted-text
  --acknowledge-license

Contact (from Supersite contact page):
  Dr. Prabhakar T.V — tvp@iitk.ac.in
  Also contact individual publishers listed on the acknowledgement page.
""".strip()

ACK_PHRASE = "I_UNDERSTAND_COPYRIGHTS_REMAIN_WITH_PUBLISHERS"


def assert_copyrighted_allowed(*, include_copyrighted: bool, acknowledge: str | None) -> None:
    """Raise if copyrighted extract requested without explicit acknowledgement."""
    if not include_copyrighted:
        return
    if (acknowledge or "").strip() != ACK_PHRASE:
        raise PermissionError(
            "Refusing to extract copyrighted translations/commentaries.\n"
            f"Re-run with --include-copyrighted-text --acknowledge-license {ACK_PHRASE}\n"
            f"after obtaining permission where needed.\n\n{LICENSE_NOTICE}"
        )
