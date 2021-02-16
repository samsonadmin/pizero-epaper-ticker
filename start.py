#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import json
import asyncio
import pathlib
import websockets
import ssl
import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
picdir = 'pic'


# https://pypi.org/project/websockets/
#
# pip3 install websockets


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE



uri='wss://api-pub.bitfinex.com:443/ws/2'
send_str='{ "event": "subscribe", "channel": "ticker", "symbol": "tBTCUST"}'

epd = epd2in13_V2.EPD()
logging.info("init and Clear")
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF)


time_image = Image.new('1', (epd.height, epd.width), 255)
time_draw = ImageDraw.Draw(time_image)

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)


last_price = 0




async def getTicker(myuri, myjson):
    global time_draw, epd
    async with websockets.connect(myuri, ssl=ssl_context) as websocket:
        await websocket.send(myjson)
        while True:
            response = await websocket.recv()
            try:
                price_array = json.loads(response)
                print(price_array[1][6])
                if (price_array[1][6] > 0 ):
                    last_price = price_array[1][6]
                else:
                    print("price error")

                print("Update screen")
                time_draw.rectangle((120, 80, 220, 105), fill = 255)
                time_draw.text((120, 40), time.strftime('%H:%M:%S'), font = font24, fill = 0)
                time_draw.text((120, 80), last_price, font = font24, fill = 0)
                #epd.displayPartial(epd.getbuffer(time_image))


            except:
                pass

            await asyncio.sleep(1)
            #print(response)


print("connection url:{}".format(uri))

image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame  
draw = ImageDraw.Draw(image)
draw.text((100, 20), 'e-Paper demo', font = font24, fill = 0)
epd.display(epd.getbuffer(image))

#epd.init(epd.PART_UPDATE)

time_image = Image.new('1', (epd.height, epd.width), 255)
time_draw = ImageDraw.Draw(time_image)


while True:
    time_draw.rectangle((120, 80, 220, 105), fill = 255)
    time_draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = 0)
    epd.display(epd.getbuffer(time_draw))
    time.sleep(5)
    epd.init(epd.FULL_UPDATE)

epd.Clear(0xFF)

asyncio.get_event_loop().run_until_complete(
    getTicker(uri, send_str)
)



logging.info("Clear...")
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF)
logging.info("Goto Sleep...")
epd.sleep()
time.sleep(3)
epd.Dev_exit()   

