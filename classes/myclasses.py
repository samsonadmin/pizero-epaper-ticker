import sys, time
import threading
import json
import asyncio
import pathlib
import websockets
import ssl

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        print( "Thread base init", file=sys.stderr )
        super(StoppableThread, self).__init__()
        self._stopper = threading.Event()          # ! must not use _stop

    def stopit(self):                              #  (avoid confusion)
        print( "Thread base stop()", file=sys.stderr )
        self._stopper.set()                        # ! must not use _stop

    def stopped(self):
        return self._stopper.is_set()              # ! must not use _stop


class GetBitFinexPriceThread(StoppableThread):
    #https://stackoverflow.com/questions/27102881/python-threading-self-stop-event-object-is-not-callable
    #https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/

    def __init__(self): 
        StoppableThread.__init__(self)  
        self.uri = 'wss://api-pub.bitfinex.com:443/ws/2'    
        self.send_str = '{ "event": "subscribe", "channel": "ticker", "symbol": "tBTCUST"}'
        self.last_price = 0


    def stopit(self): 
        print("STOP GetBitFinexPriceThread")     
        StoppableThread.stopit(self) 

    def run(self): 
        print("connection url:{}".format(self.uri))

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE


        async def getTicker(myuri, myjson):
            async with websockets.connect(myuri, ssl=ssl_context) as websocket:

                await websocket.send(myjson)
                while not self.stopped():
                    response = await websocket.recv()
                    try:
                        price_array = json.loads(response)
                        print(price_array[1][6])
                        if (price_array[1][6] > 0 ):
                            self.last_price = price_array[1][6]
                    except:
                        pass
                    #print(response)

        asyncio.get_event_loop().run_until_complete(
            getTicker(self.uri, self.send_str)
        )




