# 🍔 mcp-uber-eats-api

> Un chatbot agentique connecté à l'API Uber Eats Marketplace, pensé pour les restaurateurs.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-en%20cours%20de%20cuisson-orange?style=flat&logo=cookiecutter&logoColor=white)
![LiteLLM](https://img.shields.io/badge/LiteLLM-agentique-blueviolet?style=flat)
![FastMCP](https://img.shields.io/badge/FastMCP-serveur-green?style=flat)

---

> [!NOTE]
> **👨‍🍳 Ce projet est en pleine cuisson.** L'architecture est posée, le chatbot tourne — mais il reste encore de belles choses à faire. Revenez régulièrement, ça mijote !

---

## Description

Ce projet combine un **serveur MCP** exposant des outils connectés à l'[API Uber Eats Marketplace](https://developer.uber.com/docs/eats/introduction) avec une **boucle agentique [LiteLLM](https://github.com/BerriAI/litellm)**.

Concrètement : un restaurateur peut poser des questions en langage naturel sur ses commandes, son restaurant ou ses promotions. Le LLM choisit les bons outils MCP, interroge l'API, et répond.

Un système de **données synthétiques** permet de tester le tout sans avoir besoin d'un vrai compte Uber Eats.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   main.py                        │
│          Boucle conversationnelle                │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │    LiteLLM Agent      │  ←  src/llm/agent.py
        │  (boucle agentique)   │
        └───────────┬───────────┘
                    │  appels d'outils MCP
        ┌───────────▼───────────┐
        │    Serveur MCP        │  ←  src/mcp_server/
        │  (FastMCP + tools)    │
        └───────────┬───────────┘
                    │
           ┌────────┴───────────┐
           │                    │
   ┌───────▼──────┐    ┌────────▼────────┐
   │  API Uber    │    │  Mock / données │
   │  Eats réelle │    │  synthétiques   │
   └──────────────┘    └─────────────────┘
```

---

## Stack

| Composant       | Technologie                          |
|-----------------|--------------------------------------|
| Langage         | Python 3.12+                         |
| Serveur MCP     | [FastMCP](https://github.com/jlowin/fastmcp) |
| Boucle agentique| [LiteLLM](https://github.com/BerriAI/litellm) |
| LLM par défaut  | Groq · `llama-3.3-70b-versatile`     |
| Validation      | Pydantic v2                          |
| Gestion des deps| [uv](https://github.com/astral-sh/uv) |

---

## Démarrage rapide

### Prérequis

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) installé (`~/.local/bin/uv`)

### Installation

```bash
git clone https://github.com/Nathan7128/mcp-uber-eats-api.git
cd mcp-uber-eats-api
uv sync
```

### Configuration

Copie le fichier d'exemple et renseigne tes variables :

```bash
cp .env.example .env
```

### Lancement

```bash
# A exécuter à la racine du projet
uv run python main.py
```

---

## Variables d'environnement

| Variable                      | Description                                          | Exemple                        |
|-------------------------------|------------------------------------------------------|--------------------------------|
| `LLM_MODEL`                   | Modèle LiteLLM utilisé                              | `groq/llama-3.3-70b-versatile` |
| `GROQ_API_KEY`                | Clé API Groq (ou autre fournisseur LLM)             | `gsk_...`                      |
| `UBER_EATS_API_CALLS_DOMAIN`  | Base URL API Uber Eats                              | `https://api.uber.com`         |
| `UBER_EATS_API_TOKEN`         | Bearer token actif                                  | `...`                          |
| `UBER_EATS_CLIENT_ID`         | Client ID OAuth                                     | `...`                          |
| `UBER_EATS_CLIENT_SECRET`     | Client Secret OAuth                                 | `...`                          |
| `UBER_EATS_AUTHENT_DOMAIN`    | Domaine d'authentification OAuth                    | `https://auth.uber.com`        |

---

## 🗺️ Roadmap

Le projet avance à son rythme — c'est fait avec soin, pas dans la précipitation.

- [ ] **1. Documentation** — Docstrings, commentaires ciblés, et une documentation technique complète du projet
- [ ] **2. Interface utilisateur** — Une UI (Streamlit ou autre) pour rendre les échanges avec le chatbot plus agréables : sélection du modèle LLM, choix entre mock et API réelle, historique de conversation
- [ ] **3. Dev container** — Finalisation et validation de la configuration `.devcontainer/` pour un environnement de développement reproductible en un clic

---

## Notes

Ce projet est développé à titre personnel, pour le plaisir d'explorer le protocole MCP et les boucles agentiques. Pas de deadline, pas de pression — juste de la curiosité et de l'expérimentation.  
Je réalise la plupart de l'implémentation moi-même car j'apprécie beaucoup codé en Python, même si c'est moins rapide que de vibe codé avec Claude -> je lui confie ce que j'ai la flemme de faire (principalement la doc).

[Claude Code](https://claude.ai/code) a contribué à certaines parties du code (génération des données synthétiques, modèles de données), tout en laissant la main sur les décisions d'architecture et la logique métier.
