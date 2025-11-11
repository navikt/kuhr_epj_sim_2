import os
import httpx
from typing import Any, Dict, Optional

async def fetch_jwk(maskinporten_token: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:

    print(type(maskinporten_token))
    print(maskinporten_token)

    # Base headers, allowing optional overrides
    default_headers = {"Authorization": f"Bearer {maskinporten_token}"}
    if headers:
        default_headers.update(headers)

    # Append token as a query param
    params = {"token": maskinporten_token}

    url = os.getenv("KUHR_JWK_API_URL")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=default_headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
