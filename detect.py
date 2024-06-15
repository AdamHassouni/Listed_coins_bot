import asyncio
import logging
import json
import requests
import websockets
from asyncio import Event
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

# Initialize global variables
symbols = {}
ping_timeout = None
detectE = Event()

async def refresh_symbols():
    try:
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        response.raise_for_status()
        data = response.json()
        for symbol_info in data['symbols']:
            if symbol_info['status'] == 'TRADING':
                symbols[symbol_info['symbol']] = 1
    except requests.RequestException as err:
        raise err

async def on_open(websocket):
    log('Socket has been opened!')
    subscribe_message = {
        'method': 'SUBSCRIBE',
        'params': ['!miniTicker@arr'],
        'id': int(datetime.timestamp(datetime.now()))
    }
    await websocket.send(json.dumps(subscribe_message))

async def on_error(websocket, err):
    log(f"Socket error {err}")
    await asyncio.sleep(60)  # restart after 1 minute
    await start_ws()

async def heartbeat(websocket):
    global ping_timeout
    if ping_timeout:
        ping_timeout.cancel()
    ping_timeout = asyncio.create_task(ping_handler(websocket))

async def ping_handler(websocket):
    await asyncio.sleep(4 * 60)  # 4 minutes timeout
    log('Socket has been terminated due to heartbeat timeout!')
    await start_ws()

async def process_stream(websocket, message):
    payload = json.loads(message)
    if not isinstance(payload, list):
        return
    for data in payload:
        if not data.get('s'):
            continue
        if not data['s'].endswith('USDT'):
            continue
        if data['s'] not in symbols:
            # New symbol detected
            log(f"New symbol {data['s']} detected at {datetime.now()}")
            log(data)
            detectE.set()  # Emit event
            symbols[data['s']] = 1

async def start_ws():
    global ping_timeout
    try:
        log('Socket has been restarted!')
        await refresh_symbols()
        if ping_timeout:
            ping_timeout.cancel()
        uri = "wss://stream.binance.com:9443/ws"
        async with websockets.connect(uri) as websocket:
            await on_open(websocket)
            async for message in websocket:
                await process_stream(websocket, message)
                await heartbeat(websocket)
    except Exception as err:
        error(err)
        await asyncio.sleep(60)  # restart after 1 minute
        await start_ws()

# Run the WebSocket connection
asyncio.run(start_ws())
