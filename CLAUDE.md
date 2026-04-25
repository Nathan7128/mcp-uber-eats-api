# CLAUDE.md — poc-mcp

Parle moi toujours en français

## Contexte du projet

Projet : Combinaison d'un serveur MCP exposant des outils connectés à l'API Uber Eats Marketplace avec une boucle Agentic LiteLLM utilisant ces outils tout en répondant aux prompts d'un utilisateur.  
Implémentation de la boucle conversationnelle dans le fichier main.py.  
Personne visés: restaurateurs, commerçants ayant un restaurant (et son API key) sur Uber Eats.
Possibilité de tester le chatbot en utilisant le système de Mock et des données synthétiques
implémentés dans le package `src/mcp_server/mocks/`.


**Environnement :**
- Python 3.12+
- Dépendances : `fastmcp>=3.1.0`, `requests>=2.32.5`, `pydantic>=2.0.0`, `python-dotenv>=1.0.0`, `litellm>=1.82.6`, `mcp>=1.0.0`
- Gestionnaire de packages : `uv` (fichier `uv.lock` présent)
- Binaire uv installé dans `~/.local/bin/uv` (à ajouter au PATH si absent)

**Démarrage du serveur MCP :**
```bash
uv run python -m mcp_server.server              # transport stdio (production, API réelle)
uv run python -m mcp_server.server --mock       # transport stdio avec données synthétiques
uv run fastmcp dev mcp_server/tools.py          # interface de debug FastMCP
```
Utilisation déconseillé, tout passe par le main.py.

**Variables d'environnement** (fichier `.env`) :
- `LLM_MODEL` - Modèle utilisé par LiteLLM (défault : "groq/llama-3.3-70b-versatile")
- `GROQ_API_KEY` - API Key pour utiliser le modèle spécifier (à adapter en fonction du LLM)
- `UBER_EATS_API_CALLS_DOMAIN` — base URL de l'API (sandbox : `https://test-api.uber.com`, prod : `https://api.uber.com`)
- `UBER_EATS_API_TOKEN` — bearer token actif
- `UBER_EATS_CLIENT_ID` / `UBER_EATS_CLIENT_SECRET` — credentials OAuth
- `UBER_EATS_AUTHENT_DOMAIN` — domaine d'authentification OAuth

---

## Structure du projet

Code source dans le dossier `src/` à la racine du projet.

### Serveur MCP

Le code se trouve dans le package `mcp_server/`

- `models/` : Modèles de données exposés par l'API Uber Eats : commandes, restaurants, promotions, etc.
- `client.py` : Client HTTP pour l'API Uber Eats.
- `mocks/` : Fake service implémentant des données synthétiques dans le fichier `fixtures.py`, des fake routes et un Mock client qui simule le comportement du client connecté à l'API d'un vrai restaurant dans le fichier `mock_client.py`.
- `tools.py` : Outliers MCP intégrés au serveur. Détecte que client utilisé (Mock ou non) en fonction de la variable d'environnement "USE_MOCK" définies dans le `main.py` ou dans le `server.py` si ce dernier est lancé directement.
- Définition et lancement du serveur mcp avec une importation différents du mcp défini dans `tools.py` après avoir set la variable d'environnement "USE_MOCK"

### Boucle Agentic Litellm

Le code se trouve dans le package `llm/`

Définition d'une boucle qui connecte le LLM au serveur MCP et qui tourne dans que le LLM souhaite utilisé et récupérer les données des outils, en se basant sur le prompt de l'utilisateur.

### Orchestration du projet

Tout est dans le main, mise en place d'une boucle conversationnelle entre l'utilisateur et le LLM.