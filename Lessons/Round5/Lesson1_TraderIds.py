# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 1 - TRADER IDS: DETECT OLIVIA DIRECTLY
# =============================================================================
#
# WHAT THIS LESSON IS FOR
# -----------------------
# In some Prosperity rounds, the trade feed does not just tell you price and
# quantity. It also tells you who was on each side of the trade.
#
# That means you can look for specific trader names.
# One of the most useful names is "Olivia".
#
# The basic idea is very simple:
#   - if Olivia is buying, that is usually bullish
#   - if Olivia is selling, that is usually bearish
#
# This lesson shows a beginner-friendly version of that idea.
# We:
#   1. scan the market trades for Olivia
#   2. turn her latest action into a signal
#   3. use that signal in a small readable strategy
#   4. store the last signal in traderData so the bot remembers it
#
# This is not the full Frankfurt Hedgehogs strategy.
# It is the teaching version:
# small, direct, and easy to read.
# =============================================================================

import json
from typing import Dict, List, Optional

from datamodel import Order, OrderDepth, TradingState


class Trader:
    # ---------------------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------------------
    # We keep the lesson focused on one product so the trading logic stays
    # easy to follow.
    PRODUCT = "SQUID_INK"

    # A conservative position cap for the lesson strategy.
    # The real round limit may be different, but this keeps the example safe.
    POSITION_LIMIT = 200

    # How many units we want to hold when Olivia gives a clear signal.
    TARGET_POSITION = 60

    # Small quote size for the neutral market-making fallback.
    PASSIVE_SIZE = 5

    def load_memory(self, trader_data: Optional[str]) -> Dict[str, object]:
        # traderData is just a string, so we store our memory as JSON.
        # If nothing has been saved yet, start with an empty dictionary.
        if not trader_data:
            return {}

        try:
            return json.loads(trader_data)
        except json.JSONDecodeError:
            # If old traderData is malformed, do not crash the bot.
            # Just forget the old memory and keep trading.
            return {}

    def save_memory(self, memory: Dict[str, object]) -> str:
        # Keep the JSON compact so traderData stays small.
        return json.dumps(memory, separators=(",", ":"))

    def mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # A very standard fair-value estimate:
        # midpoint between the best bid and the best ask.
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) / 2

    def detect_olivia_signal(self, state: TradingState, memory: Dict[str, object]) -> int:
        # This function looks directly at the trade prints.
        # If Olivia bought most recently, return +1.
        # If Olivia sold most recently, return -1.
        # If Olivia has not traded recently, reuse the last known signal
        # for a short while, then fall back to 0.

        last_signal = int(memory.get("last_olivia_signal", 0))
        last_signal_time = int(memory.get("last_olivia_signal_time", -1))

        # Start with the remembered value.
        signal = last_signal
        signal_time = last_signal_time

        trades = state.market_trades.get(self.PRODUCT, [])
        for trade in trades:
            # Only trades involving Olivia matter for this lesson.
            if trade.buyer == "Olivia":
                trade_signal = 1
            elif trade.seller == "Olivia":
                trade_signal = -1
            else:
                continue

            # Use the newest Olivia trade we can find.
            # If two trades share the same timestamp, the later loop iteration
            # will win, which is fine for a beginner lesson.
            if trade.timestamp >= signal_time:
                signal = trade_signal
                signal_time = trade.timestamp

        # If Olivia has not appeared for a while, stop leaning on the signal.
        # The exact decay window is a teaching choice, not a magic number.
        if signal_time >= 0 and state.timestamp - signal_time > 3000:
            signal = 0

        memory["last_olivia_signal"] = signal
        memory["last_olivia_signal_time"] = signal_time

        return signal

    def take_best_prices(
        self,
        product: str,
        order_depth: OrderDepth,
        current_position: int,
        target_position: int,
    ) -> List[Order]:
        # This is the simplest "copy Olivia" rule:
        #   - if target_position is positive, buy toward it
        #   - if target_position is negative, sell toward it
        #
        # We only use the best available price on each side.
        orders: List[Order] = []

        buy_room = max(self.POSITION_LIMIT - current_position, 0)
        sell_room = max(self.POSITION_LIMIT + current_position, 0)

        if target_position > current_position and order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            available = abs(order_depth.sell_orders[best_ask])
            desired = target_position - current_position
            buy_qty = min(buy_room, available, desired)

            if buy_qty > 0:
                orders.append(Order(product, best_ask, buy_qty))

        if target_position < current_position and order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            available = order_depth.buy_orders[best_bid]
            desired = current_position - target_position
            sell_qty = min(sell_room, available, desired)

            if sell_qty > 0:
                orders.append(Order(product, best_bid, -sell_qty))

        return orders

    def passive_quote(
        self,
        product: str,
        order_depth: OrderDepth,
        current_position: int,
    ) -> List[Order]:
        # When Olivia is neutral, we do a tiny bit of market making.
        # This is intentionally small so the lesson stays readable.
        orders: List[Order] = []

        buy_room = max(self.POSITION_LIMIT - current_position, 0)
        sell_room = max(self.POSITION_LIMIT + current_position, 0)

        fair_value = self.mid_price(order_depth)
        if fair_value is None:
            return orders

        bid_price = int(fair_value) - 1
        ask_price = int(fair_value) + 1

        if buy_room > 0:
            orders.append(Order(product, bid_price, min(self.PASSIVE_SIZE, buy_room)))
        if sell_room > 0:
            orders.append(Order(product, ask_price, -min(self.PASSIVE_SIZE, sell_room)))

        return orders

    def run(self, state: TradingState):
        # This lesson only trades one product.
        result: Dict[str, List[Order]] = {}
        product = self.PRODUCT

        if product not in state.order_depths:
            return result, 0, self.save_memory({})

        order_depth = state.order_depths[product]
        current_position = state.position.get(product, 0)

        # Load our small memory blob from the previous tick.
        memory = self.load_memory(state.traderData)

        # Step 1: detect Olivia directly from the trade feed.
        signal = self.detect_olivia_signal(state, memory)

        # Step 2: convert the signal into a simple target position.
        #   +1 -> hold a small long position
        #   -1 -> hold a small short position
        #    0 -> stay close to flat
        if signal > 0:
            target_position = self.TARGET_POSITION
        elif signal < 0:
            target_position = -self.TARGET_POSITION
        else:
            target_position = 0

        print(
            f"[t={state.timestamp}] {product} | pos={current_position} | "
            f"signal={signal} | target={target_position}"
        )

        # Step 3: use the signal in a very readable way.
        # If Olivia is bullish, we try to move toward a long position.
        # If Olivia is bearish, we try to move toward a short position.
        # If Olivia is neutral, we place tiny passive quotes around fair value.
        if signal != 0:
            orders = self.take_best_prices(product, order_depth, current_position, target_position)
        else:
            orders = self.passive_quote(product, order_depth, current_position)

        result[product] = orders

        # Step 4: save memory for the next tick.
        trader_data = self.save_memory(memory)

        # The engine expects exactly three return values.
        conversions = 0
        return result, conversions, trader_data
