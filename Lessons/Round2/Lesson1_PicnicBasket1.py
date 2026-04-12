# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 1 - PICNIC BASKET 1: SYNTHETIC FAIR VALUE AND SPREAD TRADING
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson shows how to trade PICNIC_BASKET1 against the products that
# make it up:
#
#   - CROISSANTS
#   - JAMS
#   - DJEMBES
#
# The key idea is simple:
#   1. Estimate the basket's "synthetic fair value" from its constituents.
#   2. Compare the basket price to that synthetic value.
#   3. Buy the basket when it is cheap.
#   4. Sell the basket when it is expensive.
#
# This is the same basic idea behind ETF arbitrage in real markets.
# We are not predicting direction in the usual sense.
# We are just looking for temporary mispricing between linked products.
#
# WHY THIS IS USEFUL
# ------------------
# If the basket is worth more than its parts, it is overpriced.
# If the basket is worth less than its parts, it is underpriced.
#
# Example synthetic value:
#   6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES
#
# If that synthetic value is 100 and the basket trades at 120, the basket has
# a +20 spread. That is expensive relative to the constituents.
#
# In this lesson we keep the logic beginner-friendly:
#   - use the current mid price of each product
#   - compute one spread
#   - use a fixed entry threshold
#   - use a smaller exit threshold to avoid churning
#   - keep inventory under control with target positions
#
# =============================================================================

from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional


# -----------------------------------------------------------------------------
# PRODUCTS AND SIMPLE LIMITS
# -----------------------------------------------------------------------------
# These limits are intentionally conservative and easy to reason about.
# The exact values are not the lesson's main point.
# -----------------------------------------------------------------------------
BASKET = "PICNIC_BASKET1"
CROISSANTS = "CROISSANTS"
JAMS = "JAMS"
DJEMBES = "DJEMBES"

CONSTITUENT_WEIGHTS = {
    CROISSANTS: 6,
    JAMS: 3,
    DJEMBES: 1,
}

POSITION_LIMITS = {
    BASKET: 60,
    CROISSANTS: 250,
    JAMS: 350,
    DJEMBES: 60,
}

# Fixed thresholds for the spread.
# Entry threshold: open a trade when the basket is clearly mispriced.
# Exit threshold: close the trade once the spread comes back near zero.
ENTRY_THRESHOLD = 50
EXIT_THRESHOLD = 10

# This is the size we aim for when the spread is strong enough.
TARGET_BASKET_POSITION = 40


def best_bid_ask(order_depth: OrderDepth) -> tuple[Optional[int], Optional[int]]:
    """
    Return the best bid and best ask for one order book.

    - Best bid = highest buy price
    - Best ask = lowest sell price
    """
    best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
    best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
    return best_bid, best_ask


def midpoint(order_depth: OrderDepth) -> Optional[float]:
    """
    Estimate a fair price from the visible order book.

    We use the best bid and best ask when both exist.
    If only one side exists, we nudge by half a tick.
    """
    best_bid, best_ask = best_bid_ask(order_depth)

    if best_bid is not None and best_ask is not None:
        return (best_bid + best_ask) / 2
    if best_bid is not None:
        return best_bid + 0.5
    if best_ask is not None:
        return best_ask - 0.5
    return None


def take_volume_to_target(current_position: int, target_position: int) -> int:
    """
    Convert a current position and target position into the signed volume
    needed to move toward the target.

    Positive return value means buy.
    Negative return value means sell.
    """
    return target_position - current_position


def capped_volume(product: str, desired_volume: int, current_position: int) -> int:
    """
    Keep orders inside the position limit.

    If we want to buy, the available room is limit - current_position.
    If we want to sell, the available room is limit + current_position.
    """
    limit = POSITION_LIMITS[product]
    if desired_volume > 0:
        return min(desired_volume, limit - current_position)
    if desired_volume < 0:
        return max(desired_volume, -limit - current_position)
    return 0


class Trader:
    # =========================================================================
    # THE TRADER
    # =========================================================================
    # This trader only knows one story:
    #   - compute the synthetic fair value of PICNIC_BASKET1
    #   - compare the basket to that synthetic value
    #   - trade the spread when it is large enough
    # =========================================================================

    def synthetic_fair_value(self, state: TradingState) -> Optional[float]:
        """
        Calculate the basket's synthetic fair value from its constituents.

        For PICNIC_BASKET1, the recipe is:
            6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES
        """
        total = 0.0

        for product, weight in CONSTITUENT_WEIGHTS.items():
            order_depth = state.order_depths.get(product)
            if order_depth is None:
                return None

            price = midpoint(order_depth)
            if price is None:
                return None

            total += weight * price

        return total

    def choose_basket_target(self, spread: float, current_position: int) -> int:
        """
        Decide what basket position we want based on the current spread.

        Positive spread means the basket is expensive versus its constituents.
        Negative spread means the basket is cheap versus its constituents.
        """
        # If we are already long, keep the long until the spread has recovered.
        if current_position > 0:
            if spread >= -EXIT_THRESHOLD:
                return 0
            return TARGET_BASKET_POSITION

        # If we are already short, keep the short until the spread has recovered.
        if current_position < 0:
            if spread <= EXIT_THRESHOLD:
                return 0
            return -TARGET_BASKET_POSITION

        # If we are flat, only enter when the spread is clearly wide enough.
        if spread <= -ENTRY_THRESHOLD:
            return TARGET_BASKET_POSITION
        if spread >= ENTRY_THRESHOLD:
            return -TARGET_BASKET_POSITION
        return 0

    def make_order_toward_target(
        self,
        product: str,
        current_position: int,
        target_position: int,
        order_depth: OrderDepth,
    ) -> List[Order]:
        """
        Move the current position toward the target using the best available
        price on the opposite side of the book.
        """
        orders: List[Order] = []
        desired_volume = take_volume_to_target(current_position, target_position)
        desired_volume = capped_volume(product, desired_volume, current_position)

        if desired_volume == 0:
            return orders

        best_bid, best_ask = best_bid_ask(order_depth)

        # Buy into the best ask, sell into the best bid.
        if desired_volume > 0 and best_ask is not None:
            orders.append(Order(product, best_ask, desired_volume))
        elif desired_volume < 0 and best_bid is not None:
            orders.append(Order(product, best_bid, desired_volume))

        return orders

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        trader_data = "LESSON1_PICNIC_BASKET1"
        conversions = 0

        # We only trade if the basket and all three constituents are visible.
        required_products = [BASKET, CROISSANTS, JAMS, DJEMBES]
        if any(product not in state.order_depths for product in required_products):
            return result, conversions, trader_data

        basket_depth = state.order_depths[BASKET]
        basket_mid = midpoint(basket_depth)
        synthetic_mid = self.synthetic_fair_value(state)

        if basket_mid is None or synthetic_mid is None:
            return result, conversions, trader_data

        # Spread = market basket price - synthetic value from constituents.
        # Positive spread: basket expensive.
        # Negative spread: basket cheap.
        spread = basket_mid - synthetic_mid

        basket_position = state.position.get(BASKET, 0)
        basket_target = self.choose_basket_target(spread, basket_position)

        # ---------------------------------------------------------------------
        # BASKET TRADING
        # ---------------------------------------------------------------------
        # If the basket is expensive, we short it.
        # If the basket is cheap, we buy it.
        # If the spread has normalised, we flatten.
        # ---------------------------------------------------------------------
        basket_orders = self.make_order_toward_target(
            BASKET,
            basket_position,
            basket_target,
            basket_depth,
        )
        if basket_orders:
            result[BASKET] = basket_orders

        # ---------------------------------------------------------------------
        # SIMPLE HEDGE IN THE CONSTITUENTS
        # ---------------------------------------------------------------------
        # A long basket is economically similar to:
        #   long basket, short 6 croissants, short 3 jams, short 1 djembe.
        #
        # We keep this hedge intentionally simple by targeting the opposite
        # synthetic exposure of the basket position.
        # ---------------------------------------------------------------------
        for product, weight in CONSTITUENT_WEIGHTS.items():
            depth = state.order_depths[product]
            current_position = state.position.get(product, 0)
            target_position = -basket_target * weight

            orders = self.make_order_toward_target(
                product,
                current_position,
                target_position,
                depth,
            )

            if orders:
                result[product] = orders

        return result, conversions, trader_data
