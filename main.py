import logging
from detect import detectE, start_ws
from order_making import loadeInfo, getQty, buy, sell
from validate import validation
from asyncio import run
from config import credentials
import Notification # Import the notifications module

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

log('NewCoinListings bot is running...')
validation()
log('The bot is waiting for a new coin to be listed in the USDT market.')
log('When detected, the bot automatically trades as per the configuration.')

# Start WebSocket
start_ws()

async def handle_new_listing(data):
    try:
        symbol = data['s']
        close_price = data['c']
        log(f"New symbol {symbol} detected with price {close_price}")

        # Load trading information for the symbol
        await loadeInfo(symbol)
        qty = getQty(symbol=symbol, price=close_price, usdt=credentials['usdt'])
        log(f"Trade size is {qty} for {credentials['usdt']} USDT at price {close_price} USDT")

        # Place buy order
        bresp = await buy(api_key=credentials['api'], secret_key=credentials['sec'], qty=qty, symbol=symbol)
        buy_price = sum(f['price'] * f['qty'] for f in bresp['fills']) / sum(f['qty'] for f in bresp['fills'])
        log(f"Buy price is {buy_price}")

        # Place sell order
        await sell(
            api_key=credentials['api'],
            secret_key=credentials['sec'],
            buy_price=buy_price,
            symbol=symbol,
            qty=qty,
            profit=credentials['profit'],
            sloss=credentials['sloss']
        )

        # Send notification
        Notification.send_notification(symbol, 'buy')
    except Exception as e:
        error(e)

# Event listener for new coin listings
detectE.on('NEWLISTING', handle_new_listing)

# Keep the script running
run(start_ws())
