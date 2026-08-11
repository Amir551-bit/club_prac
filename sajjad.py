from asyncio import Event, Lock, Semaphore
from asyncio import new_event_loop, gather, timeout, sleep

lock = Lock()

async def run():
    async with lock:
        await sleep(2)


async def main():
    await gather(*(run() for _ in range(3)))


loop = new_event_loop()
loop.run_until_complete(main())
loop.close()
