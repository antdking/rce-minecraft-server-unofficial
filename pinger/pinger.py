import asyncio
import mcstatus
import os
import traceback
import datetime


MC_SERVER_ADDR = os.environ["MC_SERVER_ADDR"]
SLEEP_TIME = 10  # seconds


async def get_server(addr: str = MC_SERVER_ADDR) -> mcstatus.JavaServer:
    return await mcstatus.JavaServer.async_lookup(MC_SERVER_ADDR)


async def main():
    server = await get_server()
    keep_trying = True
    while keep_trying:
        try:
            status = await server.async_status()
            print(f"[{datetime.datetime.utcnow()}] status: {status.latency:.0f}ms; online={status.players.online}; name='{status.description}'")
        except asyncio.TimeoutError:
            print(f"[{datetime.datetime.utcnow()}] status: timed out")
        except KeyboardInterrupt:
            keep_trying = False
        except Exception as e:
            print(f"[{datetime.datetime.utcnow()}] unknown exception: ", e)
            traceback.print_exc()
        await asyncio.sleep(SLEEP_TIME)


if __name__ == '__main__':
    asyncio.run(main())
