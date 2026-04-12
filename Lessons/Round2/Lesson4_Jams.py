# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 4 - JAMS: THE PICNIC BASKET INGREDIENT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson shows how to think about JAMS inside the Picnic Basket products.
#
# In Round 2, JAMS is not a standalone "mystery price" product.
# It is one of the ingredients that builds the picnic baskets:
#
#   PICNIC_BASKET1 = 6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES
#   PICNIC_BASKET2 = 4 * CROISSANTS + 2 * JAMS
#
# That means JAMS can be studied in two ways:
#   1. Directly from its own order book.
#   2. Indirectly from the baskets that contain it.
#
# This lesson uses a simple helper strategy:
#   - look at the baskets and the other ingredients
#   - back out an implied fair value for JAMS
#   - buy JAMS when it is cheap
#   - sell JAMS when it is expensive
#
# The goal is not to be fancy.
# The goal is to be readable, beginner-friendly, and easy to modify.
#
# =============================================================================

from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional


# -----------------------------------------------------------------------------
# POSITION LIMITS
# -----------------------------------------------------------------------------
# These are the maximum absolute positions we want to hold.
# The exact limits are competition-specific, but keeping them in one place
# makes the code easier to read and adjust.
# -----------------------------------------------------------------------------
POSITION_LIMITS = {
    "CROISSANTS": 250,
    "JAMS": 350,
    "DJEMBES": 60,
    "PICNIC_BASKET1": 60,
    "PICNIC_BASKET2": 100,
}


# -----------------------------------------------------------------------------
# BASKET COMPOSITION
# -----------------------------------------------------------------------------
# These numbers tell us how many of each ingredient make up each basket.
# We use them in reverse to estimate the price of JAMS.
# -----------------------------------------------------------------------------
BASKET1_WEIGHTS = {"CROISSANTS": 6, "JAMS": 3, "DJEMBES": 1}
BASKET2_WEIGHTS = {"CROISSANTS": 4, "JAMS": 2}


def best_bid_ask(order_depth: OrderDepth) -> tuple[Optional[int], Optional[int]]:
    """Return the best bid and best ask from the current order book."""

    best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
    best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
    return best_bid, best_ask


def mid_price(order_depth: OrderDepth) -> Optional[float]:
    """Return the simple midpoint of the best bid and best ask."""

    best_bid, best_ask = best_bid_ask(order_depth)

    if best_bid is None or best_ask is None:
        return None

    return (best_bid + best_ask) / 2


def available_buy_volume(order_depth: OrderDepth, price: int) -> int:
    """Sell-side volume is stored as negative numbers, so we use abs()."""

    return abs(order_depth.sell_orders.get(price, 0))


def available_sell_volume(order_depth: OrderDepth, price: int) -> int:
    """Buy-side volume is already positive."""

    return order_depth.buy_orders.get(price, 0)


def trade_around_fair_value(
    product: str,
    order_depth: OrderDepth,
    fair_value: int,
    current_position: int,
) -> List[Order]:
    """Very small market-making helper.

    The idea is simple:
    - buy cheap asks below fair value
    - sell expensive bids above fair value
    - then place one passive buy and one passive sell near fair value

    This keeps the lesson focused on the idea rather than on a large amount
    of trading infrastructure.
    """

    orders: List[Order] = []
    limit = POSITION_LIMITS.get(product, 0)

    # How much room do we have left?
    remaining_buy = limit - current_position
    remaining_sell = limit + current_position

    # -------------------------------------------------------------------------
    # STEP 1: TAKE OBVIOUS EDGE
    # -------------------------------------------------------------------------
    # If someone is offering to sell below fair value, buy from them.
    # If someone is bidding above fair value, sell to them.
    # -------------------------------------------------------------------------
    if order_depth.sell_orders:
        best_ask = min(order_depth.sell_orders)
        if best_ask <= fair_value - 1 and remaining_buy > 0:
            buy_size = min(remaining_buy, available_buy_volume(order_depth, best_ask))
            if buy_size > 0:
                orders.append(Order(product, best_ask, buy_size))
                remaining_buy -= buy_size

    if order_depth.buy_orders:
        best_bid = max(order_depth.buy_orders)
        if best_bid >= fair_value + 1 and remaining_sell > 0:
            sell_size = min(remaining_sell, available_sell_volume(order_depth, best_bid))
            if sell_size > 0:
                orders.append(Order(product, best_bid, -sell_size))
                remaining_sell -= sell_size

    # -------------------------------------------------------------------------
    # STEP 2: PLACE SMALL PASSIVE QUOTES
    # -------------------------------------------------------------------------
    # A simple beginner-friendly rule:
    # - bid one tick below fair value
    # - ask one tick above fair value
    #
    # This is enough to show the market-making idea without adding lots of
    # extra logic or risk management machinery.
    # -------------------------------------------------------------------------
    if remaining_buy > 0:
        orders.append(Order(product, fair_value - 1, remaining_buy))

    if remaining_sell > 0:
        orders.append(Order(product, fair_value + 1, -remaining_sell))

    return orders


def estimate_jams_fair_value(order_depths: Dict[str, OrderDepth]) -> int:
    """Estimate JAMS fair value from the baskets that contain it.

    We back out the implied JAMS price from the basket order books:

        PICNIC_BASKET1 = 6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES
        PICNIC_BASKET2 = 4 * CROISSANTS + 2 * JAMS

    Rearranging gives:

        JAMS = (basket1 - 6*croissants - djembes) / 3
        JAMS = (basket2 - 4*croissants) / 2

    We average every estimate we can compute.
    If the baskets are missing, we fall back to the direct JAMS midpoint.
    """

    jams_book = order_depths.get("JAMS")
    croissants_book = order_depths.get("CROISSANTS")
    djembes_book = order_depths.get("DJEMBES")
    basket1_book = order_depths.get("PICNIC_BASKET1")
    basket2_book = order_depths.get("PICNIC_BASKET2")

    estimates: List[float] = []

    jams_mid = mid_price(jams_book) if jams_book is not None else None
    croissants_mid = mid_price(croissants_book) if croissants_book is not None else None
    djembes_mid = mid_price(djembes_book) if djembes_book is not None else None
    basket1_mid = mid_price(basket1_book) if basket1_book is not None else None
    basket2_mid = mid_price(basket2_book) if basket2_book is not None else None

    if basket1_mid is not None and croissants_mid is not None and djembes_mid is not None:
        jams_from_basket1 = (basket1_mid - 6 * croissants_mid - djembes_mid) / 3
        estimates.append(jams_from_basket1)

    if basket2_mid is not None and croissants_mid is not None:
        jams_from_basket2 = (basket2_mid - 4 * croissants_mid) / 2
        estimates.append(jams_from_basket2)

    if estimates:
        return int(round(sum(estimates) / len(estimates)))

    if jams_mid is not None:
        return int(round(jams_mid))

    # Very last fallback: if we have no book at all, use a neutral value.
    return 0


def estimate_basket_fair_value(
    basket_name: str,
    order_depths: Dict[str, OrderDepth],
    jams_fair_value: int,
) -> Optional[int]:
    """Estimate a basket fair value from its ingredients.

    This is the same idea as above, but used in the forward direction:
    instead of solving for JAMS, we build the basket from the ingredients.
    """

    croissants_book = order_depths.get("CROISSANTS")
    djembes_book = order_depths.get("DJEMBES")

    croissants_mid = mid_price(croissants_book) if croissants_book is not None else None
    djembes_mid = mid_price(djembes_book) if djembes_book is not None else None

    if basket_name == "PICNIC_BASKET1":
        if croissants_mid is None or djembes_mid is None:
            return None
        return int(round(6 * croissants_mid + 3 * jams_fair_value + djembes_mid))

    if basket_name == "PICNIC_BASKET2":
        if croissants_mid is None:
            return None
        return int(round(4 * croissants_mid + 2 * jams_fair_value))

    return None


class Trader:
    def run(self, state: TradingState):
        # ---------------------------------------------------------------------
        # 'state' is the full snapshot of the market for this tick.
        # We will read the order books, estimate fair values, and return orders.
        # ---------------------------------------------------------------------
        result: Dict[str, List[Order]] = {}

        # JAMS is the main character of this lesson.
        jams_book = state.order_depths.get("JAMS")
        if jams_book is None:
            return result, 1, "LESSON4_JAMS"

        jams_position = state.position.get("JAMS", 0)
        jams_fair_value = estimate_jams_fair_value(state.order_depths)

        print(
            f"[t={state.timestamp}] JAMS fair value = {jams_fair_value} | "
            f"position = {jams_position}"
        )

        # First, trade JAMS itself using the fair value we estimated from
        # the basket ingredients.
        result["JAMS"] = trade_around_fair_value(
            "JAMS",
            jams_book,
            jams_fair_value,
            jams_position,
        )

        # Then, if the basket books are present, use the same helper logic
        # to trade the baskets around the synthetic value implied by JAMS.
        for basket_name in ["PICNIC_BASKET1", "PICNIC_BASKET2"]:
            basket_book = state.order_depths.get(basket_name)
            if basket_book is None:
                continue

            basket_fair_value = estimate_basket_fair_value(
                basket_name,
                state.order_depths,
                jams_fair_value,
            )

            if basket_fair_value is None:
                continue

            basket_position = state.position.get(basket_name, 0)
            print(
                f"[t={state.timestamp}] {basket_name} fair value = {basket_fair_value} | "
                f"position = {basket_position}"
            )

            result[basket_name] = trade_around_fair_value(
                basket_name,
                basket_book,
                basket_fair_value,
                basket_position,
            )

        # We keep conversions at 1 here because this lesson is about baskets,
        # not about cross-exchange conversion logic.
        conversions = 1
        trader_data = "LESSON4_JAMS"

        return result, conversions, trader_data
