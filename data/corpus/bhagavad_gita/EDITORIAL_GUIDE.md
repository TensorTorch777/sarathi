# Sarathi Editorial Guide

This guide keeps **Sarathi Intelligence** consistent across all 700 verses.

Authentic Scripture (Layer 1) is never rewritten here. We only curate guidance.

Related docs:

- `SOURCE_LICENSE.md` — provenance / rights
- `SARATHI_VOICE.md` — voice rules (distinct from tone checklists)
- `benchmarks/golden_queries.v0.json` — retrieval evaluation cases (when enough verses are approved)

---

## Editorial workflow

```text
generated → reviewed → approved → locked
```

| Status | Meaning |
|--------|---------|
| `generated` | First draft. Not production-ready. |
| `reviewed` | Human editorial pass applied. May need a second pass. |
| `approved` | Ready for production. Must pass the Approval Checklist. |
| `locked` | Stable. Further edits require explicit unlock + review. |

**Never auto-approve.**  
Liking a verse is not enough. Approval requires the checklist below.

Use `review_notes[]` as an audit trail.  
Use `misconceptions[]` when users commonly misread the teaching.

---

## Approval checklist (required for `approved`)

A verse may become **`approved` only if all seven criteria pass**:

| Criterion | Requirement |
|-----------|-------------|
| **Fidelity** | No claim contradicts or extends beyond what the verse supports. |
| **Clarity** | Understandable without prior Sanskrit or Vedanta training. |
| **Practicality** | Actionable without becoming preachy or overly prescriptive. |
| **Retrieval** | Topics, emotions, intents, life domains, and related verses would help retrieve this verse for relevant queries. |
| **Misconceptions** | Common misunderstandings are addressed when appropriate (especially for famous / easily distorted verses). |
| **Tone** | Calm, compassionate, and non-judgmental. |
| **Editorial** | Follows this guide and `SARATHI_VOICE.md`. |

Also ask:

> Would I trust Sarathi if it answered me like this?

If any criterion fails → stay at `reviewed` (or `generated`) and record why in `review_notes`.

---

## Review checks during drafting (`reviewed`)

Use these while editing (lighter than full approval):

| Check | Question |
|-------|----------|
| Fidelity | Does this stay faithful to the verse? |
| Practicality | Useful without distorting the teaching? |
| Retrieval | Would these tags help find this verse? |
| Tone | Calm and compassionate? |
| Boundaries | Avoid claiming what the verse does not say? |

---

## Field guide

### Summary

- One or two sentences, conversational.
- Name the central idea the user must not miss.
- For multi-verse units (e.g. Sthitaprajña 2.54–72), keep terminology consistent across the cluster.

### Modern interpretation

- Bridge to contemporary life.
- Distinguish **what the verse says** from **how Sarathi interprets it**.
- Add boundary sentences when a verse is commonly misread.

### Topics vs life domains

| Field | Use for | Examples |
|-------|---------|----------|
| `topics` | Teaching themes | karma, duty, detachment, right_action, yoga, equanimity |
| `life_domains` | Where life hurts | career, family, placements, grief_loss |

**Rule:** Career → `life_domains`, not `topics`, unless the verse is doctrinally about livelihood.

### Emotions

Tag states that lead people to *seek* the verse.

Prefer specific tags: `fear_of_failure`, `performance_pressure` when accurate.

### User intents / virtues / practice / reflection / related verses

See prior conventions: intents = why they came; virtues = what is cultivated; practice = small and doable; reflection = first-person; related = usefulness order.

### Misconceptions

Gentle corrections for false readings, e.g.:

- Detachment ≠ laziness  
- Sense withdrawal ≠ lifelong escape  
- Freedom from fruit-fixation ≠ abandoning ethics  

---

## Handling traditionally harsh terms

1. Stay faithful to the teaching.  
2. Prefer pastoral phrasing over insult.  
3. Record the decision in `review_notes`.

---

## Cluster review (preferred)

Review philosophical units together when possible:

1. **BG 2.47–2.50** — karma-yoga core *(reviewed)*  
2. **BG 2.54–2.72** — Sthitaprajña discourse *(next)*  
3. Chapter 6 — self-mastery & meditation  
4. Chapter 12 — qualities of the devotee  
5. BG 18.66 and surrounding verses  
6. Remaining generated corpus  

Do **not** default to purely sequential verse-by-verse if a unit would lose coherence.

---

## Review format

Review as the **end user**, not as JSON:

```bash
make review-cards SPEC=2.54-2.72
```

Or in chat:

> Review BG 2.54–2.72

---

## Progressive Disclosure

Most users do not want a mini-commentary on first contact.

Every enrichment should support three response depths:

| Level | When | Content |
|-------|------|---------|
| **L1 (default)** | First answer | One or two sentences from `summary` / essence |
| **L2** | User asks more | `modern_interpretation` |
| **L3** | User goes deeper | Related verses, misconceptions, Sanskrit concepts, philosophical nuance |

Keep Sarathi conversational. Do not dump L3 unless invited.

Approved enrichments may include a `response_levels` helper object for implementers.

---

## Verse Families

`related_verses` are pairwise hints.  
**Verse Families** are stronger editorial groupings for coherent teaching units.

See `sarathi_intelligence/verse_families.json`.

Examples:

- Karma Yoga Foundations — BG 2.47–2.50  
- Steady Wisdom (Sthitaprajña) — BG 2.54–72  
- Self Mastery — BG 6.5–10 *(planned)*  

**Retrieval preference:** prefer siblings in the same family before jumping across distant chapters.

Review philosophical units as families whenever possible.

---

## Versioning

| Layer | Example | Rule |
|-------|---------|------|
| Authentic Corpus | `v1.0.0` | Locked. Do not rewrite scripture. |
| Sarathi Intelligence | `v0.3.0` → `v1.0.0` | Editorial history via `CHANGELOG.md` |

Bump Intelligence version when a meaningful cluster is approved.

---

## Style anchors (current)

Approved clusters (Intelligence **v0.3.0**):

- Karma Yoga Foundations — BG 2.47–2.50  
- Steady Wisdom — BG 2.54–2.72  

Patterns to preserve:

- Conversational summaries  
- Sharp psychological lines when faithful  
- Careful retrieval tags  
- Softened judgmental Sanskrit renderings  
- Explicit misconceptions / boundaries  
- `reviewed` after first pass; `approved` only after checklist + second pass  

Update this guide when recurring decisions appear — do not invent local styles per chapter.
