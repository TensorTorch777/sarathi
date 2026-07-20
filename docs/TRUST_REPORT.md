# Sarathi Trust Report

Engineering transparency — not marketing.

**Product release:** `v0.7.0-product-alpha`  
**Editorial release:** `sarathi-intelligence-v0.5.0`  
**Generated:** 2026-07-20T20:06:09Z  
**Release gate:** passing

## Approved anchor families

- Karma Yoga Foundations (BG 2.47–2.50)
- Steady Wisdom / Sthitaprajña (BG 2.54–2.72)
- Self Mastery (BG 6.5–6.10)
- Devotional Character (BG 12.13–12.20)

## Benchmark summary

- Golden query accuracy (ready cases): **1.0**
- Correct family selection: **1.0**
- Average editorial score: **0.9333**
- Average overall score: **0.9631**
- Safety failures in scored sample: **0**

## Safety philosophy

- No promises, diagnosis, guilt, or divine-punishment framing.
- Safety is checked on assembled editorial text — not hoped for from an LLM.
- Progressive disclosure: L1 first; L2/L3 only when invited.
- Journeys are curated from approved verses only.

## Known limitations

- Not all golden queries are fully `depends_on_approved` ready; accuracy is computed on ready cases.
- Evaluation scores are heuristic inspectors of editorial principles, not human raters.
- Lexical editorial retrieval is used for the conversation engine (no new embeddings in product-alpha).
- Trust dashboard is read-only developer/ops visibility.

## Gates

- `golden_query_accuracy`: 1.0 (threshold 0.95) — pass
- `correct_family_selection`: 1.0 (threshold 0.95) — pass
- `safety_violations`: 0 (threshold 0) — pass
- `journey_regression`: 0 (threshold 0) — pass
- `editorial_score`: 0.9333 (threshold 0.9) — pass
- `tests`: True (threshold True) — pass
