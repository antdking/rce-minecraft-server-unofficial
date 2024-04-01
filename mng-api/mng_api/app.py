import fastapi
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import asyncio
import secrets

from . import mc
import os

MC_ADDRESS_INTERNAL = os.environ.get("MC_SERVER_ADDR_INTERNAL") or ""
MC_ADDRESS_EXTERNAL = os.environ.get("MC_SERVER_ADDR_EXTERNAL") or ""
MC_RCON_ADDRESS = os.environ.get("MC_RCON_ADDRESS") or ""
MC_RCON_PORT = os.environ.get("MC_RCON_PORT") or 25575
MC_RCON_PASSWORD = os.environ.get("MC_RCON_PASSWORD") or None
RCE_API_TOKEN = os.environ["RCE_API_TOKEN"]

mc_internal_healthcheck = mc.StatusCheckLoop(MC_ADDRESS_INTERNAL)
mc_external_healthcheck = mc.StatusCheckLoop(MC_ADDRESS_EXTERNAL)


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    tasks = set[asyncio.Task]()
    if MC_ADDRESS_INTERNAL:
        tasks.add(asyncio.create_task(mc_internal_healthcheck.start()))
    if MC_ADDRESS_EXTERNAL:
        tasks.add(asyncio.create_task(mc_external_healthcheck.start()))

    yield

    for task in tasks:
        task.cancel()


security = APIKeyHeader(name="x-api-key")


def require_api_key(token: str = fastapi.Depends(security)) -> bool:
    if not secrets.compare_digest(token, RCE_API_TOKEN):
        raise fastapi.HTTPException(status_code=403, detail="Invalid API Key")
    return True


app = fastapi.FastAPI(
    lifespan=lifespan, dependencies=[fastapi.Depends(require_api_key)]
)


@app.get("/healthz")
async def healthz():
    return {"self": "ok"}


@app.get("/healthz/full")
async def healthz_full():
    return {
        "self": "ok",
        "mc": {
            "internal": {
                "latency": mc_internal_healthcheck.latency,
                "last_check": mc_internal_healthcheck.last_check,
                "reachable": mc_internal_healthcheck.is_reachable(),
            },
            "latency": mc_external_healthcheck.latency,
            "reachable": mc_external_healthcheck.is_reachable(),
            "last_check": mc_external_healthcheck.last_check,
            "online_users": mc_external_healthcheck.online_users,
        },
    }


@app.post("/allow")
async def allowlist(username: str):
    client = mc.RconClient(MC_RCON_ADDRESS, 25575, password=MC_RCON_PASSWORD)
    result = await client.allow_user(username)
    return {
        "success": result,
    }


@app.post("/remove")
async def remove_user(username: str):
    client = mc.RconClient(MC_RCON_ADDRESS, 25575, password=MC_RCON_PASSWORD)
    result = await client.remove_user(username)
    return {
        "success": result,
    }
