#!/usr/bin/env python3

import asyncio
import json
import ssl
import websockets

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Example trading pairs for a triangle: BTC/USDT, ETH/BTC, ETH/USDT
TRADING_PAIRS = ['btcusdt', 'ethbtc', 'ethusdt']

BINANCE_WS_BASE = 'wss://stream.binance.com:9443/stream?streams='
STREAM_SUFFIX = '@depth5@100ms'  # Top 5 order book levels, 100ms updates

def build_url(pairs):
    streams = '/'.join([f"{pair.lower()}{STREAM_SUFFIX}" for pair in pairs])
    return BINANCE_WS_BASE + streams

async def handle_message(message):
    data = json.loads(message)
    stream = data.get('stream')
    payload = data.get('data')

    if not payload or 'bids' not in payload:
        return

    symbol = payload['s']
    bids = payload['b']
    asks = payload['a']

    # You can store these in a shared in-memory structure for live triangle analysis
    print(f"[{symbol}] Top bid: {bids[0]} | Top ask: {asks[0]}")

async def listen_to_depth():
    url = build_url(TRADING_PAIRS)
    async with websockets.connect(url, ssl=ssl_context) as ws:
        print("Connected to Binance WebSocket...")
        while True:
            message = await ws.recv()
            await handle_message(message)

if __name__ == "__main__":
    asyncio.run(listen_to_depth())

