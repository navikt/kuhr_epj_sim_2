import httpx
from typing import Any, Dict, Optional


async def fetch_jwks(url: str, token: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:

    # Base headers, allowing optional overrides
    default_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        default_headers.update(headers)

    # Append token as a query param
    params = {"token": token}

    """
        {
            keys: [
                {
                    'kty': 'RSA',     <- key type
                    'x5t#S256': '',
                    'nbf': '',
                    'e': '',          <- modulus
                    'kid': '',
                    'x5c': [''],
                    'exp': '',
                    'n': ''           <- exponent
                }
            ]
        }
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=default_headers, params=params)
        response.raise_for_status()  # Raises an exception for 4xx/5xx
        return response.json()
