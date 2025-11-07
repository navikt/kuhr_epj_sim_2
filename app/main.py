import httpx
import asyncio
import uvicorn
import oracledb
from fastapi import FastAPI
from router import Innsending
from dotenv import load_dotenv
from utils.database import startup_pool
from contextlib import asynccontextmanager

# Init Oracle thick client
try:
    oracledb.init_oracle_client(lib_dir=r"C:\Workspace\oracleinstaclient\instantclient_23_9")
except oracledb.Error as e:
    print("Error initializing Oracle Client:", e)
    exit(1)

# Periodisk jobb
async def call_innsending_periodically():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://127.0.0.1:8000/innsending/send",
                    json={"amount": 1}
                )

        except Exception as e:
            pass
        await asyncio.sleep(60*60)

# Startup process
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    app.state.pool = startup_pool()
    # Start background task
    app.state.task = asyncio.create_task(call_innsending_periodically())

    yield

    # Shutdown
    print("Closing database connection pool...")
    if app.state.pool:
        app.state.pool.close()
        print("Connection pool closed.")
    app.state.task.cancel()

    try:
        await app.state.task
    except asyncio.CancelledError:
        pass

# Entrypoint
app = FastAPI(lifespan=lifespan)
app.include_router(Innsending.router)

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
