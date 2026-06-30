# lawdz — Algerian Law Chatbot

Ask about your legal problem in French or Arabic. Get grounded answers based on Algerian law (Journal Officiel / Codes).

**⚠️ IMPORTANT DISCLAIMER**  
This tool provides **informational** answers only, based on publicly available Algerian legislation.  
**It is not legal advice.** It is not a substitute for consulting a qualified lawyer or official authorities.  
Laws change; always verify with primary sources and professionals. Use at your own risk.

## What it does (MVP)

- Retrieves relevant excerpts from official Algerian codes and laws.
- Generates answers with precise citations (article numbers + source links).
- Supports queries in French and Arabic.
- Runs fully via Docker + Traefik reverse proxy.

## Core Tech

- **Backend**: Django + Django REST Framework (DRF)
- **RAG engine**: LlamaIndex (or LangChain) over vector embeddings of the law texts
- **Embeddings**: Multilingual models (BGE-M3 or equivalent)
- **LLM**: Ollama (local) or any OpenAI-compatible provider
- **Frontend (MVP)**: Streamlit calling the Django API
- **Infrastructure**: Docker + **Traefik** (reverse proxy + routing)
- **Data source**: Official consolidated PDFs from joradp.dz (Civil Code, Family Code, Penal, etc.)

## Project Layout (key)

```
lawdz/
├── manage.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── lawdz/                 # Django project
├── chat/                  # Main Django app (DRF + RAG)
│   └── management/commands/   # ingest_laws, etc.
├── ui/streamlit_app.py
├── data/raw/              # PDFs
└── data/processed/        # vector index (volume)
```

## Quick Start (Docker recommended)

1. Clone the repo:
   ```bash
   git clone <your-github-repo-url>
   cd lawdz
   ```

2. Copy env:
   ```bash
   cp .env.example .env
   # Edit .env with any API keys (optional if using local Ollama)
   ```

3. Start everything:
   ```bash
   docker compose up --build
   ```

4. Traefik will route:
   - Django API: http://localhost/api/chat/  (or configured host)
   - (Optional) Streamlit: http://localhost (or separate label)

   Or for local dev without Traefik first:
   ```bash
   docker compose up django --build
   ```

5. Ingest core laws (inside container or via management command):
   ```bash
   docker compose exec web python manage.py ingest_laws --codes civil,family
   ```

6. Test the API (example):
   ```bash
   curl -X POST http://localhost/api/chat/ \
     -H "Content-Type: application/json" \
     -d '{"query": "Quelles sont les conditions du divorce selon le code de la famille ?"}'
   ```

## Development (without Docker first)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then run the Streamlit UI separately pointing at the Django API.

## Adding Laws / Updating

- Place new/updated PDFs in `data/raw/`.
- Run `python manage.py ingest_laws --codes <code-names>`.
- Rebuild the index (the command handles it).

See `docs/SOURCES.md` for tracked versions.

## Evaluation & Quality

We maintain a golden set of queries in `evaluation/golden_questions.json`.
Run:
```bash
python scripts/evaluate.py
```

## Roadmap (high level)

- Phase 0: GitHub + Django skeleton + Docker + Traefik
- Phase 1: PDF ingestion pipeline + vector store
- Phase 2: RAG + DRF /chat endpoint with citations
- Phase 3: Streamlit UI + full docker experience
- Phase 4: Evaluation, guardrails, bilingual polish
- Later: GraphRAG, admin UI, better history, production deployment

## References

- Official Journal: https://www.joradp.dz/
- Similar prior work: Moustachar (RAG Algerian law)

Contributions welcome (with strong emphasis on accuracy and source fidelity).
