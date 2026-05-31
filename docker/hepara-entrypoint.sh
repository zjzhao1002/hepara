#!/bin/sh
set -eu

DATA_DIR=/app/data
CITATION_RECORD=/app/hepara/subagents/inspirehep_agent/citations_record.json

mkdir -p "$DATA_DIR/pdf" /root/.ollama
touch "$DATA_DIR/.env"

ln -sf "$DATA_DIR/.env" /app/.env
rm -f "$CITATION_RECORD"
ln -s "$DATA_DIR/citations_record.json" "$CITATION_RECORD"

ollama serve &
OLLAMA_PID=$!

for _ in $(seq 1 60); do
    if ollama list >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if ! ollama show "${OLLAMA_MODEL}" >/dev/null 2>&1; then
    ollama pull "${OLLAMA_MODEL}"
fi

trap 'kill "$OLLAMA_PID" 2>/dev/null || true' INT TERM EXIT

exec uv run streamlit run streamlit_app_local.py
