# SpecFuzzer

Team project built by Rohith Belede and Bhavana Ediga ([@bhavanagoud111](https://github.com/bhavanagoud111)).

LLM-powered adversarial API test generator following the Ultrathink building style. Upload an OpenAPI spec, auto-generate three malicious test cases per endpoint, execute them, and review findings in a clean dashboard.

## Project Layout

```
/specfuzzer 2
  /backend        # FastAPI server (upload → parse → generate → execute → validate)
  /frontend       # React/Vite dashboard
/model          # Adapter notes for the fine-tuned Llama-2 LoRA
```

## Backend Setup (macOS, repo folder has a space!)

Because the repo folder is literally named `specfuzzer 2`, always wrap the path in quotes when using `cd`. You can also rename the directory to `specfuzzer-2` if you prefer to avoid quoting.

```bash
# 1. Enter the repo (note the quotes)
cd "$HOME/Desktop/specfuzzer 2"

# 2. Create + activate the virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Copy env template and set LLM credentials + base URL
cp .env.example .env
# edit .env to set LLM_API_BASE, LLM_API_KEY, LLM_MODEL, TARGET_BASE_URL

# 5. Smoke test the remote LLM gateway
python -m backend.dev_llm_smoke_test

# 6. Run the FastAPI server
uvicorn backend.main:app --reload --port 8000
```

## Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Environment variables (set these in your `.env`):

- `LLM_PROVIDER` – currently only `remote`, but leaves room for future `ollama`/`hf_lora`.
- `LLM_API_BASE` – base URL for any OpenAI compatible endpoint (OpenAI, Baseten, HF TGI, Together, etc.).
- `LLM_API_KEY` – bearer token for the remote endpoint.
- `LLM_MODEL` – model identifier understood by that endpoint.
- `TARGET_BASE_URL` – default API host for executing tests once cases are generated.

SpecFuzzer now uses a provider-agnostic HTTP gateway (see `backend/llm_remote.py` + `backend/llm_client.py`). Swap vendors by editing `.env`, not code. If the remote call fails or is skipped, the backend reverts to deterministic heuristic tests so workflows keep running.

## Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to point at the FastAPI server (defaults to `http://127.0.0.1:8000`).

Example `.env`:

```
LLM_PROVIDER=remote
LLM_API_BASE=https://api.openai.com
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini
TARGET_BASE_URL=https://api.example.com
```

## Model Adapter

See `model/adapter.md` for instructions on wiring up the QLoRA adapter emitted from Colab fine-tuning. When the adapter is absent, the backend gracefully falls back to OpenAI as required by the safety note. The primary upload endpoint is `POST /upload_spec` (with `/upload` retained for backward compatibility).

## Team

- Rohith Belede
- Bhavana Ediga ([@bhavanagoud111](https://github.com/bhavanagoud111))
