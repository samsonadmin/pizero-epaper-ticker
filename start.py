# https://pypi.org/project/websockets/
#
# pip3 install websockets
import json
import asyncio
import pathlib
import websockets
import ssl
    
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE



uri='wss://api-pub.bitfinex.com:443/ws/2'
send_str='{ "event": "subscribe", "channel": "ticker", "symbol": "tBTCUST"}'

last_price = 0

async def getTicker(myuri, myjson):
    async with websockets.connect(myuri, ssl=ssl_context) as websocket:

        await websocket.send(myjson)
        while True:
            response = await websocket.recv()
            try:
                price_array = json.loads(response)
                print(price_array[1][6])
                if (price_array[1][6] > 0 ):
                    last_price = price_array[1][6]
            except:
                pass
            #print(response)

print("connection url:{}".format(uri))

asyncio.get_event_loop().run_until_complete(
    getTicker(uri, send_str)
)

