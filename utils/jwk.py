import os
import httpx
from typing import Any, Dict
from utils.helseid import generate_dpop_proof

async def fetch_jwk(auth_header: str, is_helseid: bool, token: str) -> Dict[str, Any]:

    url = str(os.getenv("KUHR_KRAV_API_URL")) + "/maskinporten/v1/jwk"
    headers = {"Authorization": auth_header}

    if is_helseid:
        url = str(os.getenv("KUHR_KRAV_API_URL")) + "/helseid/v1/jwk"
        dpop_url = "https://api-preprod.helserefusjon.no/kuhr/krav/v1/jwk"
        headers["DPoP"] = generate_dpop_proof("GET", dpop_url, token)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
