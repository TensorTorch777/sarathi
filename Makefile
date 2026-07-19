.PHONY: help up down logs api-shell migrate migrate-create lint test install seed-verses pull-models web web-install voice-models validate-corpus build-corpus import-gita-supersite import-gita-supersite-license

help:
	@echo "Sarathi AI — common commands"
	@echo "  make install          Install API deps with Poetry"
	@echo "  make web-install      Install Next.js frontend deps"
	@echo "  make web              Start Next.js frontend (localhost:3000)"
	@echo "  make pull-models      Pull local Gemma 4 + embed model via Ollama"
	@echo "  make voice-models     Download Piper TTS voice for calm narration"
	@echo "  make validate-corpus  Validate canonical corpus JSON"
	@echo "  make build-corpus     Validate + emit corpus build artifact"
	@echo "  make import-gita-supersite  Offline Layer-1 import (default: all chapters)"
	@echo "  make import-gita-supersite-license  Print Supersite licensing notice"
	@echo "  make generate-intelligence  Generate Sarathi Intelligence drafts (700)"
	@echo "  make review-cards SPEC=2.47-2.50  Render end-user review cards"
	@echo "  make up               Start Docker Compose stack"
	@echo "  make down             Stop Docker Compose stack"
	@echo "  make logs             Tail API logs"
	@echo "  make api-shell        Shell into API container"
	@echo "  make migrate          Run Alembic migrations"
	@echo "  make migrate-create   Create a new Alembic revision (msg=...)"
	@echo "  make seed-verses      Seed sample Gita verses (+ local Qdrant index)"
	@echo "  make lint             Run ruff on API"
	@echo "  make test             Run API tests"

install:
	cd apps/api && poetry install --with voice

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

api-shell:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

migrate-create:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

lint:
	cd apps/api && poetry run ruff check app tests

test:
	cd apps/api && poetry run pytest

seed-verses:
	cd apps/api && poetry run python ../../scripts/ingestion/seed_and_index_verses.py

# Master corpus is the only runtime knowledge source. Importers are offline-only.
validate-corpus:
	cd apps/api && poetry run python ../../scripts/corpus/validate_corpus.py \
		../../data/corpus/bhagavad_gita/bhagavad_gita.json \
		../../data/corpus/bhagavad_gita/samples/bg_2_47_50.curated.json

build-corpus:
	cd apps/api && poetry run python ../../scripts/corpus/build_corpus.py \
		--source ../../data/corpus/bhagavad_gita/bhagavad_gita.json \
		--out ../../data/corpus/bhagavad_gita/build

import-gita-supersite-license:
	cd apps/api && poetry run python ../../scripts/corpus/import_gita_supersite.py --print-license

# Offline one-time extract → master bhagavad_gita.json (SSOT). Default: all 18 chapters.
# Partial: make import-gita-supersite CHAPTERS=2
CHAPTERS ?=
import-gita-supersite:
	cd apps/api && poetry run python ../../scripts/corpus/import_gita_supersite.py \
		$(if $(CHAPTERS),--chapters $(CHAPTERS),) \
		--sanskrit-only \
		--out ../../data/corpus/bhagavad_gita/bhagavad_gita.json \
		--cache-dir ../../data/corpus/bhagavad_gita/sources/gita_supersite/raw

generate-intelligence:
	cd apps/api && poetry run python ../../scripts/corpus/generate_sarathi_intelligence.py

# End-user style review cards (not raw JSON). Example: make review-cards SPEC=2.47-2.50
SPEC ?= 2.47-2.50
review-cards:
	cd apps/api && poetry run python ../../scripts/corpus/render_review_cards.py "$(SPEC)"

pull-models:
	# Prefer user-local Ollama on :11435 (Gemma 4 needs >= 0.20)
	OLLAMA_HOST=$${OLLAMA_HOST:-127.0.0.1:11435} ollama pull gemma4:12b
	OLLAMA_HOST=$${OLLAMA_HOST:-127.0.0.1:11435} ollama pull nomic-embed-text

web-install:
	cd apps/web && npm install

web:
	cd apps/web && npm run dev

voice-models:
	bash scripts/voice/download_piper_voice.sh
