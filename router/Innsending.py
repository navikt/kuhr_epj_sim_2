import asyncio
import json
import httpx
from fastapi import APIRouter
from jwcrypto import jwe, jwk
from jwcrypto.common import json_encode
from starlette import status
from fastapi import Request, Response
from utils.bkm_generator import generer_bkm
from utils.jwk import fetch_jwks
from utils.maskinporten import hent_maskinporten_token_mock

router = APIRouter(prefix="/innsending", tags=["innsending"])

@router.post("/send")
async def send_innsending(data: dict, request: Request, response: Response):

    if "amount" not in data or not isinstance(data["amount"], int):
        return Response(
            content='{"error": "Invalid or missing amount"}',
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    """
        1. Henter maskinporten-token
        2. Bruker den til å hente kuhr-jwk
        3. Generer syntetisk kombinasjon av pasienter/profiler/takster
        4. Krypterer payload (JWE)
        4. Kaller kuhr_krav API
    """

    # Innsending
    # POST /v1/process/sendinnbehandlerkravmelding
    # Sjekk status på innsending
    # GET /v1/data/behandlerkravmelding
    # PORTS
    # EPJ_SIM           8000
    # Kuhr-krav-api     8080
    # kuhr-jwk          8081
    # Maskinporten Mock 8082

    # Hent token med scope nav:kuhr/krav

    iterations = int(data['amount'])

    for i in range(iterations):

        token = await hent_maskinporten_token_mock()

        # Get kuhr jwk
        jwk_info = await fetch_jwks('http://localhost:8081/jwk', token)

        key_data = jwk_info['keys'][0]

        rsa_key = jwk.JWK(**{
            "kty": key_data["kty"],
            "n":   key_data["n"],
            "e":   key_data["e"],
            "kid": key_data["kid"]
        })

        payload = await generer_bkm(request, response)

        protected_header = {
            "alg": "RSA-OAEP-256",
            "enc": "A256GCM",
            "kid": key_data.get("kid")
        }

        # Convert payload dict -> bytes
        plaintext = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        jwetoken = jwe.JWE(plaintext, json_encode(protected_header))
        jwetoken.add_recipient(rsa_key)
        compact_jwe = jwetoken.serialize(compact=True)

        # KUHR_KRAV_API
        url = "http://localhost:8080/v1/process/sendinnbehandlerkravmelding"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/jose"
        }

        async with httpx.AsyncClient() as client:
            kuhr_response = await client.post(url, content=compact_jwe, headers=headers)
            print(kuhr_response)
            print(kuhr_response.text)

        await asyncio.sleep(1)