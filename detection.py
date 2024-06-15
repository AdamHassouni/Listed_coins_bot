import json
import time
import threading
import websocket
import requests

class BinanceListingDetector:
    def __init__(self):
        self.symbols = {}
        self.ws = None
        self.ping_timeout = None
        self.event_listeners = {}

    def refresh_symbols(self):
        try:
            resp = requests.get('https://api.binance.com/api/v3/exchangeInfo').json()
            for symbol_info in resp['symbols']:
                if symbol_info['status'] == 'TRADING':
                    self.symbols[symbol_info['symbol']] = 1
        except Exception as e:
            print(f"Error refreshing symbols: {e}")
            raise e

    def on_open(self, ws):
        print("Socket has been opened!")
        subscribe_message = json.dumps({
            "method": "SUBSCRIBE",
            "params": ["!miniTicker@arr"],
            "id": int(time.time())
        })
        ws.send(subscribe_message)

    def on_error(self, ws, error):
        print(f"Socket error: {error}")
        time.sleep(60)
        self.start_ws()

    def on_message(self, ws, message):
        payload = json.loads(message)
        if not isinstance(payload, list):
            return

        for data in payload:
            if 's' not in data:
                continue
            if not data['s'].endswith('USDT'):
                continue
            if data['s'] not in self.symbols:
                print(f"New symbol {data['s']} detected at {time.time()}")
                print(data)
                self.emit('NEWLISTING', data)
                self.symbols[data['s']] = 1

    def on_ping(self, ws, message):
        self.heartbeat()

    def heartbeat(self):
        if self.ping_timeout:
            self.ping_timeout.cancel()
        self.ping_timeout = threading.Timer(4*60, self.start_ws)
        self.ping_timeout.start()

    def start_ws(self):
        try:
            print("Socket has been restarted!")
            self.refresh_symbols()
            if self.ws:
                self.ws.close()
            self.ws = websocket.WebSocketApp(
                "wss://stream.binance.com:9443/ws",
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_ping=self.on_ping
            )
            self.heartbeat()
            self.ws.run_forever()
        except Exception as e:
            print(f"Error starting websocket: {e}")
            time.sleep(60)
            self.start_ws()

    def add_event_listener(self, event_type, listener):
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)

    def emit(self, event_type, data):
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                listener(data)

if __name__ == "__main__":
    detector = BinanceListingDetector()
    
    # Add your event listener for new listings
    def new_listing_listener(data):
        print(f"New listing detected: {data}")
    
    detector.add_event_listener('NEWLISTING', new_listing_listener)
    detector.start_ws()
