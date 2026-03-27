import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIMEOUT = 30  # seconds


class UberEatsAPIError(Exception):
    def __init__(self, status_code: int, code: str, message: str, metadata: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.metadata = metadata or {}
        super().__init__(f"[{status_code}] {code}: {message}")


class UberEatsClient:
    """Base HTTP client for the Uber Eats API.

    Handles authentication, session management, and error parsing.
    All methods return the parsed JSON response as a dict.

    Usage:
        client = UberEatsClient()
        stores = client.get("/v1/delivery/stores")
        order  = client.get("/v1/delivery/order/order-xyz")
    """

    def __init__(self, token: str | None = None, base_url: str | None = None):
        self._token = token or os.getenv("UBER_EATS_API_TOKEN")
        self._base_url = (base_url or os.getenv("UBER_EATS_API_CALLS_DOMAIN", "https://api.uber.com")).rstrip("/")

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        })

    # ------------------------------------------------------------------
    # Low-level request helpers
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        url = f"{self._base_url}{path}"
        response = self._session.request(method, url, **kwargs)
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return
        try:
            body = response.json()
        except ValueError:
            body = {}
        raise UberEatsAPIError(
            status_code=response.status_code,
            code=body.get("code", "unknown_error"),
            message=body.get("message", response.text),
            metadata=body.get("metadata", {}),
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._request("GET", path, params=params)
        if response.status_code == 204:
            return {}
        return response.json()

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._request("POST", path, json=json or {})
        if response.status_code == 204:
            return {}
        return response.json()

    def delete(self, path: str) -> dict[str, Any]:
        response = self._request("DELETE", path)
        if response.status_code == 204:
            return {}
        return response.json()
