import httpx
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


class MaskinportenClient:
    def __init__(self, client_id: str, issuer: str, audience: str, private_key: str, scopes: list[str]):
        """
        Initialize the Maskinporten client.

        :param client_id: Client ID registered in Maskinporten.
        :param issuer: The issuer ID (organization number or identifier).
        :param audience: Maskinporten base URL (e.g., https://maskinporten.no).
        :param private_key: PEM-encoded private RSA key.
        :param scopes: List of Maskinporten scopes to request access for.
        """
        self.client_id = client_id
        self.issuer = issuer
        self.audience = audience.rstrip("/")
        self.private_key = private_key
        self.scopes = scopes

    def _create_jwt_assertion(self) -> str:
        """Generate a signed JWT assertion for Maskinporten."""
        now = int(time.time())
        payload = {
            "iss": self.issuer,
            "sub": self.client_id,
            "aud": f"{self.audience}/token",
            "scope": " ".join(self.scopes),
            "iat": now,
            "exp": now + 120,  # expires in 2 minutes
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_access_token(self, timeout: float = 10.0) -> Optional[str]:
        """Request a Maskinporten access token using the JWT grant flow."""
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
    private_key = open("maskinporten_private_key.pem").read()

    client = MaskinportenClient(
        client_id="your-client-id",
        issuer="your-issuer-id",
        audience="https://test.maskinporten.no",
        private_key=private_key,
        scopes=["altinn:serviceowner/read"]
    )

    token = client.get_access_token()
    print("Access Token:", token)
