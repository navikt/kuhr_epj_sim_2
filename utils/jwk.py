import os
import httpx
from typing import Any, Dict, Optional

async def fetch_jwk(maskinporten_token: str) -> Dict[str, Any]:

    url = os.getenv("KUHR_JWK_API_URL")

    # Base headers, allowing optional overrides
    default_headers = {"Authorization": f"Bearer {maskinporten_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=default_headers
        )
        response.raise_for_status()
        return response.json()
