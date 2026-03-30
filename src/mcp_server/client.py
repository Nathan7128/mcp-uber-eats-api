"""Client HTTP pour l'API Uber Eats.

Fournit `UberEatsClient` (requêtes authentifiées) et `UberEatsAPIError`
(exception structurée pour tout statut HTTP non-2xx).
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class UberEatsAPIError(Exception):
    """Exception levée pour tout statut HTTP non-2xx retourné par l'API Uber Eats."""

    def __init__(self, status_code: int, code: str, message: str, metadata: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.metadata = metadata or {}
        super().__init__(f"[{status_code}] {code}: {message}")


class UberEatsClient:
    """Client HTTP avec session persistante et authentification Bearer automatique."""

    def __init__(self, token: str | None = None, base_url: str | None = None):
        self._token = token or os.getenv("UBER_EATS_API_TOKEN")
        self._base_url = (base_url or os.getenv("UBER_EATS_API_CALLS_DOMAIN", "https://api.uber.com")).rstrip("/")

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self._base_url}{path}"
        response = self._session.request(method, url, **kwargs)
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return
        # Tente de parser le corps JSON pour extraire code/message structurés ;
        # repli sur un dict vide si le corps n'est pas du JSON valide.
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

    def get(self, path: str, params: dict | None = None) -> dict:
        response = self._request("GET", path, params=params)
        if response.status_code == 204:
            return {}
        return response.json()

    def post(self, path: str, json: dict | None = None) -> dict:
        response = self._request("POST", path, json=json or {})
        if response.status_code == 204:
            return {}
        return response.json()

    def delete(self, path: str) -> dict:
        response = self._request("DELETE", path)
        if response.status_code == 204:
            return {}
        return response.json()
