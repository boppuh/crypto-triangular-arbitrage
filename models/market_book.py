#!/usr/bin/env python3

from collections import defaultdict
from typing import Dict, Optional


class MarketBook:
    def __init__(self):
        self.prices: Dict[str, Dict[str, Optional[float]]
                          ] = defaultdict(lambda: {'bid': None, 'ask': None})

    def update(self, symbol: str, bids: list, asks: list):
        best_bid = float(bids[0][0]) if bids else None
        best_ask = float(asks[0][0]) if asks else None

        self.prices[symbol]['bid'] = best_bid
        self.prices[symbol]['ask'] = best_ask

    def get(self, symbol: str) -> Dict[str, Optional[float]]:
        return self.prices.get(symbol, {'bid': None, 'ask': None})

    def dump(self):
        print("📘 MarketBook Snapshot:")
        for symbol, data in self.prices.items():
            print(f"  {symbol}: Bid {data['bid']} | Ask {data['ask']}")
