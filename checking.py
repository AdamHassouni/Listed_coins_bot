import time
import asyncio
import aiohttp
from datetime import datetime, timedelta

# Constants
CHECK_FROM = 10  # last 10 days
LAST_TS = int((datetime.now() - timedelta(days=CHECK_FROM)).timestamp() * 1000)
API_URL = 'https://api.binance.com/api/v3'
RATE_LIMIT = 10  # max 10 requests per second
MAX_CONCURRENT = 10

# Rate limiting
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

async def fetch_symbols(session):
    async with session.get(f'{API_URL}/exchangeInfo') as resp:
        data = await resp.json()
        return [d['symbol'] for d in data['symbols'] if d['quoteAsset'] == 'USDT' and d['status'] == 'TRADING']

async def fetch_listing_date(session, symbol):
    async with semaphore:
        async with session.get(f'{API_URL}/klines?symbol={symbol}&interval=1d&limit=1') as resp:
            data = await resp.json()
            return symbol, int(data[0][0])

async def main():
    async with aiohttp.ClientSession() as session:
        symbols = await fetch_symbols(session)
        print(f'{len(symbols)} USDT pairs identified.')

        tasks = [fetch_listing_date(session, symbol) for symbol in symbols]
        listing_dates = await asyncio.gather(*tasks)

        new_listings = [f'{symbol} is listed on {datetime.fromtimestamp(listed_on / 1000).strftime("%Y-%m-%d %H:%M:%S")}'
                        for symbol, listed_on in listing_dates if listed_on > LAST_TS]

        print(new_listings)

if __name__ == '__main__':
    asyncio.run(main())
