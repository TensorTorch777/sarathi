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

Prefer specific tags: `fear_of_failure`, `performance_pressure`, `self_doubt`, `inner_conflict`, `mental_restlessness`, `discouragement`, `lack_of_focus` when accurate.

### User intents / virtues / practice / reflection / related verses

See prior conventions: intents = why they came; virtues = what is cultivated; practice = small and doable; reflection = first-person; related = usefulness order.

### Common queries (optional → recommended for high-traffic verses)

`common_queries` capture the **natural language people are likely to type**.

| Field | Answers | Example |
|-------|---------|---------|
| `topics` | What the verse is about | compassion, equanimity |
| `user_intents` | Why someone is asking | seeking_peace |
| `common_queries` | What they might type | "How do I become kinder?" |

Rules:

- Prefer 2–4 concrete, conversational phrases per verse when useful.  
- Not required on every verse; prioritize frequently retrieved / pastoral units.  
- Feed golden benchmarks and semantic retrieval — do not duplicate `topics`.  
- Keep Sarathi Voice: no guilt, no diagnosis, no promises.

### Misconceptions

Gentle corrections for false readings, e.g.:

- Detachment ≠ laziness  
- Sense withdrawal ≠ lifelong escape  
- Freedom from fruit-fixation ≠ abandoning ethics  
- Compassion ≠ staying in unsafe situations  

---

## Handling traditionally harsh terms

1. Stay faithful to the teaching.  
2. Prefer pastoral phrasing over insult.  
3. Record the decision in `review_notes`.

---

## Cluster review (preferred)

Review philosophical units together when possible:

1. **BG 2.47–2.50** — karma-yoga core *(approved, anchor)*  
2. **BG 2.54–2.72** — Sthitaprajña discourse *(approved, anchor)*  
3. **BG 6.5–6.10** — Self Mastery *(approved, anchor)*  
4. **BG 12.13–12.20** — Devotional Character *(approved, anchor)*  
5. **BG 12.8–12.12** — Devotional Practice  
6. **BG 12.1–12.7** — Nature of Worship  
7. BG 18.66 cluster · Chapter 3 depth · remainder of Chapter 6  
8. Remaining generated corpus  

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

- Karma Yoga Foundations — BG 2.47–2.50 *(anchor)*  
- Steady Wisdom (Sthitaprajña) — BG 2.54–72 *(anchor)*  
- Self Mastery — BG 6.5–10 *(anchor)*  
- Devotional Character — BG 12.13–20 *(anchor)*  
- Devotional Practice — BG 12.8–12  
- Nature of Worship — BG 12.1–7  

**Retrieval preference:** prefer siblings in the same family before jumping across distant chapters.

Review philosophical units as families whenever possible.

### Anchor families

**Anchor families** are the editorial exemplars every new family should match in style and quality.

Current anchors (`anchor_family: true` in `verse_families.json`):

1. Karma Yoga Foundations (BG 2.47–2.50)  
2. Steady Wisdom / Sthitaprajña (BG 2.54–2.72)  
3. Self Mastery (BG 6.5–6.10)  
4. Devotional Character (BG 12.13–12.20)  

When reviewing a new family, ask:

> Does this meet the bar set by the anchor families — fidelity, voice, misconceptions, and practical clarity?

Promote a family to anchor only after approval + second-pass confidence that it should define future style.

### Family overview (required for approved families)

Each approved family in `verse_families.json` should eventually include:

| Field | Purpose |
|-------|---------|
| `overview` | Short pastoral introduction for journeys / education (does not replace verse-level content) |
| `family_misconceptions` | Cross-cutting misreadings that apply to the whole unit |
| `theme` | Compact retrieval / editorial label |
| `why_this_matters_today` | Bridge from ancient teaching to modern relevance (onboarding, journeys, education — not a second interpretation) |

Example pattern (Self Mastery):

> This group of verses explores how disciplined attention transforms the mind from an obstacle into an ally…

Do not put family overviews into Layer 1 scripture files.

### Editorial vocabulary (reuse when faithful)

Prefer these phrases when the teaching supports them — consistency helps Sarathi's voice:

| Phrase | Use when |
|--------|----------|
| *adding / creating / reducing turbulence* | Relational composure (esp. BG 12.15 lineage) |
| *equal worth ≠ equal usefulness* | Equanimity toward objects/people without practical blindness |
| *results are not a verdict on your worth* | Detachment from outcomes without self-erasure |
| *effort without blame* | Self-responsibility that is not self-condemnation |

---

## Versioning

| Layer | Example | Rule |
|-------|---------|------|
| Authentic Corpus | `v1.0.0` | Locked. Do not rewrite scripture. |
| Sarathi Intelligence | `v0.5.0` → `v1.0.0` | Editorial history via `CHANGELOG.md` |

Bump Intelligence version when a meaningful cluster is approved.

---

## Style anchors (current)

**Four anchor pillars** (Intelligence **v0.5.0**):

1. Karma Yoga Foundations — BG 2.47–2.50 — purposeful action without attachment  
2. Steady Wisdom — BG 2.54–2.72 — inner equanimity  
3. Self Mastery — BG 6.5–6.10 — training the mind with compassion  
4. Devotional Character — BG 12.13–12.20 — spirituality through everyday conduct  

Patterns to preserve:

- Conversational summaries  
- Sharp psychological lines when faithful  
- Careful retrieval tags + `common_queries` on high-traffic verses  
- Softened judgmental Sanskrit renderings  
- Explicit misconceptions / boundaries (especially psychology / safety)  
- Effort without blame; steadiness without numbness; compassion without unsafe endurance  
- `reviewed` after first pass; `approved` only after checklist + second pass  

Update this guide when recurring decisions appear — do not invent local styles per chapter.
