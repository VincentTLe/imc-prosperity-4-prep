# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 5 - DJEMBES: READING A CONSTITUENT INSIDE PICNIC_BASKET1
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson shows how to think about DJEMBES inside the Picnic Basket family.
#
# In Round 2, DJEMBES is not an isolated product.
# It is one of the ingredients that make up PICNIC_BASKET1:
#
#   PICNIC_BASKET1 = 6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES
#
# That means DJEMBES has two "prices" we can think about:
#   1. Its own market price in the DJEMBES order book.
#   2. Its implied price inside PICNIC_BASKET1.
#
# If the basket is trading at a price that does not match the sum of its
# ingredients, then one of the pieces is likely mispriced.
# This lesson uses that idea in the simplest possible way:
#   - estimate DJEMBES fair value from the basket and the other ingredients
#   - buy DJEMBES when the market is too cheap
#   - sell DJEMBES when the market is too expensive
#
# The goal is not to be clever.
# The goal is to be clear, readable, and easy to copy into your own notes.
#
# =============================================================================

from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional


# -----------------------------------------------------------------------------
# PRODUCTS
# -----------------------------------------------------------------------------
# We keep the names in one place so the lesson is easy to scan.
# -----------------------------------------------------------------------------
BASKET = "PICNIC_BASKET1"
CROISSANTS = "CROISSANTS"
JAMS = "JAMS"
DJEMBES = "DJEMBES"


# -----------------------------------------------------------------------------
# SIMPLE POSITION LIMITS
# -----------------------------------------------------------------------------
# These are intentionally conservative. The exact values are less important
# than the idea: never send an order that would break the limit.
# -----------------------------------------------------------------------------
POSITION_LIMITS = {
    CROISSANTS: 250,
    JAMS: 350,
    DJEMBES: 60,
    BASKET: 60,
}


def best_bid_ask(order_depth: OrderDepth) -> tuple[Optional[int], Optional[int]]:
    """Return the best bid and best ask from the current order book."""

    best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
    best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
    return best_bid, best_ask


def mid_price(order_depth: OrderDepth) -> Optional[float]:
    """Return a simple midpoint for one order book."""

    best_bid, best_ask = best_bid_ask(order_depth)

    if best_bid is not None and best_ask is not None:
        return (best_bid + best_ask) / 2
    if best_bid is not None:
        return best_bid + 0.5
    if best_ask is not None:
        return best_ask - 0.5
    return None


def estimate_djembes_fair_value(order_depths: Dict[str, OrderDepth]) -> Optional[int]:
    """
    Estimate DJEMBES fair value from PICNIC_BASKET1.

    Rearranging the basket formula gives:

        DJEMBES = PICNIC_BASKET1 - 6 * CROISSANTS - 3 * JAMS

    We use the mid price of each visible book as a beginner-friendly proxy.
    """

    basket_book = order_depths.get(BASKET)
    croissants_book = order_depths.get(CROISSANTS)
    jams_book = order_depths.get(JAMS)

    basket_mid = mid_price(basket_book) if basket_book is not None else None
    croissants_mid = mid_price(croissants_book) if croissants_book is not None else None
    jams_mid = mid_price(jams_book) if jams_book is not None else None

    # We need the basket and both other ingredients to back out DJEMBES.
    if basket_mid is None or croissants_mid is None or jams_mid is None:
        return None

    implied_djembes = basket_mid - 6 * croissants_mid - 3 * jams_mid
    return int(round(implied_djembes))


def trade_toward_fair_value(
    product: str,
    order_depth: OrderDepth,
    fair_value: int,
    current_position: int,
) -> List[Order]:
    """
    Very small helper that trades around a fair value estimate.

    The logic is simple:
      - buy asks below fair value
      - sell bids above fair value
      - keep a small passive quote near fair value if room remains

    This is enough to show the idea without adding a lot of strategy code.
    """

    orders: List[Order] = []
    limit = POSITION_LIMITS.get(product, 0)

    remaining_buy = limit - current_position
    remaining_sell = limit + current_position

    # -------------------------------------------------------------------------
    # STEP 1 - TAKE OBVIOUS EDGE
    # -------------------------------------------------------------------------
    # If someone is offering to sell DJEMBES well below our estimate, buy it.
    # If someone is bidding well above our estimate, sell into that bid.
    # -------------------------------------------------------------------------
    if order_depth.sell_orders:
        best_ask = min(order_depth.sell_orders)
        if best_ask <= fair_value - 1 and remaining_buy > 0:
            available_volume = abs(order_depth.sell_orders[best_ask])
            buy_size = min(remaining_buy, available_volume)
            if buy_size > 0:
                orders.append(Order(product, best_ask, buy_size))
                remaining_buy -= buy_size

    if order_depth.buy_orders:
        best_bid = max(order_depth.buy_orders)
        if best_bid >= fair_value + 1 and remaining_sell > 0:
            available_volume = order_depth.buy_orders[best_bid]
            sell_size = min(remaining_sell, available_volume)
            if sell_size > 0:
                orders.append(Order(product, best_bid, -sell_size))
                remaining_sell -= sell_size

    # -------------------------------------------------------------------------
    # STEP 2 - POST SMALL PASSIVE ORDERS
    # -------------------------------------------------------------------------
    # We use one-tick quotes around fair value.
    # This keeps the lesson beginner-friendly and shows the market-making idea.
    # -------------------------------------------------------------------------
    if remaining_buy > 0:
        orders.append(Order(product, fair_value - 1, remaining_buy))

    if remaining_sell > 0:
        orders.append(Order(product, fair_value + 1, -remaining_sell))

    return orders


class Trader:
    def run(self, state: TradingState):
        # ---------------------------------------------------------------------
        # 'state' is the full snapshot of the market for this tick.
        # We read the books, estimate DJEMBES fair value, and return orders.
        # ---------------------------------------------------------------------
        result: Dict[str, List[Order]] = {}

        djembes_book = state.order_depths.get(DJEMBES)
        if djembes_book is None:
            return result, 1, "LESSON5_DJEMBES"

        # DJEMBES is the star of this lesson.
        djembes_position = state.position.get(DJEMBES, 0)
        djembes_fair_value = estimate_djembes_fair_value(state.order_depths)

        if djembes_fair_value is None:
            return result, 1, "LESSON5_DJEMBES"

        print(
            f"[t={state.timestamp}] DJEMBES fair value = {djembes_fair_value} | "
            f"position = {djembes_position}"
        )

        # ---------------------------------------------------------------------
        # TRADE DJEMBES FROM ITS IMPLIED VALUE
        # ---------------------------------------------------------------------
        # If the basket says DJEMBES should be worth more than the market,
        # we buy DJEMBES.
        # If the basket says DJEMBES should be worth less, we sell DJEMBES.
        # ---------------------------------------------------------------------
        result[DJEMBES] = trade_toward_fair_value(
            DJEMBES,
            djembes_book,
            djembes_fair_value,
            djembes_position,
        )

        # ---------------------------------------------------------------------
        # OPTIONAL TEACHING HOOK: LOOK AT THE BASKET TOO
        # ---------------------------------------------------------------------
        # We do not need to trade the basket in this lesson.
        # But printing its synthetic value makes the relationship visible.
        # ---------------------------------------------------------------------
        basket_book = state.order_depths.get(BASKET)
        if basket_book is not None:
            basket_mid = mid_price(basket_book)
            croissants_mid = mid_price(state.order_depths.get(CROISSANTS))
            jams_mid = mid_price(state.order_depths.get(JAMS))

            if basket_mid is not None and croissants_mid is not None and jams_mid is not None:
                synthetic_basket = 6 * croissants_mid + 3 * jams_mid + djembes_fair_value
                spread = basket_mid - synthetic_basket
                print(
                    f"[t={state.timestamp}] PICNIC_BASKET1 mid = {basket_mid:.1f} | "
                    f"synthetic = {synthetic_basket:.1f} | spread = {spread:.1f}"
                )

        # We keep conversions at 1 here because this lesson is about reading the
        # basket relationship, not about cross-exchange conversion logic.
        conversions = 1
        trader_data = "LESSON5_DJEMBES"

        return result, conversions, trader_data
