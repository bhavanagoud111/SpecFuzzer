"""FastAPI server powering SpecFuzzer."""
from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .executor import TestExecutor
from .llm import generate_tests
from .parser import SpecParseError, parse_openapi_document
from .validator import summarize_results

app = FastAPI(title="SpecFuzzer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_base_url(explicit: Optional[str]) -> Optional[str]:
    # settings reads .env; os.getenv covers variables exported in the shell.
    return explicit or settings.target_base_url or os.getenv("TARGET_BASE_URL")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


async def _process_upload(file: UploadFile, base_url: Optional[str]) -> dict:
    raw_bytes = await file.read()
    try:
        endpoints = parse_openapi_document(raw_bytes)
    except SpecParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    test_cases = generate_tests(endpoints)
    executor = TestExecutor(base_url=_resolve_base_url(base_url))
    execution_results = executor.execute_suite(test_cases)
    report = summarize_results(execution_results)
    return report


@app.post("/upload_spec")
async def upload_spec(
    file: UploadFile = File(...),
    base_url: Optional[str] = Form(default=None),
) -> dict:
    """Accept an OpenAPI document, fuzz endpoints, and return findings."""

    return await _process_upload(file, base_url)


@app.post("/upload")
async def upload_spec_legacy(
    file: UploadFile = File(...),
    base_url: Optional[str] = Form(default=None),
) -> dict:
    """Backward-compatible endpoint."""

    return await _process_upload(file, base_url)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
