#!/usr/bin/env bash
# Bring up the ROM stack and make sure Rom's models are present.
#   ./scripts/03-start.sh
set -euo pipefail
cd "$(dirname "$0")/.."

[[ -f .env ]] || { cp .env.example .env; echo "==> Created .env from template (edit to taste)."; }
set -a; source .env; set +a
ROM_MODEL="${ROM_MODEL:-llama3.1:8b}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"

echo "==> Building and starting containers"
docker compose up -d --build

echo "==> Waiting for Ollama to be ready"
for i in $(seq 1 30); do
    if docker compose exec -T ollama ollama list >/dev/null 2>&1; then break; fi
    sleep 2
done

pull_model() {  # pull only if missing
    local m="$1"
    if docker compose exec -T ollama ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$m"; then
        echo "    model '$m' already present"
    else
        echo "==> Pulling model '$m' (needs internet; one time)"
        docker compose exec -T ollama ollama pull "$m"
    fi
}
pull_model "$ROM_MODEL"
pull_model "$EMBED_MODEL"

echo
echo "==> Stack is up."
docker compose ps
echo
echo "    Rom UI:   http://localhost:${ROM_PORT:-8080}"
echo "    Library:  http://localhost:${KIWIX_PORT:-8090}"
echo "    Health:   curl -s http://localhost:${ROM_PORT:-8080}/health | jq"
echo
echo "==> If you've added/updated content, index it now:"
echo "    docker compose exec rom python ingest.py"
