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
from fastapi import BackgroundTasks
from cfg import debug
from utils.slackbot import SlackBot

router = APIRouter(prefix="/innsending", tags=["innsending"])

@router.post("/send")
async def send_innsending(data: dict, request: Request, response: Response, background_tasks: BackgroundTasks):

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
    # EPJ_SIM           8080
    # Maskinporten Mock 8082
    # kuhr-jwk          8089
    # Kuhr-krav-api     8090
    # Hent token med scope nav:kuhr/krav

    iterations = int(data['amount'])

    for i in range(iterations):

        if os.getenv("MILJO") == "LOCAL":
            maskinporten_token = await hent_maskinporten_token_mock()
        else:
            maskinporten_token = await get_maskinporten_token_nais()

        # Get kuhr JWK
        jwk_info = await fetch_jwk(maskinporten_token)

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
        khur_krav_api = os.getenv("KUHR_KRAV_API_URL") + "/v1/process/sendinnbehandlerkravmelding"

        headers = {
            "Authorization": f"Bearer {maskinporten_token}",
            "Content-Type": "application/jose"
        }

        async with httpx.AsyncClient() as client:
            kuhr_response = await client.post(khur_krav_api, content=compact_jwe, headers=headers)

            response_json = kuhr_response.json()

            # fields for background task
            request_status_code = kuhr_response.status_code
            bkmId = response_json.get("behandlerkravmeldingId")
            bkmStatus = response_json.get("status")

            background_tasks.add_task(sjekk_innsending_status, request, bkmId, bkmStatus, request_status_code)


async def sjekk_innsending_status(request: Request, bkmId: str, bkmStatus: str, request_status_code: int):

    await asyncio.sleep(10)

    try:
        if os.getenv("MILJO") == "LOCAL":
            maskinporten_token = await hent_maskinporten_token_mock()
        else:
            maskinporten_token = await get_maskinporten_token_nais()

        if not maskinporten_token:
            request.app.state.keep_running = False
            bot = SlackBot()
            bot.send_message(f"""
            Failed to obtain maskinporten token for in kuhr_epj_sim_2.
            Stopping periodic task for now, pod needs to be redeployed.
            """)
            bot.close()

        url = os.getenv("KUHR_KRAV_API_URL") + "/v1/data/behandlerkravmelding/" + bkmId

        headers = {
            "Authorization": f"Bearer {maskinporten_token}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            meldingsstatus = data.get("meldingsstatus")
            kontrollstatus = data.get("kontrollstatus")
            utbetalingsstatus = data.get("utbetalingsstatus")

            if meldingsstatus == "feil_i_melding":
                bot = SlackBot()
                bot.send_message(f"""
                feil_i_melding detected for bkm_id: {bkmId} in kuhr_epj_sim_2 during status check.
                """)
                bot.close()

            if debug:
                print(f"--- Status Check for BKM ID: {bkmId} ---")
                print(f"Meldingsstatus:  {meldingsstatus}")
                print(f"Kontrollstatus:  {kontrollstatus}")
                print(f"Utbetalingsstatus: {utbetalingsstatus}")
                print(f"Status: {bkmStatus}")
                print("----------------------------------------")

    # HTTP exception
    except httpx.HTTPStatusError as e:
        request.app.state.keep_running = False
        bot = SlackBot()
        bot.send_message(f"""
        HTTP error during status check for bkm_id: {bkmId} in kuhr_epj_sim_2.
        Exception details: {e}
        Stopping periodic task for now, pod needs to be redeployed.
        """)
        bot.close()

    # Generell exception
    except Exception as e:
        print(f"Unexpected error during status check for {bkmId}: {e}")
        request.app.state.keep_running = False
        bot = SlackBot()
        bot.send_message(f"""
        An exception has occured for bkm_id: {bkmId} in kuhr_epj_sim_2 during status check.
        Exception details: {e}
        Stopping periodic task for now, pod needs to be redeployed.
        """)
        bot.close()
