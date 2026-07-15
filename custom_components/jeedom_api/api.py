"""Minimal asynchronous client for Jeedom's HTTP API."""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


class JeedomApiError(Exception):
    """Base Jeedom API error."""


class JeedomAuthenticationError(JeedomApiError):
    """Authentication error."""


class JeedomApi:
    """Client using stdlib HTTP calls in Home Assistant's executor."""

    def __init__(self, hass, base_url: str, api_key: str, timeout: int = 15) -> None:
        self._hass = hass
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/core/api/jeeApi.php"

    def _request_sync(self, params: dict[str, Any]) -> Any:
        query = urlencode(
            {
                "apikey": self.api_key,
                **{key: value for key, value in params.items() if value is not None},
            }
        )
        request = Request(
            f"{self.endpoint}?{query}",
            headers={"Accept": "application/json", "User-Agent": "HomeAssistant-JeedomAPI/0.1"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except Exception as err:
            raise JeedomApiError(str(err)) from err

        stripped = raw.strip()
        if "Clé API non valide" in stripped or "API key" in stripped and "invalid" in stripped.lower():
            raise JeedomAuthenticationError(stripped)

        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            # Command execution often returns a scalar/plain value.
            return stripped

    async def async_request(self, **params: Any) -> Any:
        return await self._hass.async_add_executor_job(self._request_sync, params)

    async def async_get_full_data(self) -> list[dict[str, Any]]:
        data = await self.async_request(type="fullData")
        if not isinstance(data, list):
            raise JeedomApiError(f"Réponse fullData inattendue: {type(data).__name__}")
        return data

    async def async_execute(
        self,
        command_id: str,
        *,
        slider: int | float | None = None,
        color: str | None = None,
        message: str | None = None,
        title: str | None = None,
    ) -> Any:
        return await self.async_request(
            type="cmd",
            id=command_id,
            slider=slider,
            color=color,
            message=message,
            title=title,
        )
