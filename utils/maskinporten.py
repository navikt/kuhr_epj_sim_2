import os
import jwt
import time
import httpx
from typing import Optional


async def hent_maskinporten_token_mock():
    BASE_URL = "http://localhost:8082"
    url = f"{BASE_URL}/agent/securitymock/maskinporten/token"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
        except httpx.HTTPStatusError as e:
            print(f"Error response {e.response.status_code} while requesting {e.request.url!r}")


async def get_maskinporten_token_nais():
    token_endpoint = os.getenv("NAIS_TOKEN_ENDPOINT")

    if not token_endpoint:
        raise EnvironmentError("NAIS_TOKEN_ENDPOINT environment variable is not set.")

    payload = {
        "identity_provider": "maskinporten",
        "target": "nav:kuhr/krav"
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(token_endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")


class MaskinportenClient:

    def __init__(self, client_id: str, issuer: str, kid: str, audience: str, private_key: str, scopes: list[str]):
        self.client_id = client_id
        self.issuer = issuer
        self.kid = kid
        self.audience = audience.rstrip("/")
        self.private_key = private_key
        self.scopes = scopes

    def _create_jwt_assertion(self) -> str:

        now = int(time.time())
        payload = {
            "iss": self.issuer,
            "sub": self.client_id,
            "aud": f"{self.audience}/token",
            "scope": " ".join(self.scopes),
            "iat": now,
            "exp": now + 120
        }

        headers = {
            "kid": self.kid
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256", headers=headers)

    def get_access_token(self, timeout: float = 10.0) -> Optional[str]:
        assertion = self._create_jwt_assertion()
        token_endpoint = f"{self.audience}/token"

        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with httpx.Client(timeout=timeout) as client:
            response = client.post(token_endpoint, data=data, headers=headers)

        if response.status_code == 200:
            return response.json().get("access_token")

        else:
            print(f"Failed to obtain token ({response.status_code}): {response.text}")
            return None


if __name__ == "__main__":

    private_key = open("../private_key.pem").read()

    client = MaskinportenClient(
        client_id="310004693",
        issuer="fd421ad6-de04-4fc9-adf1-63899aa58a1a",
        kid="1ca42513-d321-4cd0-99c6-183af6e5b7a5",
        audience="https://test.maskinporten.no",
        private_key=private_key,
        scopes=["altinn:profiles.read"]
    )

    token = client.get_access_token()

    print(token)
