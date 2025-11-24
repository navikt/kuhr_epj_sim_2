import os
import httpx
import asyncio
import uvicorn
import oracledb
from fastapi import FastAPI
from router import Innsending
from dotenv import load_dotenv
from utils.database import startup_pool
from contextlib import asynccontextmanager

load_dotenv()

# Init Oracle thick client
try:
    if os.getenv("MILJO") == "LOCAL":
        oracledb.init_oracle_client(lib_dir=r"C:\Workspace\oracleinstaclient\instantclient_23_9")
    else:
        oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_4")

except oracledb.Error as init_e:
    print("Error initializing Oracle Client:", init_e)
    exit(1)

# Periodisk jobb
async def call_innsending_periodically():

    freq   = int(os.getenv("CALL_FREQUENCY"))
    amount = int(os.getenv("CALL_AMOUNT"))

    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://127.0.0.1:8080/innsending/send",
                    json={"amount": amount}
                )
        except Exception as call_e:
            print(call_e)
        await asyncio.sleep(60*freq)

# Startup process
@asynccontextmanager
async def lifespan(f_app: FastAPI):

    # Startup
    f_app.state.pool = startup_pool()

    f_app.state.run_loop = True

    # Start background task
    f_app.state.task = asyncio.create_task(call_innsending_periodically())

    yield

    # Shutdown
    print("Closing database connection pool...")
    if f_app.state.pool:
        f_app.state.pool.close()
        print("Connection pool closed.")
    f_app.state.task.cancel()

    try:
        await f_app.state.task
    except asyncio.CancelledError:
        pass

# Entrypoint
app = FastAPI(lifespan=lifespan)

@app.get("/ready")
async def health_check():
    return "ok"

@app.get("/alive")
async def health_check():
    return "ok"

app.include_router(Innsending.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True, log_level="error")
