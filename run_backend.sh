#!/usr/bin/env bash
set -euo pipefail

# Always work from the repo root even if script is invoked elsewhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PATH="$SCRIPT_DIR/backend/.venv"

if [[ ! -d "$VENV_PATH" ]]; then
  python3 -m venv "$VENV_PATH"
fi

# shellcheck disable=SC1090
source "$VENV_PATH/bin/activate"

pip install -r backend/requirements.txt

# The smoke test needs LLM credentials; don't let a failure stop the server
# from starting (the backend falls back to heuristic tests without an LLM).
if ! python -m backend.dev_llm_smoke_test; then
  echo "Warning: LLM smoke test failed (check LLM_* settings in .env). Starting the server anyway." >&2
fi

uvicorn backend.main:app --reload --port 8000
