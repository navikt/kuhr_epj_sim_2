import os
import json
import httpx
import asyncio
from fastapi import APIRouter
from jwcrypto import jwe, jwk
from jwcrypto.common import json_encode
from starlette import status
from fastapi import Request, Response
from utils.bkm_generator import generer_bkm
from utils.jwk import fetch_jwk
from utils.maskinporten import hent_maskinporten_token_mock, get_maskinporten_token_nais

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
        1. Henter maskinporten-token [nav:kuhr/krav]
        2. Bruker den til å hente kuhr-jwk
        3. Generer syntetisk kombinasjon av pasienter/profiler/takster
        4. Krypterer payload
        4. Kaller kuhr_krav API
    """

    # PORT
    # EPJ_SIM           8000
    # Kuhr-krav-api     8080
    # kuhr-jwk          8081
    # Maskinporten Mock 8082

    # Hent token med scope nav:kuhr/krav

    iterations = int(data['amount'])

    for i in range(iterations):

        # Lokal mock
        # maskinporten_token = await hent_maskinporten_token_mock()
        # Nais
        maskinporten_token = await get_maskinporten_token_nais()

        # Get kuhr jwk
        jwk_info = await fetch_jwk(maskinporten_token)

        # TODO, ekte maskinporten endpoint returnerer annerledes

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
        jwetoken  = jwe.JWE(plaintext, json_encode(protected_header))
        jwetoken.add_recipient(rsa_key)
        compact_jwe = jwetoken.serialize(compact=True)

        # KUHR_KRAV_API
        khur_krav_api = os.getenv("KUHR_KRAV_API_URL")

        headers = {
            "Authorization": f"Bearer {maskinporten_token}",
            "Content-Type": "application/jose"
        }

        async with httpx.AsyncClient() as client:
            kuhr_response = await client.post(khur_krav_api, content=compact_jwe, headers=headers)

            # TODO fjern
            print(kuhr_response)
            print(kuhr_response.text)

        await asyncio.sleep(1)
