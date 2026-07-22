# Sarathi AI

Production-oriented AI assistant grounded in the Bhagavad Gita.

**Foundational documents** (read before changing product or editorial behavior):

| Document | Answers |
|----------|---------|
| [`VISION_2.0.md`](VISION_2.0.md) | Why Sarathi exists (constitution) |
| [`PEDAGOGY.md`](PEDAGOGY.md) | How Sarathi teaches (scripture-centered) |
| [`data/corpus/bhagavad_gita/EDITORIAL_GUIDE.md`](data/corpus/bhagavad_gita/EDITORIAL_GUIDE.md) | How content is written and reviewed |
| [`data/corpus/bhagavad_gita/SARATHI_VOICE.md`](data/corpus/bhagavad_gita/SARATHI_VOICE.md) | How Sarathi is allowed to speak |

## Repository layout

```
apps/api/          FastAPI backend (Python 3.12 + Poetry)
infra/compose/     Shared Docker Compose service definitions
docs/              Architecture and product docs (stubs)
data/              Gita corpus and seeds (stubs)
scripts/           Ops / ingestion / eval scripts (stubs)
```

## Backend quick start

```bash
cp .env.example .env
make install
make up
make migrate
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- Version: http://localhost:8000/api/v1/version

Frontend is intentionally not included in this scaffold.
