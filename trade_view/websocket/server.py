import math
import time
import asyncio
import websockets

async def stream():
    async with websockets.connect(
        "ws://localhost:3000/api/live/push/sinewave_test", 
        extra_headers={'Authorization': 'Bearer eyJrIjoiRDA2RlpjUVBQTDAzSFYzSjkwWVlvOHltRHhiUGthdHYiLCJuIjoidGVsZWdyYWYiLCJpZCI6MX0='}
    ) as websocket:
        i = 0
        while True:
            await websocket.send("test Sinewave=" + str((math.sin(math.radians(i))+1)*20+80) +" " + str(time.time_ns()+1000000000))
            if (i == 361):
                i = 0
            else:
                i = i + 15
            await asyncio.sleep(0.03)

asyncio.run(stream())