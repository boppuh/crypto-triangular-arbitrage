#!/usr/bin/env python3

import asyncio
import json
import ssl
import websockets

from models.market_book import MarketBook
from analyzers.triangle_finder import TriangleArbitrageFinder


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Example trading pairs for a triangle: BTC/USDT, ETH/BTC, ETH/USDT
TRADING_PAIRS = ['btcusdt', 'ethbtc', 'ethusdt']

BINANCE_WS_BASE = 'wss://stream.binance.com:9443/stream?streams='
STREAM_SUFFIX = '@depth5@100ms'  # Top 5 order book levels, 100ms updates

market_book = MarketBook()
arb_finder = TriangleArbitrageFinder(market_book)


def build_url(pairs):
    streams = '/'.join([f"{pair.lower()}{STREAM_SUFFIX}" for pair in pairs])
    return BINANCE_WS_BASE + streams


async def handle_message(message):
    data = json.loads(message)
    stream = data.get('stream')
    payload = data.get('data')

    if not payload or 'bids' not in payload:
        return

    symbol = stream.split('@')[0].upper()
    bids = payload.get('bids', [])
    asks = payload.get('asks', [])

    # Update book
    market_book.update(symbol, bids, asks)

    # Print current best price
    latest = market_book.get(symbol)
    print(f"[{symbol}] Bid: {latest['bid']} | Ask: {latest['ask']}")

    # Run triangle scan
    opportunities = arb_finder.find_opportunities()
    for opp in opportunities:
        print(
            f"🚀 TRIANGLE FOUND: {opp['path']} | ROI: {opp['roi']:.4f}% | Profit: ${opp['profit']:.2f}")
        arb_finder.simulate_execution(opp)


async def listen_to_depth():
    url = build_url(TRADING_PAIRS)
    async with websockets.connect(url, ssl=ssl_context) as ws:
        print("Connected to Binance WebSocket...")
        while True:
            message = await ws.recv()
            await handle_message(message)


if __name__ == "__main__":
    asyncio.run(listen_to_depth())
