#!/usr/bin/env bash
# DocuMind AI — setup helper (macOS/Linux)
# Usage: ./setup.sh
set -euo pipefail

echo "== DocuMind AI setup =="

[ -f .env ] || { cp .env.example .env; echo "Created root .env"; }
[ -f backend/.env ] || { cp backend/.env.example backend/.env; echo "Created backend/.env"; }

echo
echo "Environment files ready."
echo "IMPORTANT: edit SECRET_KEY in .env before any real deployment."
echo
echo "Next steps:"
echo "  1. docker compose up -d --build"
echo "  2. docker compose exec ollama ollama pull qwen2.5:3b"
echo "  3. Open http://localhost:8080"
