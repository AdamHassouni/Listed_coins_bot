import requests
import math
from decimal import Decimal

class BinanceTrader:
    def __init__(self):
        self.eInfo = {}

    def loadeInfo(self, symbol):
        try:
            resp = requests.get('https://api.binance.com/api/v3/exchangeInfo').json()
            einfoSymbol = next((s for s in resp['symbols'] if s['symbol'] == symbol), None)
            if not einfoSymbol:
                raise ValueError('Symbol missing in Exchange Info API')
            self.eInfo[symbol] = einfoSymbol
        except Exception as err:
            raise err

    def getQty(self, symbol, price, usdt):
        try:
            # Debugging: Print the filters to understand their structure
            print(self.eInfo[symbol]['filters'])

            # Attempt to find the correct filter for stepSize
            stepSize_filter = next(filter for filter in self.eInfo[symbol]['filters'] if 'stepSize' in filter)

            qstep = -math.log10(float(stepSize_filter['stepSize']))
            qty = round(usdt / price, int(qstep))
            return qty
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            # Handle the error or re-raise with more information
            raise KeyError(f"Missing key in symbol data for {symbol}: {e}")
        except StopIteration:
            # Handle the case where the stepSize filter is not found
            raise ValueError(f"'stepSize' filter not found for symbol {symbol}")
    def buy(self, keys, symbol, qty):
        try:
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quantity': str(qty),
                'newOrderRespType': 'FULL',
            }
            headers = {
                'X-MBX-APIKEY': keys['api'],
            }
            resp = requests.post(
                'https://api.binance.com/api/v3/order',
                params=params,
                headers=headers
            )
            if resp.status_code != 200:
                resp.raise_for_status()
            return resp.json()
        except Exception as err:
            raise err

    def sell(self, keys, buyPrice, symbol, qty, profit, sloss=None):
        try:
            pstep = -math.log10(float(self.eInfo[symbol]['filters'][0]['tickSize']))
            price = round(math.floor(buyPrice * (1 + profit / 100) * 10 ** pstep) / 10 ** pstep, int(pstep))
            if sloss:
                stopPrice = round(math.floor(buyPrice * (1 - sloss / 100) * 10 ** pstep) / 10 ** pstep, int(pstep))
                params = {
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': str(qty),
                    'price': str(price),
                    'stopPrice': str(stopPrice),
                    'stopLimitPrice': str(stopPrice),
                    'stopLimitTimeInForce': 'GTC',
                }
                path = 'https://api.binance.com/api/v3/order/oco'
            else:
                params = {
                    'symbol': symbol,
                    'side': 'SELL',
                    'type': 'LIMIT',
                    'quantity': str(qty),
                    'price': str(price),
                    'newOrderRespType': 'RESULT',
                    'timeInForce': 'GTC',
                }
                path = 'https://api.binance.com/api/v3/order'
            
            headers = {
                'X-MBX-APIKEY': keys['api'],
            }
            resp = requests.post(
                path,
                params=params,
                headers=headers
            )
            if resp.status_code != 200:
                resp.raise_for_status()
            return resp.json()
        except Exception as err:
            raise err

# Example usage
if __name__ == '__main__':
    trader = BinanceTrader()
    symbol = 'BTCUSDT'
    trader.loadeInfo(symbol)
    price = 50000.0  # example price
    usdt = 100.0  # example USDT amount to trade
    qty = trader.getQty(symbol, price, usdt)
    print(f'Quantity to buy: {qty}')

    keys = {
        'api': 'YOUR_API_KEY',
        'sec': 'YOUR_SECRET_KEY'
    }

    # Market Buy Order
    buy_order = trader.buy(keys, symbol, qty)
    print(f'Buy order: {buy_order}')

    # Sell Order
    profit = 5.0  # example profit percentage
    sloss = 2.0  # example stop loss percentage
    sell_order = trader.sell(keys, price, symbol, qty, profit, sloss)
    print(f'Sell order: {sell_order}')
