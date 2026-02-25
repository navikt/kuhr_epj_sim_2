import asyncio
import base64
import hashlib
import httpx
import time
import uuid
import json
import os

from dotenv import load_dotenv
from jwcrypto import jwk, jwt

# Generate or load a persistent key for DPoP
# In a real app, store this securely; for TTT, we can generate it on startup
DPOP_KEY = jwk.JWK.generate(kty='RSA', size=2048)

async def get_helseid_token_ttt():
    url = "https://helseid-ttt.test.nhn.no/v2/create-test-token-with-key"
    api_key = os.getenv("HELSE_ID_KEY")

    headers = {
        "X-Auth-Key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "audience": "hdir:kuhr",
        "withoutDefaultClientClaims": True,
        "withoutDefaultUserClaims": True,
        "userClaimsParameters": {
            "securityLevel": "4",
            "pid": "01017012345"
        },
        "clientClaimsParameters": {
            "clientId": "eeb808a2-6e6f-42ae-849a-505432cf128f",
            "scope": [
                "openid",
                "profile",
                "hdir:kuhr-krav-api/krav"
            ],
            "jti": str(uuid.uuid4())
        },
        "createDPoPTokenWithDPoPProof": True,
        "dPoPProofParameters": {
            "htmClaimValue": "POST",
            "htuClaimValue": "https://my.backend.api.no"
        }
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["successResponse"]["accessTokenJwt"]

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def generate_dpop_proof(method: str, url: str, access_token: str) -> str:
    """Generates the signed DPoP header required by your Java backend."""

    # Compute ath = base64url( SHA256(access_token) )
    access_token_hash = hashlib.sha256(access_token.encode("ascii")).digest()
    ath = _base64url_encode(access_token_hash)

    header = {
        "typ": "dpop+jwt",
        "alg": "RS256",
        "jwk": json.loads(DPOP_KEY.export_public())
    }

    payload = {
        "jti": str(uuid.uuid4()),  # Unique ID for this specific request
        "htm": method.upper(),  # HTTP Method (e.g., POST)
        "htu": url,
        "iat": int(time.time()),  # Issued at
        "ath": ath
    }

    token = jwt.JWT(header=header, claims=payload)
    token.make_signed_token(DPOP_KEY)
    return token.serialize()


async def main():
    load_dotenv()
    print("Fetching token from HelseID TTT...")
    token = await get_helseid_token_ttt()
    print(token)


if __name__ == "__main__":
    asyncio.run(main())
