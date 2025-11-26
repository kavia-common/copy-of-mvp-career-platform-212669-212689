from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from src.core.config import get_settings


# PUBLIC_INTERFACE
async def suggest_role_adjacency(current_role_id: str, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Call the Node.js Role Mapping Service to retrieve role adjacency suggestions.

    Args:
        current_role_id: The current role identifier.
        top_n: Optional integer to limit the number of suggestions.

    Returns:
        List of suggestion dicts: [{ "targetRoleId": str, "weight": float, "rationale": str | None }, ...]

    Raises:
        RuntimeError: When the service call fails (non-200 status) or response is invalid.
    """
    settings = get_settings()
    base_url = (settings.ROLE_MAPPER_BASE_URL or "").rstrip("/")
    if not base_url:
        raise RuntimeError("ROLE_MAPPER_BASE_URL is not configured")

    body: Dict[str, Any] = {"currentRoleId": current_role_id}
    if top_n is not None:
        body["topN"] = int(top_n)

    headers = {
        "X-Internal-Token": settings.INTERNAL_TOKEN or "",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        resp = await client.post("/adjacency/suggest", headers=headers, json=body)
        if resp.status_code != 200:
            raise RuntimeError(f"Role mapper service error: {resp.status_code} {resp.text}")

        data = resp.json()
        if not isinstance(data, dict) or "suggestions" not in data or not isinstance(data["suggestions"], list):
            raise RuntimeError("Unexpected response format from role mapper service")

        return data["suggestions"]
