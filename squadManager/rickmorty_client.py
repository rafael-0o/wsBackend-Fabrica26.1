from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class RickMortyClient:
    base_url: str = "https://rickandmortyapi.com/api"
    timeout_s: float = 10.0

    def _fetch_json(
        self, url: str, *, params: dict[str, Any] | None = None
    ) -> Any:
        response = requests.get(url, params=params, timeout=self.timeout_s)
        response.raise_for_status()
        return response.json()

    def _map_characters_by_id(
        self, upstream_payload: Any
    ) -> dict[int, dict[str, Any]]:
        """
        Normaliza o retorno da Rick and Morty API para:
        {<character_id>: <character_obj>}
        """
        if isinstance(upstream_payload, list):
            return {
                int(character_obj["id"]): character_obj
                for character_obj in upstream_payload
                if isinstance(character_obj, dict) and "id" in character_obj
            }
        if isinstance(upstream_payload, dict) and "id" in upstream_payload:
            return {int(upstream_payload["id"]): upstream_payload}
        return {}

    def get_character(self, character_id: int) -> dict[str, Any]:
        request_url = f"{self.base_url}/character/{character_id}"
        return self._fetch_json(request_url)

    def get_characters(self, character_ids: list[int]) -> dict[int, dict[str, Any]]:
        normalized_ids: list[int] = []
        for raw_id in character_ids:
            normalized_id = int(raw_id)
            if normalized_id > 0:
                normalized_ids.append(normalized_id)
        if not normalized_ids:
            return {}

        request_url = f"{self.base_url}/character/{','.join(map(str, normalized_ids))}"
        upstream_payload = self._fetch_json(request_url)
        return self._map_characters_by_id(upstream_payload)

    def search_characters(self, *, name: str | None = None, page: int | None = None) -> dict[str, Any]:
        request_url = f"{self.base_url}/character"
        query_params: dict[str, Any] = {}
        if name:
            query_params["name"] = name
        if page:
            query_params["page"] = page
        return self._fetch_json(request_url, params=query_params or None)

