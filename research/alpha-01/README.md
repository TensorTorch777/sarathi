# Alpha 01 — Internal Evidence Collection

**Status:** Prepared — no findings yet  
**Related product:** `sarathi-product-v0.7.0-alpha`  
**Related constitution:** [`VISION_2.0.md`](../../VISION_2.0.md)

This directory is the historical record of how Sarathi moves from assumptions to evidence.  
**Do not invent findings here.** Add observations only after real alpha sessions.

---

## Objectives

Answer whether people can use Sarathi without guidance, and whether they trust what they receive.

Primary questions:

- Which questions do people actually ask?
- Do they understand L1 without needing L2?
- How many are offered journeys, and how many accept?
- Which journeys are completed, abandoned, or never started?
- Which intents or life situations feel missing?
- Which responses feel too long or too shallow?
- Where do people get stuck or lose trust?

Secondary (engineering):

- Where does retrieval confidence look high but guidance feel weak?
- Where does editorial coverage fail for common real phrasing?

---

## Tester profile

Target: roughly **20–30** people for this first wave.

Prefer a mix of:

- Students or professionals under performance pressure
- People curious about the Gita without deep prior study
- A smaller set of readers already familiar with the text

Not required: technical background.  
Avoid: recruiting only friends who will compliment the project.

---

## Consent and privacy

- Testers should know this is an **early alpha**, not finished product or pastoral care.
- Prefer **anonymous** or lightly labeled notes (e.g. `T07`), not real names in this repo.
- **Do not commit message transcripts** unless a tester explicitly opts in to sharing anonymized quotes.
- Never commit credentials, contact details, or health information.
- If someone is in distress, stop product testing and point them to appropriate human support—Sarathi is not a crisis service.

Default recording: structured observations and aggregate counts, not full chat logs.

---

## Observation template

Copy one block per session (or per distinct conversation):

```text
### Session
- Tester ID:
- Date:
- Context (optional, non-identifying):

### Prompts tried
-

### What happened
- First answer understood? (Y/N/Partial)
- Asked for more depth (L2/L3)? (Y/N)
- Journey offered? (Y/N) — which:
- Journey accepted? (Y/N)
- Journey completed / abandoned at step:
- Trusted the response? (Y/N/Unsure) — why:

### Friction
- Too long / too shallow / confusing / wrong verse feel / other:

### Verbatim (only if opted in)
>

### Pattern tags
- (e.g. exam-anxiety, comparison, grief, discipline, missing-intent, retrieval-mismatch)
```

Aggregate patterns in a later `PATTERNS.md` only after several sessions exist.

---

## Success criteria (for closing Alpha 01)

Alpha 01 is “complete enough to inform a roadmap” when:

1. At least **20** sessions are documented with the template above.
2. Recurring patterns appear in at least **three** independent sessions each (not one-off anecdotes alone).
3. The team can list **concrete** editorial gaps and product frictions with evidence pointers—not opinions.
4. No silent expansion of product scope occurred “while testing.”

Passing success criteria does **not** automatically authorize new features. It authorizes writing the next roadmap from evidence.

---

## Open questions

Carry these until evidence answers them:

- Is progressive disclosure legible without explanation?
- Are journeys felt as guidance or as interruption?
- Does citing chapter/verse increase or decrease trust for newcomers?
- Which missing families would have changed outcomes most often?
- What should “done” look like for a single conversation?

---

## Repository rule during alpha

> No commits driven by ideas. Only commits driven by evidence.

Every future issue or change should answer at least one of:

- Which alpha observation motivated this?
- Which benchmark exposed this?
- Which editorial review required this?
- Which user conversation demonstrated the need?

If the answer is only “this would be cool,” it belongs in a backlog—not on `main`.

---

## Contents of this folder

| Path | Purpose |
|------|---------|
| `README.md` | This protocol |
| *(later)* session notes / `PATTERNS.md` | Evidence only |

No findings yet.
