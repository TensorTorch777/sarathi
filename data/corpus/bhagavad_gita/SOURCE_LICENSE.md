# Corpus source licensing — Gita Supersite

Sarathi uses **IIT Kanpur’s Gita Supersite** as a *technical* source for verse
structure and Devanagari text. That does **not** automatically grant rights to
redistribute every translation or commentary hosted there.

## What the Supersite says

The project’s acknowledgement page states that copyrights of the books remain
with the original organisations / publishers. Contact those publishers (and the
Supersite maintainers if needed) before bundling their translations or
commentaries inside a product.

Contacts listed by the project include:

- Dr. Prabhakar T.V — `tvp@iitk.ac.in`
- Acknowledgement / publisher list on the Supersite site

## Sarathi policy

| Content | Default |
|--------|---------|
| Sanskrit shlokas (ancient text) | Allowed in Layer 1 (`--sanskrit-only`) |
| Transliteration | Only if present in source (often absent) |
| English/Hindi translations | **Opt-in** + `--acknowledge-license` after permission |
| Commentaries | **Opt-in** + same acknowledgement |
| Sarathi summaries / topics / practices | Layer 2 — human curated, never auto-invented at import |

## Importer outputs

- Cached HTML and Layer-1 extracts with copyrighted text belong under  
  `data/corpus/bhagavad_gita/sources/` (gitignored).
- Curated Layer-2 samples live under `samples/` and are hand-authored.

## Commands

```bash
make import-gita-supersite-license   # print notice
make import-gita-supersite           # Sanskrit-only Layer 1 (safe default)
```
