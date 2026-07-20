# Sarathi Conversation Engine

**Release:** `v0.6.0-product-alpha`  
**Package:** `apps/api/app/conversation/`

## Purpose

An **editorially-driven wisdom conversation engine** — not a generic chatbot.

It knows how much to say, when to deepen, when to ask one clarifying question, and when to stay practical. Answers are assembled from **approved Sarathi Intelligence**, not free-form LLM lectures.

## Frozen foundation (do not modify)

- Authentic Scripture v1.0.0  
- Sarathi Intelligence v0.5.0 (+ in-review content readable but ranked lower)  
- Editorial Guide v1.0  
- Anchor families  

## Flow

```text
Question
  → UNDERSTAND (intent)
  → RETRIEVE (editorial priority)
  → RESPOND_L1
  → WAIT
  → RESPOND_L2 (on “why / explain / more”)
  → WAIT
  → RESPOND_L3 (on explicit depth / philosophy)
```

No state skipping.

## Progressive disclosure

| Level | Trigger | Content |
|-------|---------|---------|
| **L1** | First answer | Summary + one practice · max ~2 paragraphs |
| **L2** | “why?”, “tell me more”, “explain” | Interpretation + misconceptions + related verse |
| **L3** | Explicit depth / philosophy | Family overview, why-this-matters, related families |

L3 is never automatic.

## Retrieval priority

```text
Approved Anchor → Approved Core → Approved → Reviewed → Generated
```

Editorial quality outweighs bare lexical similarity. Matching uses topics, emotions, and `common_queries` — **no new embeddings**.

## Intent (deterministic)

`guidance` · `reflection` · `learning` · `crisis` · `comparison` · `search`

No AI agents.

## Follow-ups

At most **one** follow-up, only when:

- multiple equally relevant families, or  
- low retrieval confidence  

Otherwise answer directly.

## Safety

Rejects: promises, diagnosis, guilt, punishment framing, abusive-relationship advice, invalid citations.

## Debug (developer only)

`apps/api/debug/debug_response.json` after each turn:

- intent, family, verses, confidence  
- response level, misconceptions, practice, reflection  
- safety checks  

Never shown to end users.

## Wisdom journeys (M2)

Curated paths live in `data/journeys/*.json` (approved verses only).

After a confident L1, Sarathi may **offer** a journey. The user may ignore, decline, accept, continue, or exit anytime.

```text
L1 answer
  → optional journey offer
  → "yes" → step 1 (verse + practice + reflection)
  → "continue" → next step
  → "stop" → exit
```

Modules: `journey_loader.py`, `journey_selector.py`, `journey_renderer.py`.

Rules: never offer on low confidence; never use generated-only steps; no AI-generated journey content.

## API

`POST /api/v1/chat/ask` → `ConversationalAnswerUseCase` → `ConversationEngine`

Pass the same `conversation_id` across turns for L1→L2→L3 and journeys.

Legacy LLM pipeline (`GenerateAnswerUseCase`) remains available for other callers but is not the product-alpha chat path.

## Modules

| File | Role |
|------|------|
| `conversation_state.py` | State machine + journey progress |
| `conversation_engine.py` | Orchestrator |
| `intent_classifier.py` | Deterministic intents |
| `editorial_retriever.py` | Priority retrieval |
| `response_builder.py` | Natural L1/L2/L3 prose |
| `followup_selector.py` | Single follow-up policy |
| `safety_checker.py` | Voice / safety gates |
| `intelligence_loader.py` | Read-only corpus index |
| `journey_loader.py` | Curated journey catalog |
| `journey_selector.py` | Optional journey offer |
| `journey_renderer.py` | Step prose + accept/continue/exit cues |
| `session_store.py` | In-memory progressive-disclosure sessions |

## Tests

```bash
cd apps/api && poetry run pytest tests/conversation -q
```

See also: `PRODUCT_RELEASES.md` (editorial vs product version streams).
