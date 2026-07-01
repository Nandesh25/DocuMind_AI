# DocuMind AI — Enterprise Document Intelligence Platform

A production-ready, fully **open-source** GenAI platform where authenticated users
upload documents, organize them into workspaces, and interact with them using
**Retrieval-Augmented Generation (RAG)** — plus AI summaries, semantic search,
document comparison, quizzes, and flashcards.

Built with Clean Architecture, SOLID principles, the Repository Pattern, and a
Service Layer across the whole stack. **100% free/open-source — no paid APIs.**

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Angular 19 (standalone components, signals, lazy loading), Angular Material, SCSS, TypeScript |
| **Backend** | FastAPI, async SQLAlchemy 2.0, Alembic, Pydantic v2, JWT auth |
| **Database** | PostgreSQL |
| **AI / RAG** | Ollama (Qwen / Gemma), LangChain, ChromaDB, all-MiniLM-L6-v2 embeddings |
| **DevOps** | Docker, Docker Compose, GitHub Actions, Nginx |

---

## Features

- 🔐 **Auth** — register, login, JWT access/refresh with rotation + revocation, logout
- 🗂️ **Workspaces** — multi-tenant, role-based (owner/editor/viewer), full CRUD + members
- 📄 **Documents** — upload PDF / DOCX / TXT / Markdown, async ingestion, metadata (pages/chunks/words)
- 🧠 **RAG chat** — streaming answers with source citations and multi-turn conversation memory
- 🔎 **Search** — semantic (vector), document keyword, and chat content search
- 📝 **Summaries** — short, detailed, and executive
- 🆚 **Comparison** — compare two documents (similarity score + structured analysis)
- ❓ **Quiz generator** — MCQ, True/False, short answer
- 🎴 **Flashcards** — flip-card study mode
- 🎨 **UX** — Material 3 theming, light/dark mode, responsive shell

---

## Architecture

```
┌─────────────┐   HTTPS/REST + SSE   ┌──────────────────────────┐
│ Angular 19  │ ───────────────────► │ FastAPI (Clean Arch)     │
│  SPA (Nginx)│                      │ routers → services →     │
└─────────────┘                      │ repositories → models    │
                                     └───────┬───────────┬──────┘
                                             │           │
                                   ┌─────────▼──┐   ┌────▼─────────┐
                                   │ PostgreSQL │   │ ChromaDB     │
                                   │ (metadata) │   │ (vectors)    │
                                   └────────────┘   └──────────────┘
                                             │
                                   ┌─────────▼───────────┐
                                   │ Ollama (Qwen/Gemma) │
                                   │ MiniLM embeddings   │
                                   └─────────────────────┘
```

Detailed docs: [backend/README.md](backend/README.md) · [frontend/README.md](frontend/README.md)

---

## Quick Start

### Option A — Docker (all services)
```bash
cp .env.example .env          # then set a strong SECRET_KEY
docker compose up -d --build
docker compose exec ollama ollama pull qwen2.5:3b   # one-time model pull
```
- App: http://localhost:8080
- API docs: http://localhost:8000/docs
- ChromaDB: http://localhost:8001

Tables are auto-created on first boot (`AUTO_CREATE_TABLES=true`).

### Option B — Native (local dev)
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # AUTO_CREATE_TABLES=true, blank CHROMA_HOST
uvicorn app.main:app --reload                        # http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm start                                            # http://localhost:4200
```
Requires local **PostgreSQL** and **Ollama** (`ollama pull qwen2.5:3b`). ChromaDB runs
embedded when `CHROMA_HOST` is blank.

### With Make
```bash
make setup     # copy .env files
make up        # docker compose up --build
make model     # pull the Ollama model
make migrate   # alembic upgrade head (production schema)
make down      # stop the stack
```

---

## Database Migrations
For production, disable `AUTO_CREATE_TABLES` and use Alembic:
```bash
cd backend
alembic upgrade head        # applies migrations/versions/0001_initial_schema.py
```

---

## Project Structure
```
DocuMind_AI/
├── backend/          # FastAPI (Clean Architecture) — see backend/README.md
├── frontend/         # Angular 19 SPA — see frontend/README.md
├── .github/workflows # CI (Angular + backend build) and Docker image publishing
├── docker-compose.yml
├── .env.example
├── Makefile
└── LICENSE (MIT)
```

---

## Deploying on Free Services
- **Frontend →** Vercel / Netlify / Cloudflare Pages
- **Backend →** Render / Railway / Fly.io / Hugging Face Spaces (Docker)
- **PostgreSQL →** Neon / Supabase
- **Vectors →** embedded ChromaDB on a persistent disk, or Chroma Cloud
- **LLM →** a free OpenAI-compatible API (Groq / OpenRouter) in place of self-hosted Ollama
- **Embeddings →** all-MiniLM-L6-v2 in-process (CPU)
- **CI/CD →** GitHub Actions + GHCR (already configured)

Everything is env-driven — no code changes required to switch providers.

---

## License
[MIT](LICENSE) — free and open-source.
