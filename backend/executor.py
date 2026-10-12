"""HTTP executor for running adversarial test cases."""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from .schemas import TestCase, TestResult, TestStatus


class TestExecutor:
    def __init__(self, base_url: Optional[str], timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout

    def execute_suite(self, cases: List[TestCase]) -> List[TestResult]:
        return [self.execute_case(case) for case in cases]

    def execute_case(self, case: TestCase) -> TestResult:
        if not self.base_url:
            return TestResult(
                case=case,
                status=TestStatus.skipped,
                error="No base URL configured for execution",
            )

        path = _fill_path_params(case.path, case.payload)
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        start = time.perf_counter()
        try:
            response = requests.request(
                method=case.method,
                url=url,
                json=case.payload,
                timeout=self.timeout,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status = (
                TestStatus.passed
                if response.status_code == case.expected_status
                else TestStatus.failed
            )
            return TestResult(
                case=case,
                status=status,
                actual_status=response.status_code,
                response_body=self._safe_json(response),
                latency_ms=latency_ms,
            )
        except requests.RequestException as exc:  # noqa: BLE001
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return TestResult(
                case=case,
                status=TestStatus.error,
                error=str(exc),
                latency_ms=latency_ms,
            )

    @staticmethod
    def _safe_json(response: requests.Response):
        try:
            return response.json()
        except ValueError:
            return response.text


_PATH_PARAM = re.compile(r"\{([^{}/]+)\}")


def _fill_path_params(path: str, payload: Dict[str, Any]) -> str:
    """Replace OpenAPI path templates like /items/{id} with concrete values.

    Uses a scalar value from the test payload when it has a key with the
    parameter's name, otherwise a placeholder value of "1".
    """

    def _replace(match: "re.Match[str]") -> str:
        value = payload.get(match.group(1)) if isinstance(payload, dict) else None
        if value is None or isinstance(value, (dict, list)):
            value = "1"
        return quote(str(value), safe="")

    return _PATH_PARAM.sub(_replace, path)
