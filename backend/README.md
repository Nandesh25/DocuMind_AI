# DocuMind AI — Backend

Enterprise Document Intelligence Platform API built with **FastAPI** following
**Clean Architecture**, the **Repository Pattern**, and a **Service Layer**.

## Stack
- FastAPI · async SQLAlchemy 2.0 · asyncpg · Alembic · PostgreSQL
- JWT auth (python-jose) · passlib[bcrypt]
- RAG: LangChain · Ollama (LLM) · ChromaDB (vectors) · all-MiniLM-L6-v2 embeddings

## Architecture (dependency rule points inward)
```
api/routers  ->  services  ->  repositories (interfaces + impl)  ->  models
                    |                                   \-> database
                    \-> rag / ai adapters (ollama, chroma, embeddings)
core (security, deps, exceptions) · config · utils
```

## Local Setup
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # then edit secrets

# Start Postgres + Ollama (or use docker compose)
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

## Docker
Run the **full stack** (Angular + FastAPI + PostgreSQL + ChromaDB + Ollama) from
the repository root:
```bash
docker compose up --build
# Pull the chat model into the Ollama container (Qwen by default; Gemma also works)
docker compose exec ollama ollama pull qwen2.5:3b
```
- Frontend: http://localhost:8080
- API docs: http://localhost:8000/docs
- ChromaDB: http://localhost:8001

Tables are auto-created on first boot (`AUTO_CREATE_TABLES=true`). For production,
disable that and use Alembic:
```bash
docker compose exec api alembic upgrade head
```

To run just the backend services (Postgres + ChromaDB + Ollama + API):
```bash
cd backend && docker compose up --build
```

## Layout
| Path | Responsibility |
|------|----------------|
| `app/api/routers` | HTTP endpoints (presentation) |
| `app/services` | Use cases / business rules |
| `app/repositories` | Data access (interfaces + implementations) |
| `app/models` | SQLAlchemy ORM entities |
| `app/schemas` | Pydantic request/response DTOs |
| `app/ai` | Ollama, ChromaDB, embedding adapters |
| `app/rag` | Loaders, chunker, retriever, prompts, pipeline |
| `app/core` | Security, DI, exceptions, constants |
| `app/config` | Settings |
| `app/utils` | Pure helpers |
