import httpx

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
