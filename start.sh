#!/bin/bash
# start.sh
# Lance l'application : verifie l'environnement puis demarre main.py.

set -e

# ── .env ───────────────────────────────────────────────
if [ ! -f .env ]; then
    echo "Erreur : fichier .env introuvable."
    echo "Copiez .env.example en .env et renseignez vos variables."
    exit 1
fi

# ── uv ─────────────────────────────────────────────────
if ! command -v uv &> /dev/null; then
    echo "uv introuvable. Installation..."
    pip install uv --quiet
fi

# ── Dependances ────────────────────────────────────────
if [ ! -d .venv ]; then
    echo "Environnement virtuel absent. Installation des dependances..."
    uv sync
fi

# ── Lancement ──────────────────────────────────────────
exec uv run python main.py
