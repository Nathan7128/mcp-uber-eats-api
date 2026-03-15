import os
import requests
from dotenv import load_dotenv

load_dotenv()


class UberEatsAPIError(Exception):
    def __init__(self, status_code: int, code: str, message: str, metadata: dict = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.metadata = metadata or {}
        super().__init__(f"[{status_code}] {code}: {message}")


class UberEatsClient:
    """Base HTTP client for the Uber Eats API.

    Usage:
        client = UberEatsClient()
        stores = client.stores.list()
        orders = client.orders.list(store_id="...")
    """

    def __init__(self, token: str = None, base_url: str = None):
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
        url = f"{self._base_url}{path}"
        response = self._session.request(method, url, **kwargs)
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: requests.Response):
        if response.ok:
            return
        try:
            body = response.json()
        except Exception:
            body = {}
        raise UberEatsAPIError(
            status_code=response.status_code,
            code=body.get("code", "unknown_error"),
            message=body.get("message", response.text),
            metadata=body.get("metadata", {}),
        )

    def get(self, path: str, params: dict = None) -> dict:
        response = self._request("GET", path, params=params)
        if response.status_code == 204:
            return {}
        return response.json()

    def post(self, path: str, json: dict = None) -> dict:
        response = self._request("POST", path, json=json or {})
        if response.status_code == 204:
            return {}
        return response.json()

    def delete(self, path: str) -> dict:
        response = self._request("DELETE", path)
        if response.status_code == 204:
            return {}
        return response.json()

