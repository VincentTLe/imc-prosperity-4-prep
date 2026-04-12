# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 2 - PICNIC_BASKET2: A SIMPLE BASKET ARBITRAGE BOT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson shows how to trade a basket product against its constituents.
# The idea is very similar to Lesson 1, but instead of comparing a product to
# a fixed fair value, we build a synthetic fair value from other products.
#
# For PICNIC_BASKET2, the reference hedge uses:
#   - CROISSANTS
#   - JAMS
#   - DJEMBES
#
# In the Frankfurt Hedgehogs reference strategy, the basket weights for
# PICNIC_BASKET2 are:
#   4 x CROISSANTS + 2 x JAMS + 0 x DJEMBES
#
# So the third leg is kept in the code for clarity, but its weight is zero.
#
# WHAT IS THE TRADE?
# -------------------
# If the basket is trading ABOVE its synthetic fair value, it is expensive.
# We sell the basket and buy the hedge legs.
#
# If the basket is trading BELOW its synthetic fair value, it is cheap.
# We buy the basket and sell the hedge legs.
#
# WHAT IS THE SIGNAL?
# -------------------
# spread = basket_mid - synthetic_fair_value
#
#   spread > ENTRY_THRESHOLD  -> basket is rich, short basket
#   spread < -ENTRY_THRESHOLD -> basket is cheap, long basket
#
# To avoid flipping back and forth on tiny noise, we use an exit band:
#   - if the spread comes back close to zero, we close the position
#
# SIMPLE INVENTORY HANDLING
# --------------------------
# Every product has a hard position limit.
# We never place an order that would push us past that limit.
# We also keep the logic simple:
#   - compute a target position
#   - compare it with the current position
#   - trade only the difference we still need
#
# =============================================================================

from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional, Tuple


class Trader:
    # -------------------------------------------------------------------------
    # BASKET SETUP
    # -------------------------------------------------------------------------
    # This is the one basket we trade in this lesson.
    # The basket is priced against the three constituent products below.
    # -------------------------------------------------------------------------
    BASKET = "PICNIC_BASKET2"
    CONSTITUENTS = ["CROISSANTS", "JAMS", "DJEMBES"]

    # Basket composition:
    #   synthetic_value = 4 * CROISSANTS + 2 * JAMS + 0 * DJEMBES
    # This matches the reference Frankfurt Hedgehogs basket-2 setup.
    WEIGHTS = [4, 2, 0]

    # Position limits from the reference code.
    POSITION_LIMITS = {
        BASKET: 100,
        "CROISSANTS": 250,
        "JAMS": 350,
        "DJEMBES": 60,
    }

    # Thresholds for the spread signal.
    # Entry is wider than exit so we do not churn around zero.
    ENTRY_THRESHOLD = 50
    EXIT_THRESHOLD = 10

    def run(self, state: TradingState):
        # Result format required by the engine:
        #   { "PRODUCT": [Order(...), Order(...)] }
        result: Dict[str, List[Order]] = {}

        # We only trade products we can actually compute a fair value for.
        trade_products = [self.BASKET] + self.CONSTITUENTS

        # Build a position lookup once so the rest of the code stays simple.
        positions = {product: state.position.get(product, 0) for product in trade_products}

        # ---------------------------------------------------------------------
        # 1) READ THE LIVE MARKET PRICES
        # ---------------------------------------------------------------------
        # We use the mid price of each product:
        #   mid = (best_bid + best_ask) / 2
        #
        # This keeps the example easy to follow.
        # In production you might use richer estimates, but the mid is enough
        # for a beginner-friendly lesson.
        # ---------------------------------------------------------------------
        basket_mid = self.get_mid_price(state.order_depths.get(self.BASKET))
        constituent_mids = []
        for product in self.CONSTITUENTS:
            constituent_mids.append(self.get_mid_price(state.order_depths.get(product)))

        # If any required price is missing, we simply do nothing.
        if basket_mid is None or any(mid is None for mid in constituent_mids):
            return result, 1, ""

        # ---------------------------------------------------------------------
        # 2) COMPUTE THE SYNTHETIC FAIR VALUE
        # ---------------------------------------------------------------------
        # This is the core of basket arbitrage.
        #
        # Example:
        #   fair_value = 4 * croissants_mid + 2 * jams_mid + 0 * djembes_mid
        #
        # Then we compare the live basket price to that synthetic value.
        # ---------------------------------------------------------------------
        synthetic_fair_value = 0.0
        for price, weight in zip(constituent_mids, self.WEIGHTS):
            synthetic_fair_value += price * weight

        spread = basket_mid - synthetic_fair_value

        print(
            f"[t={state.timestamp}] basket_mid={basket_mid:.2f} "
            f"synthetic={synthetic_fair_value:.2f} spread={spread:.2f}"
        )

        # ---------------------------------------------------------------------
        # 3) DECIDE THE TARGET POSITION
        # ---------------------------------------------------------------------
        # The target is the position we would like to end up with.
        #
        # A simple hysteresis rule:
        #   - if spread is large and positive: short the basket
        #   - if spread is large and negative: long the basket
        #   - if spread is near zero: close the basket position
        #   - otherwise: keep the current position
        #
        # We use the basket position as the "main" signal.
        # The hedge legs are sized from that basket target.
        # ---------------------------------------------------------------------
        basket_position = positions[self.BASKET]
        if spread > self.ENTRY_THRESHOLD:
            target_basket_position = -self.POSITION_LIMITS[self.BASKET]
        elif spread < -self.ENTRY_THRESHOLD:
            target_basket_position = self.POSITION_LIMITS[self.BASKET]
        elif abs(spread) < self.EXIT_THRESHOLD:
            target_basket_position = 0
        else:
            target_basket_position = basket_position

        # If we want to be short the basket, we buy the constituents.
        # If we want to be long the basket, we sell the constituents.
        target_positions = {
            self.BASKET: target_basket_position,
        }
        for product, weight in zip(self.CONSTITUENTS, self.WEIGHTS):
            target_positions[product] = -target_basket_position * weight

        # ---------------------------------------------------------------------
        # 4) TRANSLATE TARGETS INTO ORDERS
        # ---------------------------------------------------------------------
        # For each product:
        #   current_position -> target_position
        #   difference > 0   -> buy
        #   difference < 0   -> sell
        #
        # We only trade at the top of book.
        # That keeps the lesson short and easy to reason about.
        # ---------------------------------------------------------------------
        for product in trade_products:
            order_depth = state.order_depths.get(product)
            if order_depth is None:
                continue

            current_position = positions[product]
            target_position = self.clamp_target(product, target_positions[product])
            delta = target_position - current_position

            if delta > 0:
                self.buy_toward_target(
                    product,
                    order_depth,
                    current_position,
                    delta,
                    result,
                )
            elif delta < 0:
                self.sell_toward_target(
                    product,
                    order_depth,
                    current_position,
                    -delta,
                    result,
                )

        return result, 1, ""

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def get_mid_price(self, order_depth: Optional[OrderDepth]) -> Optional[float]:
        # Without both sides of the book we do not have a proper mid price.
        if order_depth is None:
            return None
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return None

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) / 2.0

    def clamp_target(self, product: str, desired_target: int) -> int:
        # Keep the target within the allowed position range.
        limit = self.POSITION_LIMITS[product]
        return max(-limit, min(limit, desired_target))

    def buy_toward_target(
        self,
        product: str,
        order_depth: OrderDepth,
        current_position: int,
        desired_buy_quantity: int,
        result: Dict[str, List[Order]],
    ) -> None:
        # Buy only if there is someone willing to sell.
        if len(order_depth.sell_orders) == 0:
            return

        best_ask = min(order_depth.sell_orders.keys())
        available_at_ask = abs(order_depth.sell_orders[best_ask])

        # Do not exceed our position limit.
        room_to_buy = self.POSITION_LIMITS[product] - current_position
        buy_quantity = min(desired_buy_quantity, available_at_ask, room_to_buy)

        if buy_quantity <= 0:
            return

        result.setdefault(product, []).append(Order(product, best_ask, buy_quantity))

    def sell_toward_target(
        self,
        product: str,
        order_depth: OrderDepth,
        current_position: int,
        desired_sell_quantity: int,
        result: Dict[str, List[Order]],
    ) -> None:
        # Sell only if there is someone willing to buy.
        if len(order_depth.buy_orders) == 0:
            return

        best_bid = max(order_depth.buy_orders.keys())
        available_at_bid = order_depth.buy_orders[best_bid]

        # Do not exceed our short limit.
        room_to_sell = self.POSITION_LIMITS[product] + current_position
        sell_quantity = min(desired_sell_quantity, available_at_bid, room_to_sell)

        if sell_quantity <= 0:
            return

        result.setdefault(product, []).append(Order(product, best_bid, -sell_quantity))
