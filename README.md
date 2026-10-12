# SpecFuzzer

Team project built by Rohith Belede and Bhavana Ediga ([@bhavanagoud111](https://github.com/bhavanagoud111)).

LLM-powered adversarial API test generator. Upload an OpenAPI spec, auto-generate three adversarial test cases per endpoint, execute them against a target API, and review findings in a dashboard.

## Project Layout

```
backend/     # FastAPI server (upload -> parse -> generate -> execute -> validate)
frontend/    # React/Vite dashboard
run_backend.sh
```

## Backend Setup

Run these from the repository root:

```bash
# 1. Create + activate the virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Copy env template and set LLM credentials + base URL
cp .env.example .env
# edit .env to set LLM_API_BASE, LLM_API_KEY, LLM_MODEL, TARGET_BASE_URL

# 4. (Optional) Smoke test the remote LLM gateway
python -m backend.dev_llm_smoke_test

# 5. Run the FastAPI server
uvicorn backend.main:app --reload --port 8000
```

Or run `./run_backend.sh` from the repository root, which creates the virtual environment, installs dependencies, runs the smoke test (a failure only prints a warning), and starts the server on port 8000.

The backend is imported as the `backend` package, so start `uvicorn backend.main:app` from the repository root, not from inside `backend/`.

Environment variables (set these in `.env` at the repository root):

- `LLM_PROVIDER` – currently only `remote` is supported.
- `LLM_API_BASE` – base URL of an OpenAI-compatible endpoint, without `/v1` (the backend calls `<LLM_API_BASE>/v1/chat/completions`).
- `LLM_API_KEY` – bearer token for that endpoint.
- `LLM_MODEL` – model identifier understood by that endpoint.
- `TARGET_BASE_URL` – default API host for executing the generated tests. Without it (and without a `base_url` form field on upload), tests are generated but reported as skipped.

LLM calls go through a provider-agnostic HTTP gateway (see `backend/llm_remote.py` and `backend/llm_client.py`), so you can switch endpoints by editing `.env`. If the LLM call fails or is not configured, the backend falls back to built-in heuristic tests (oversized payload, SQL injection, type confusion) so the workflow keeps running.

The upload endpoint is `POST /upload_spec` (`POST /upload` is kept for backward compatibility).

## Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_BACKEND_URL` (for example in `frontend/.env`, see `frontend/.env.example`) to point at the FastAPI server. It defaults to `http://127.0.0.1:8000`.

Example root `.env`:

```
LLM_PROVIDER=remote
LLM_API_BASE=https://api.openai.com
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini
TARGET_BASE_URL=https://api.example.com
```

## Team

- Rohith Belede
- Bhavana Ediga ([@bhavanagoud111](https://github.com/bhavanagoud111))
