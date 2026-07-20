# Sarathi Product Releases

Product capabilities evolve separately from editorial corpus quality.

| Stream | Versioning | Tracks |
|--------|------------|--------|
| **Editorial** | `sarathi-intelligence-v0.x` | Approved families, enrichments, Editorial Guide |
| **Product** | `sarathi-product-v0.x` | Conversation engine, journeys, evaluation, UI |

## Current

| Stream | Tag / Version | Notes |
|--------|---------------|-------|
| Editorial | `sarathi-intelligence-v0.5.0` | 4 anchor families · Guide v1.0 frozen |
| Product | `sarathi-product-v0.7.0-alpha` | Conversation + Journeys + Evaluation & Trust (M3) |

Do not conflate UI/feature releases with corpus approvals.

## Product freeze after v0.7.0-alpha

**No new product features** until internal alpha evidence exists.

Next product engineering (when needed): **M4 — Observability & Analytics** (anonymous conversation analytics).  
Editorial work continues independently as `sarathi-intelligence-v0.6.x+`.

## M3 notes

Every product response can carry an `evaluation` object (developer diagnostics).  
Release gates live in `apps/api/reports/` after `make eval`.  
Public engineering transparency: `docs/TRUST_REPORT.md`.  
Trust dashboard (read-only): `/admin/trust`.
