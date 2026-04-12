# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 3 - CROISSANTS: A KEY ETF COMPONENT WITH A DIRECTIONAL SIGNAL
# =============================================================================
#
# WHAT THIS LESSON IS FOR
# -----------------------
# CROISSANTS is not a stand-alone "mystery price" product.
# It is one of the main building blocks of the picnic baskets.
#
# That matters because an ETF-like basket gives us extra information:
#   - If the basket becomes expensive, one of its components may be cheap.
#   - If the basket becomes cheap, one of its components may be expensive.
#
# In other words, CROISSANTS can be traded by looking at the basket, not just
# by looking at CROISSANTS itself.
#
# This lesson also shows a second idea:
#   - If the market prints trades from an informed trader like "Olivia",
#     that can bias our CROISSANTS trades up or down.
#
# The goal here is learning, not completeness.
# So the code below is deliberately small, direct, and heavily commented.
#
# =============================================================================

from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional


class Trader:
    # CROISSANTS position limit from the round summary.
    POSITION_LIMIT = 250

    # These are the basket formulas from the notes.
    # PICNIC_BASKET1 = 6 CROISSANTS + 3 JAMS + 1 DJEMBES
    # PICNIC_BASKET2 = 4 CROISSANTS + 2 JAMS
    BASKET_1 = {"CROISSANTS": 6, "JAMS": 3, "DJEMBES": 1}
    BASKET_2 = {"CROISSANTS": 4, "JAMS": 2}

    def mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # A simple fair-value guess: midpoint between best bid and best ask.
        # If one side is missing, we cannot compute a clean mid.
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) / 2

    def implied_croissants_from_basket_1(self, state: TradingState) -> Optional[float]:
        # If we know the basket price and the other components' prices,
        # we can infer what CROISSANTS is "worth" inside the basket.
        required = ["PICNIC_BASKET1", "JAMS", "DJEMBES"]
        if any(product not in state.order_depths for product in required):
            return None

        basket_mid = self.mid_price(state.order_depths["PICNIC_BASKET1"])
        jams_mid = self.mid_price(state.order_depths["JAMS"])
        djembes_mid = self.mid_price(state.order_depths["DJEMBES"])

        if basket_mid is None or jams_mid is None or djembes_mid is None:
            return None

        # Rearranged basket equation:
        #   basket = 6*CROISSANTS + 3*JAMS + 1*DJEMBES
        #   CROISSANTS = (basket - 3*JAMS - 1*DJEMBES) / 6
        return (basket_mid - 3 * jams_mid - djembes_mid) / 6

    def implied_croissants_from_basket_2(self, state: TradingState) -> Optional[float]:
        required = ["PICNIC_BASKET2", "JAMS"]
        if any(product not in state.order_depths for product in required):
            return None

        basket_mid = self.mid_price(state.order_depths["PICNIC_BASKET2"])
        jams_mid = self.mid_price(state.order_depths["JAMS"])

        if basket_mid is None or jams_mid is None:
            return None

        # Rearranged basket equation:
        #   basket = 4*CROISSANTS + 2*JAMS
        #   CROISSANTS = (basket - 2*JAMS) / 4
        return (basket_mid - 2 * jams_mid) / 4

    def estimate_fair_value(self, state: TradingState) -> float:
        # Start with any basket-implied croissant prices we can compute.
        estimates: List[float] = []

        basket_1_value = self.implied_croissants_from_basket_1(state)
        basket_2_value = self.implied_croissants_from_basket_2(state)

        if basket_1_value is not None:
            estimates.append(basket_1_value)
        if basket_2_value is not None:
            estimates.append(basket_2_value)

        # If we have no basket information, fall back to CROISSANTS' own mid.
        if not estimates:
            croissants_book = state.order_depths["CROISSANTS"]
            croissants_mid = self.mid_price(croissants_book)
            if croissants_mid is not None:
                return croissants_mid
            # Absolute last resort: use the best bid/ask if we have only one side.
            if croissants_book.buy_orders and croissants_book.sell_orders:
                return (max(croissants_book.buy_orders) + min(croissants_book.sell_orders)) / 2
            if croissants_book.buy_orders:
                return float(max(croissants_book.buy_orders))
            return float(min(croissants_book.sell_orders))

        # Average the basket-based estimates.
        return sum(estimates) / len(estimates)

    def olivia_signal(self, state: TradingState) -> int:
        # If Olivia is buying CROISSANTS, we treat that as bullish.
        # If Olivia is selling CROISSANTS, we treat that as bearish.
        #
        # This is intentionally simple:
        #   +1 = bullish bias
        #   -1 = bearish bias
        #    0 = no signal
        trades = state.market_trades.get("CROISSANTS", [])
        net_volume = 0

        for trade in trades:
            if trade.buyer == "Olivia":
                net_volume += trade.quantity
            if trade.seller == "Olivia":
                net_volume -= trade.quantity

        if net_volume > 0:
            return 1
        if net_volume < 0:
            return -1
        return 0

    def run(self, state: TradingState):
        # We only trade CROISSANTS in this lesson.
        result: Dict[str, List[Order]] = {}
        product = "CROISSANTS"

        if product not in state.order_depths:
            return result, 0, ""

        order_depth = state.order_depths[product]
        current_position = state.position.get(product, 0)

        # Room to buy and sell before hitting the position limit.
        buy_room = max(self.POSITION_LIMIT - current_position, 0)
        sell_room = max(self.POSITION_LIMIT + current_position, 0)

        # Step 1: estimate a fair value from the baskets.
        fair_value = self.estimate_fair_value(state)

        # Step 2: bias that fair value using Olivia's prints.
        #
        # The key lesson:
        #   - If Olivia is buying, we lean a little more bullish.
        #   - If Olivia is selling, we lean a little more bearish.
        # We are not blindly copying her trade.
        # We are nudging our pricing in her direction.
        signal = self.olivia_signal(state)
        fair_value += signal * 1.0

        print(
            f"[t={state.timestamp}] CROISSANTS | pos={current_position} | "
            f"fair={fair_value:.2f} | signal={signal}"
        )

        orders: List[Order] = []

        # Step 3: take obvious mispricings first.
        #
        # If the best ask is cheaper than our fair value, buy it.
        if order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            if best_ask <= fair_value - 1 and buy_room > 0:
                available = abs(order_depth.sell_orders[best_ask])
                buy_qty = min(buy_room, available)
                if buy_qty > 0:
                    orders.append(Order(product, best_ask, buy_qty))
                    buy_room -= buy_qty
                    print(f"  buy {buy_qty} @ {best_ask}")

        # If the best bid is richer than our fair value, sell into it.
        if order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            if best_bid >= fair_value + 1 and sell_room > 0:
                available = order_depth.buy_orders[best_bid]
                sell_qty = min(sell_room, available)
                if sell_qty > 0:
                    orders.append(Order(product, best_bid, -sell_qty))
                    sell_room -= sell_qty
                    print(f"  sell {sell_qty} @ {best_bid}")

        # Step 4: if nothing was crossed, place a tiny passive quote.
        #
        # This is the simplest form of market making:
        #   - bid slightly below fair value
        #   - ask slightly above fair value
        #
        # The Olivia signal already shifts the fair value.
        if not orders:
            bid_price = int(fair_value) - 1
            ask_price = int(fair_value) + 1

            # Keep the quote size small so the lesson stays easy to follow.
            quote_size = 5

            if buy_room > 0:
                orders.append(Order(product, bid_price, min(quote_size, buy_room)))
            if sell_room > 0:
                orders.append(Order(product, ask_price, -min(quote_size, sell_room)))

        result[product] = orders
        return result, 0, ""
