#!/usr/bin/env python3

class TriangleArbitrageFinder:
    def __init__(self, market_book, fee_rate=0.001):  # 0.1% fee per trade
        self.book = market_book
        self.fee_rate = fee_rate
        self.simulated_balance = 1000.0
        self.opportunity_log = []

    def compute_trade(self, amount, price, reverse=False):
        """Apply a trade and deduct fee."""
        if reverse:
            result = amount / price  # buy: spend amount in quote to get base
        else:
            result = amount * price  # sell: base to quote
        return result * (1 - self.fee_rate)

    def check_triangle(self, start_amt, path):
        """
        Example path: ['USDT', 'BTC', 'ETH', 'USDT']
        Simulate: USDT → BTC → ETH → USDT
        """
        a, b, c, d = path
        pair1 = a + b
        pair2 = b + c
        pair3 = c + d

        # Prices from order book
        p1 = self.book.get(pair1)['ask']  # buy B with A
        p2 = self.book.get(pair2)['ask']  # buy C with B
        p3 = self.book.get(pair3)['bid']  # sell C for D

        if None in (p1, p2, p3):
            return None  # incomplete data

        amt1 = self.compute_trade(start_amt, p1, reverse=True)
        amt2 = self.compute_trade(amt1, p2, reverse=True)
        final = self.compute_trade(amt2, p3, reverse=False)

        profit = final - start_amt
        roi = (profit / start_amt) * 100

        return {
            'path': f"{a} → {b} → {c} → {d}",
            'start': start_amt,
            'final': final,
            'profit': profit,
            'roi': roi
        }

    def find_opportunities(self, start_amt=1000):
        paths = [
            ['USDT', 'BTC', 'ETH', 'USDT'],
            ['USDT', 'ETH', 'BTC', 'USDT']
        ]
        results = []
        for path in paths:
            result = self.check_triangle(start_amt, path)
            if result and result['profit'] > 0:
                results.append(result)
        return results

    def simulate_execution(self, result):
        self.simulated_balance = result['final']
        self.opportunity_log.append(result)
        print(
            f"✅ Simulated Execution | New Balance: ${self.simulated_balance:.2f}")
