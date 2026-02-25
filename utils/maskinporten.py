import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def hent_maskinporten_token_mock():

    # henter med scope nav:kuhr/krav
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


async def get_helseid_token_ttt():
    url = "https://helseid-ttt.test.nhn.no/v2/create-test-token-with-key"
    api_key = os.getenv("HELSE_ID_KEY")

    headers = {
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "audience": "nhn:kjernejournal",
        "scopes": ["hdir:kuhr-krav-api/krav"],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"❌ TTT HTTP Error {e.response.status_code}: {e.response.text}")

        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

        return None


async def main():
    token = await hent_maskinporten_token_mock()
    print(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
