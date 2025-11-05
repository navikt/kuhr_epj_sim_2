import uuid
import random
from fastapi import Request, Response
from datetime import datetime, time, timedelta, timezone
from utils.database_kall import getPasient


# Dette er bkm for pasientreise
"""
payload = {
    "praksisId": "1004326178",  # KUHR praksis
    "behandlerkrav": {
        "regninger": [
            {
                "guid": "0b8dc559-6c2d-419b-aeef-faaf537c6117", # DONE
                "regningsnummer": "12496", # Kan være hva som helst
                "tidspunkt": "2014-05-17T11:20:00+02:00", # ISO 8601 timestamp
                "pasient": {
                    "identifikasjon": {
                        "id": "14057012345", # DONE
                        "type": "FNR"
                    }
                },
                "arsakFriEgenandel": "F",
                "belop": 435.00
            }
        ],
        "antallRegninger": 1,
        "belop": 435.00
    }
}
"""

def random_guid() -> str:
    """Generate and return a random GUID (UUID4)."""
    return str(uuid.uuid4())

def random_int_between(x: int, y: int) -> int:
    """Return a random integer between x and y inclusive."""
    return random.randint(x, y)

def random_kl_timestamp():
    # Define KL timezone (UTC+8)
    kl_tz = timezone(timedelta(hours=8))

    # Get current date in KL
    today = datetime.now(kl_tz).date()

    # Generate random hour and minute between 09:00 and 16:00
    start_hour, end_hour = 9, 16
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    # Combine into a datetime object
    dt = datetime.combine(today, time(hour, minute, second), tzinfo=kl_tz)

    # Return as ISO 8601 string
    return dt.isoformat()

async def get_fnr(conn):
    pasienter = await getPasient(conn, antall=1)
    return pasienter[0].pasient_fnr

async def generer_bkm(request: Request, response: Response):
    app = request.app
    pool = app.state.pool

    with pool.acquire() as conn:
        fnr = await get_fnr(conn)

    guid  = random_guid()
    tid   = random_kl_timestamp()
    belop = random_int_between(50, 1000)

    payload = {
        "praksisId": "1004326178",  # KUHR praksis
        "behandlerkrav": {
            "regninger": [
                {
                    "guid": str(guid),
                    "regningsnummer": "12496",
                    "tidspunkt": str(tid),
                    "pasient": {
                        "identifikasjon": {
                            "id": str(fnr),
                            "type": "FNR"
                        }
                    },
                    "arsakFriEgenandel": "F",
                    "belop": float(belop)
                }
            ],
            "antallRegninger": 1,
            "belop": float(belop)
        }
    }

    return payload
