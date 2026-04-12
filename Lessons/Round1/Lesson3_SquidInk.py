# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 3 - SQUID INK: FOLLOW THE DAILY EXTREMES
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This is a beginner-friendly lesson bot for SQUID_INK.
#
# The main idea is not "predict the whole price chart".
# Instead, we look for a very specific behavior:
#
#   - one trader tends to buy near the daily low
#   - the same trader tends to sell near the daily high
#
# That is the "daily-extrema / informed-trader" idea.
# We do not need to know the trader's name to learn from the pattern.
# We only need to notice that large trades keep appearing at the day low
# and day high.
#
# HOW THE LESSON BOT WORKS
# ------------------------
# 1. Read the previous note from traderData.
# 2. Track today's running low and running high.
# 3. Look for a 15-lot trade at one of those extremes.
# 4. If we see a buy-at-low signal, target a long position.
# 5. If we see a sell-at-high signal, target a short position.
# 6. Save everything back into traderData for the next tick.
#
# This is intentionally simple. The goal is learning clarity, not maximum
# performance.
# =============================================================================

from datamodel import OrderDepth, TradingState, Order
from typing import List
import json


class Trader:
    # ---------------------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------------------
    # SQUID_INK is the only product we actively trade in this lesson.
    # The position limit in Prosperity is 50 units.
    # The pattern we care about is usually a 15-lot trade.
    # ---------------------------------------------------------------------
    PRODUCT = "SQUID_INK"
    POSITION_LIMIT = 50
    SIGNAL_TRADE_SIZE = 15

    # Prosperity timestamps increase by 100 each tick, and a day is roughly
    # 10,000 ticks. That means one day is about 1,000,000 timestamp units.
    DAY_LENGTH = 1_000_000

    def get_day_index(self, timestamp: int) -> int:
        # Convert the raw timestamp into a day number.
        return timestamp // self.DAY_LENGTH

    def load_memory(self, state: TradingState) -> dict:
        # traderData is the note we wrote at the end of the previous tick.
        # If it is empty or broken, start with an empty dictionary.
        if not state.traderData:
            return {}

        try:
            memory = json.loads(state.traderData)
            if isinstance(memory, dict):
                return memory
        except Exception:
            pass

        return {}

    def save_memory(self, memory: dict) -> str:
        # Compact JSON keeps traderData small and easy to inspect.
        return json.dumps(memory, separators=(",", ":"))

    def start_new_day_memory(self, day_index: int) -> dict:
        # A new day starts with fresh extrema and no signal.
        return {
            "day_index": day_index,
            "running_low": None,
            "running_high": None,
            "signal_side": 0,      # 1 = buy, -1 = sell, 0 = no signal
            "signal_price": None,   # the extreme price that created the signal
        }

    def get_best_bid_ask(self, order_depth: OrderDepth):
        # Best bid = highest buy price.
        # Best ask = lowest sell price.
        best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
        return best_bid, best_ask

    def update_running_extremes(self, memory: dict, trades) -> None:
        # Update today's low and high using the trade prices we just saw.
        running_low = memory["running_low"]
        running_high = memory["running_high"]

        for trade in trades:
            price = trade.price

            if running_low is None or price < running_low:
                running_low = price

            if running_high is None or price > running_high:
                running_high = price

        memory["running_low"] = running_low
        memory["running_high"] = running_high

    def detect_extreme_signal(self, memory: dict, trades) -> None:
        # This is the core learning idea.
        #
        # If a 15-lot trade happens exactly at today's low, we treat that as
        # a buy signal.
        #
        # If a 15-lot trade happens exactly at today's high, we treat that as
        # a sell signal.
        #
        # We only start doing this once the day has a real range.
        running_low = memory["running_low"]
        running_high = memory["running_high"]

        if running_low is None or running_high is None:
            return

        if running_low == running_high:
            # Nothing interesting yet. We only have one price so far.
            return

        for trade in trades:
            if abs(trade.quantity) != self.SIGNAL_TRADE_SIZE:
                continue

            if trade.price == running_low:
                memory["signal_side"] = 1
                memory["signal_price"] = trade.price

            elif trade.price == running_high:
                memory["signal_side"] = -1
                memory["signal_price"] = trade.price

    def invalidate_stale_signal(self, memory: dict) -> None:
        # A signal is only useful while the old extreme is still the extreme.
        #
        # If a new lower low appears after a buy-at-low signal, the old signal
        # is no longer the same setup.
        #
        # If a new higher high appears after a sell-at-high signal, we also
        # clear the old signal.
        signal_side = memory.get("signal_side", 0)
        signal_price = memory.get("signal_price")
        running_low = memory.get("running_low")
        running_high = memory.get("running_high")

        if signal_side == 1 and signal_price is not None:
            if running_low is not None and running_low < signal_price:
                memory["signal_side"] = 0
                memory["signal_price"] = None

        elif signal_side == -1 and signal_price is not None:
            if running_high is not None and running_high > signal_price:
                memory["signal_side"] = 0
                memory["signal_price"] = None

    def trade_towards_target(self, product: str, order_depth: OrderDepth, current_position: int, target_position: int) -> List[Order]:
        # This helper places one aggressive order toward the target position.
        # It keeps the lesson simple: follow the signal, then cross the spread.
        orders: List[Order] = []

        best_bid, best_ask = self.get_best_bid_ask(order_depth)
        position_gap = target_position - current_position

        if position_gap > 0 and best_ask is not None:
            # We want to buy.
            available_volume = abs(order_depth.sell_orders[best_ask])
            buy_volume = min(position_gap, available_volume)

            if buy_volume > 0:
                orders.append(Order(product, best_ask, buy_volume))

        elif position_gap < 0 and best_bid is not None:
            # We want to sell.
            available_volume = order_depth.buy_orders[best_bid]
            sell_volume = min(-position_gap, available_volume)

            if sell_volume > 0:
                orders.append(Order(product, best_bid, -sell_volume))

        return orders

    def run(self, state: TradingState):
        # -----------------------------------------------------------------
        # STEP 1 - LOAD OUR MEMORY FROM THE PREVIOUS TICK
        # -----------------------------------------------------------------
        memory = self.load_memory(state)
        current_day = self.get_day_index(state.timestamp)

        # If this is a new day, reset the day-specific memory.
        if memory.get("day_index") != current_day:
            memory = self.start_new_day_memory(current_day)
        else:
            # Make sure older traderData still has all the keys we expect.
            memory.setdefault("running_low", None)
            memory.setdefault("running_high", None)
            memory.setdefault("signal_side", 0)
            memory.setdefault("signal_price", None)

        result = {}

        # -----------------------------------------------------------------
        # STEP 2 - LOOP OVER THE PRODUCTS
        # -----------------------------------------------------------------
        # We keep the loop structure from Lesson 1 so the file still looks
        # like a normal Prosperity bot.
        for product in state.order_depths:
            orders: List[Order] = []

            if product == self.PRODUCT:
                order_depth = state.order_depths[product]
                recent_trades = state.market_trades.get(product, [])

                # ---------------------------------------------------------
                # STEP 2A - UPDATE THE DAY'S RUNNING LOW AND HIGH
                # ---------------------------------------------------------
                self.update_running_extremes(memory, recent_trades)

                # ---------------------------------------------------------
                # STEP 2B - LOOK FOR THE DAILY-EXTREME SIGNAL
                # ---------------------------------------------------------
                self.detect_extreme_signal(memory, recent_trades)

                # ---------------------------------------------------------
                # STEP 2C - DISCARD STALE SIGNALS
                # ---------------------------------------------------------
                self.invalidate_stale_signal(memory)

                # ---------------------------------------------------------
                # STEP 2D - TURN THE SIGNAL INTO A POSITION TARGET
                # ---------------------------------------------------------
                signal_side = memory.get("signal_side", 0)
                target_position = {
                    1: self.POSITION_LIMIT,
                    -1: -self.POSITION_LIMIT,
                }.get(signal_side, 0)

                current_position = state.position.get(product, 0)

                # ---------------------------------------------------------
                # STEP 2E - PLACE THE ACTUAL ORDER
                # ---------------------------------------------------------
                # If we have a buy signal, we buy up to the long limit.
                # If we have a sell signal, we sell down to the short limit.
                # If there is no signal, we flatten back toward zero.
                orders = self.trade_towards_target(
                    product,
                    order_depth,
                    current_position,
                    target_position,
                )

            result[product] = orders

        # -----------------------------------------------------------------
        # STEP 3 - SAVE MEMORY FOR THE NEXT TICK
        # -----------------------------------------------------------------
        traderData = self.save_memory(memory)
        conversions = 1

        return result, conversions, traderData
