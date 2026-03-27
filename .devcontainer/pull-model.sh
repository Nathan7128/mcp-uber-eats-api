#!/bin/sh
set -e

MODEL=${OLLAMA_MODEL:-llama3.2}

echo "Attente du service Ollama..."
until curl -s http://ollama:11434/ > /dev/null 2>&1; do
  sleep 1
done

echo "Téléchargement du modèle : $MODEL"

curl -N -s http://ollama:11434/api/pull \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$MODEL\"}" | \
python3 -c "
import sys, json

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
        status = d.get('status', '')
        total = d.get('total', 0)
        completed = d.get('completed', 0)
        if total:
            pct = int(completed / total * 100)
            bar = '#' * (pct // 5) + '-' * (20 - pct // 5)
            print(f'\r  {status}: [{bar}] {pct}%   ', end='', flush=True)
        else:
            print(f'\r  {status:<50}', end='', flush=True)
    except Exception:
        pass

print()
"

echo "Modèle $MODEL prêt."
