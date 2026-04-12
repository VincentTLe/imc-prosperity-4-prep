# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 2 - KELP: YOUR FIRST "MOVING FAIR VALUE" TRADING BOT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson is the next step after RAINFOREST_RESIN.
# Resin had a fixed fair value of 10,000, so the only hard part was learning
# how to read the order book and trade around that number.
#
# KELP is slightly harder because the fair value moves over time.
# The key lesson is:
#   - do not hardcode one magic price
#   - re-estimate fair value every tick
#   - then trade around that estimate in a simple, disciplined way
#
# THE BIG IDEA
# ------------
# Frankfurt Hedgehogs used a very teachable KELP strategy:
#   1. Estimate fair value from the order book "wall mid"
#   2. Take cheap asks and expensive bids immediately
#   3. Make passive quotes one tick inside the book
#   4. Reduce aggressiveness when inventory gets too large
#
# This version keeps that structure, but strips it down so the logic is easy to
# read and easy to modify.
# =============================================================================

from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional, Tuple


class Trader:
    # =========================================================================
    # SIMPLE CONSTANTS
    # =========================================================================
    # POSITION_LIMIT:
    #   KELP allows us to hold at most +50 or -50 units.
    #
    # TAKE_EDGE:
    #   We only take orders when they are clearly better than fair value by at
    #   least 1 tick.
    #
    # FLATTEN_LEVEL:
    #   If inventory gets too large, we stop leaning harder into that side.
    # =========================================================================
    POSITION_LIMIT = 50
    TAKE_EDGE = 1
    FLATTEN_LEVEL = 40

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest buy price currently in the book.
        # Best ask = lowest sell price currently in the book.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _wall_mid(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[float], Optional[int]]:
        # Frankfurt Hedgehogs used a simple "wall mid" estimate:
        #   bid wall = the lowest buy price in the visible book
        #   ask wall = the highest sell price in the visible book
        #
        # Averaging those two prices gives a smooth fair value estimate that
        # moves with the order book instead of staying fixed.
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None, None, None

        bid_wall = min(order_depth.buy_orders.keys())
        ask_wall = max(order_depth.sell_orders.keys())
        fair_value = (bid_wall + ask_wall) / 2
        return bid_wall, fair_value, ask_wall

    def run(self, state: TradingState):
        # The engine expects:
        #   1. result      -> our orders by product
        #   2. conversions -> not used in this round
        #   3. traderData  -> a string we can keep for future ticks
        result = {}

        # We loop over all products, but only trade KELP in this lesson.
        for product in state.order_depths:
            orders: List[Order] = []

            if product != "KELP":
                result[product] = orders
                continue

            order_depth: OrderDepth = state.order_depths[product]
            current_position = state.position.get(product, 0)

            best_bid, best_ask = self._best_bid_ask(order_depth)
            bid_wall, fair_value, ask_wall = self._wall_mid(order_depth)

            # If we cannot estimate fair value, do nothing this tick.
            if fair_value is None or bid_wall is None or ask_wall is None:
                result[product] = orders
                continue

            # Remaining capacity before we hit the position limit.
            remaining_buy_capacity = max(0, self.POSITION_LIMIT - current_position)
            remaining_sell_capacity = max(0, self.POSITION_LIMIT + current_position)

            print(
                f"[t={state.timestamp}] {product} | "
                f"pos={current_position} | "
                f"fair={fair_value:.1f} | "
                f"best_bid={best_bid} | best_ask={best_ask} | "
                f"bid_wall={bid_wall} | ask_wall={ask_wall}"
            )

            # =================================================================
            # 1. FAIR VALUE
            # =================================================================
            # KELP does not have a fixed price like Resin.
            # We re-estimate the fair price every tick using wall_mid.
            #
            # The strategy below assumes:
            #   - prices below fair_value are cheap
            #   - prices above fair_value are expensive
            # =================================================================

            # =================================================================
            # 2. TAKING
            # =================================================================
            # "Taking" means hitting existing orders in the book right away.
            # This is the aggressive part of the strategy.
            #
            # Buy when the cheapest ask is clearly below fair value.
            if best_ask is not None and best_ask <= fair_value - self.TAKE_EDGE:
                available_volume = abs(order_depth.sell_orders[best_ask])
                buy_volume = min(remaining_buy_capacity, available_volume)

                if buy_volume > 0:
                    orders.append(Order(product, best_ask, buy_volume))
                    remaining_buy_capacity -= buy_volume

            # Sell when the best bid is clearly above fair value.
            if best_bid is not None and best_bid >= fair_value + self.TAKE_EDGE:
                available_volume = order_depth.buy_orders[best_bid]
                sell_volume = min(remaining_sell_capacity, available_volume)

                if sell_volume > 0:
                    orders.append(Order(product, best_bid, -sell_volume))
                    remaining_sell_capacity -= sell_volume

            # =================================================================
            # 3. INVENTORY CONTROL
            # =================================================================
            # If inventory gets too large, we stop leaning harder in that same
            # direction. This is the beginner-friendly version of flattening.
            #
            # If we are already quite long, stop placing new buy orders.
            # If we are already quite short, stop placing new sell orders.
            if current_position >= self.FLATTEN_LEVEL:
                remaining_buy_capacity = 0
            if current_position <= -self.FLATTEN_LEVEL:
                remaining_sell_capacity = 0

            # =================================================================
            # 4. MAKING
            # =================================================================
            # "Making" means posting passive orders around fair value.
            # This is how we earn spread when nobody is offering us a better deal.
            #
            # The simple Frankfurt-style idea:
            #   - bid one tick above the bid wall
            #   - ask one tick below the ask wall
            #   - stay close to fair value, but do not cross it blindly

            bid_price = bid_wall + 1
            ask_price = ask_wall - 1

            # If the current best bid is still below fair value, we can improve
            # it by one tick and still remain conservative.
            if best_bid is not None and best_bid + 1 < fair_value:
                bid_price = max(bid_price, best_bid + 1)

            # If the current best ask is still above fair value, we can improve
            # it by one tick and still stay on the safe side.
            if best_ask is not None and best_ask - 1 > fair_value:
                ask_price = min(ask_price, best_ask - 1)

            if remaining_buy_capacity > 0:
                orders.append(Order(product, int(bid_price), remaining_buy_capacity))

            if remaining_sell_capacity > 0:
                orders.append(Order(product, int(ask_price), -remaining_sell_capacity))

            result[product] = orders

        traderData = "LESSON2_KELP_BOT_RUNNING"
        conversions = 0
        return result, conversions, traderData
