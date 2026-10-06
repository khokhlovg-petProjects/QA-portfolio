"""HTTP client for the DummyJSON API.

Every method returns the raw `requests.Response` rather than a parsed model.
A test client that unwrapped responses would leave the status code and headers
unreachable, and those are exactly what the negative tests assert on; parsing
is left to the caller, which knows whether it is expecting a product or an
error.

Each call is attached to the Allure report as it happens, so a failure in CI
can be read without reproducing it locally.
"""

from __future__ import annotations

import json
from types import TracebackType
from typing import Any, Self

import allure
import requests

from api.models import LoginResponse
from settings import settings


class DummyJsonClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout or settings.http_timeout
        self.session = requests.Session()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.session.close()

    # --- authentication -------------------------------------------------

    def login(self, username: str, password: str) -> requests.Response:
        """Attempt a sign-in. Does not touch the session's auth header."""
        return self._request(
            "POST",
            "/auth/login",
            json={"username": username, "password": password},
        )

    def authorize(self, username: str, password: str) -> LoginResponse:
        """Sign in and keep the bearer token for every later call."""
        response = self.login(username, password)
        response.raise_for_status()
        session_user = LoginResponse.model_validate(response.json())
        self.session.headers["Authorization"] = f"Bearer {session_user.access_token}"
        return session_user

    def me(self) -> requests.Response:
        return self._request("GET", "/auth/me")

    # --- products -------------------------------------------------------

    def get_product(self, product_id: int) -> requests.Response:
        return self._request("GET", f"/products/{product_id}")

    def list_products(self, limit: int | None = None, skip: int | None = None) -> requests.Response:
        params = {k: v for k, v in {"limit": limit, "skip": skip}.items() if v is not None}
        return self._request("GET", "/products", params=params)

    def search_products(self, query: str) -> requests.Response:
        return self._request("GET", "/products/search", params={"q": query})

    def add_product(self, **fields: Any) -> requests.Response:
        return self._request("POST", "/products/add", json=fields)

    def update_product(self, product_id: int, **fields: Any) -> requests.Response:
        return self._request("PUT", f"/products/{product_id}", json=fields)

    def delete_product(self, product_id: int) -> requests.Response:
        return self._request("DELETE", f"/products/{product_id}")

    # --- plumbing -------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        self._attach(method, url, kwargs, response)
        return response

    @staticmethod
    def _attach(
        method: str,
        url: str,
        request_kwargs: dict[str, Any],
        response: requests.Response,
    ) -> None:
        body = request_kwargs.get("json")
        params = request_kwargs.get("params")

        lines = [f"{method} {url}"]
        if params:
            lines.append(f"query: {params}")
        if body is not None:
            lines.append(f"request body:\n{json.dumps(body, indent=2, ensure_ascii=False)}")
        lines.append(f"\n-> {response.status_code} in {response.elapsed.total_seconds():.3f}s")
        lines.append(f"response body:\n{_pretty(response)}")

        allure.attach(
            "\n".join(lines),
            name=f"{method} {path_of(url)} -> {response.status_code}",
            attachment_type=allure.attachment_type.TEXT,
        )


def path_of(url: str) -> str:
    """The path part of a URL, for a readable Allure attachment name."""
    _, _, remainder = url.partition("://")
    _, slash, path = remainder.partition("/")
    return f"{slash}{path}"


def _pretty(response: requests.Response) -> str:
    try:
        return json.dumps(response.json(), indent=2, ensure_ascii=False)[:4000]
    except ValueError:
        return response.text[:4000]
