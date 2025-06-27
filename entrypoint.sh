#!/usr/bin/env sh
set -e

# 1) Pull model if missing
ollama pull qwen3:8b

# 2) Wait for Ollama HTTP API readiness
until curl --silent http://ollama:11434/v1/models | grep -q '"qwen3:8b"'; do
  echo "Waiting for Ollama server…"
  sleep 2
done

# 3) Launch the bot
exec python -m app.main
