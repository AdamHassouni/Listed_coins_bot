import sys
import logging
from binance import binance
from config import credentials

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

def terminate(message):
    log(message)
    log('Terminating the bot...')
    sys.exit()

async def validation():
    try:
        api = credentials.get('api')
        sec = credentials.get('sec')
        usdt = credentials.get('usdt')
        profit = credentials.get('profit')
        sloss = credentials.get('sloss')

        if not api:
            terminate('"api" is missing in config file!')
        if len(api) != 64:
            terminate('"api" should be an alphanumeric string of 64 char!')
        if not sec:
            terminate('"sec" is missing in config file!')
        if len(sec) != 64:
            terminate('"sec" should be an alphanumeric string of 64 char!')
        if not isinstance(usdt, (int, float)):
            terminate('"usdt" is missing or not a number in config file!')
        if not isinstance(profit, (int, float)):
            terminate('"profit" is missing or not a number in config file!')
        if sloss and not isinstance(sloss, (int, float)):
            terminate('"sloss" must be a number in config file!')
        if sloss and sloss < 0.05:
            log('Warning! Stop-Loss is less than 5%, which could be too tight and result in the sell OCO order failure!')

        # Test the API keys by placing a test order
        response = await binance({
            'method': 'POST',
            'path': '/api/v3/order/test',
            'keys': {'api': api, 'sec': sec},
            'params': {
                'quantity': 20,
                'symbol': 'XRPUSDT',
                'side': 'BUY',
                'type': 'MARKET',
                'newOrderRespType': 'FULL',
            },
        })

    except Exception as err:
        terminate(
            str(err) +
            ' Invalid API keys, or Insufficient access to API keys, or IP Address access could be missing for the API keys'
        )

# Example of how to run validation
if __name__ == "__main__":
    import asyncio
    asyncio.run(validation())
