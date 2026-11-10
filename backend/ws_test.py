import asyncio
import websockets

async def listen():
    async with websockets.connect('ws://127.0.0.1:8010/ws/monitor') as ws:
        print('Listening for live updates...')
        while True:
            msg = await ws.recv()
            print('RECEIVED:', msg)

if __name__ == "__main__":
    asyncio.run(listen())