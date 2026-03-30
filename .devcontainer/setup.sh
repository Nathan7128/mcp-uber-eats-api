#!/bin/bash
# .devcontainer/setup.sh
# Script de configuration initiale du devcontainer.
# Appelé une seule fois via postCreateCommand.

set -e

WORKSPACE="/workspace"
cd "$WORKSPACE"

echo ""
echo "==================================================="
echo "   Setup : mcp-uber-eats-api devcontainer"
echo "==================================================="

# ── 1. uv ─────────────────────────────────────────────
echo ""
echo "[1/4] Verification de uv..."
if ! command -v uv &> /dev/null; then
    pip install uv --quiet
    echo "  OK  uv installe"
else
    echo "  OK  uv present ($(uv --version))"
fi

# ── 2. Dependances Python ──────────────────────────────
echo ""
echo "[2/4] Installation des dependances Python..."
uv sync
echo "  OK  dependances installees"

# ── 3. Fichier .env ────────────────────────────────────
echo ""
echo "[3/4] Verification du fichier .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Dans le devcontainer, Ollama est accessible via le service Docker "ollama"
    sed -i 's|OLLAMA_API_BASE=.*|OLLAMA_API_BASE="http://ollama:11434"|' .env
    echo "  OK  .env cree depuis .env.example"
    echo "  /!\\ Renseignez vos credentials Uber Eats dans .env pour utiliser l'API reelle."
else
    echo "  OK  .env deja present"
fi

# Verification des variables d'environnement
echo ""
echo "      Etat des variables d'environnement :"

check_var() {
    local name=$1
    local placeholder=$2
    local value
    value=$(grep "^${name}=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [ -z "$value" ]; then
        printf "      %-35s [MANQUANTE]\n" "$name"
    elif [ "$value" = "$placeholder" ]; then
        printf "      %-35s [placeholder - a renseigner]\n" "$name"
    else
        printf "      %-35s [OK]\n" "$name"
    fi
}

echo "      -- LLM --"
check_var "LLM_MODEL"          ""
check_var "OLLAMA_MODEL"       ""
check_var "OLLAMA_API_BASE"    ""
echo "      -- Uber Eats (optionnels en mode mock) --"
check_var "UBER_EATS_API_TOKEN"      "YOUR_UBER_EATS_API_TOKEN"
check_var "UBER_EATS_CLIENT_ID"      "YOUR_UBER_EATS_CLIENT_ID"
check_var "UBER_EATS_CLIENT_SECRET"  "YOUR_UBER_EATS_CLIENT_SECRET"

# ── 4. Modele Ollama ───────────────────────────────────
echo ""
echo "[4/4] Telechargement du modele Ollama..."
bash .devcontainer/pull-model.sh

# ── Fin ────────────────────────────────────────────────
echo ""
echo "==================================================="
echo "   Setup termine !"
echo "   Lancez : bash start.sh"
echo "==================================================="
echo ""
