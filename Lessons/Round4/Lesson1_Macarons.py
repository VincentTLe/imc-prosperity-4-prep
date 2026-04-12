# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 1 - MAGNIFICENT MACARONS: LOCAL VS EXTERNAL MARKET ARBITRAGE
# =============================================================================
#
# WHAT THIS LESSON IS FOR
# -----------------------
# Magnificent Macarons is the first Round 4 product that teaches a new idea:
# you are no longer trading in just one market.
#
# Instead, you have:
#   1. A local island order book
#   2. An external market with its own bid and ask
#   3. Conversion costs for moving inventory between the two
#
# That means the real question is not just:
#   "Is this local price cheap or expensive?"
#
# The real question is:
#   "Is this local price cheap or expensive compared to the external market
#    after I include transport fees and tariffs?"
#
# THE THREE CORE IDEAS
# ---------------------
# 1. Local vs external market
#    - Local market: the normal order book in TradingState.order_depths
#    - External market: the conversion observation in state.observations
#
# 2. Conversion costs
#    - transportFees, importTariff, and exportTariff all reduce the edge
#    - you must beat those costs before an arbitrage trade is profitable
#
# 3. Long vs short arbitrage
#    - Long arbitrage: buy locally when local ask is below external value
#    - Short arbitrage: sell locally when local bid is above external cost
#
# This lesson keeps the strategy deliberately simple:
#   - compute the adjusted external prices
#   - compare them to the local best bid / ask
#   - trade only when there is positive edge
#   - use conversions in the safest possible beginner-friendly way
# =============================================================================

import math
from datamodel import Order, OrderDepth, TradingState
from typing import List, Optional, Tuple


class Trader:
    # =========================================================================
    # SIMPLE LESSON CONSTANTS
    # =========================================================================
    # The round limit for Magnificent Macarons is 75 units.
    POSITION_LIMIT = 75

    # The round also gives a conversion limit of 10 units per timestep.
    # We keep the lesson conservative and never exceed that limit.
    CONVERSION_LIMIT = 10

    # Keep the example small and readable.
    ORDER_SIZE = 10

    COMMODITY_SYMBOL = "MAGNIFICENT_MACARONS"

    def best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest price in the buy book.
        # Best ask = lowest price in the sell book.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def conversion_prices(self, order_depth: OrderDepth, state: TradingState):
        # If the external market observation is missing, we cannot compute a
        # clean arbitrage edge.
        if self.COMMODITY_SYMBOL not in state.observations.conversionObservations:
            return None

        conv_obs = state.observations.conversionObservations[self.COMMODITY_SYMBOL]

        # The external market itself has a bid and ask.
        external_bid = conv_obs.bidPrice
        external_ask = conv_obs.askPrice

        # Moving goods across markets is not free.
        # We must pay:
        #   - transportFees
        #   - exportTariff if we send inventory outward
        #   - importTariff if we bring inventory inward
        transport_fees = conv_obs.transportFees
        export_tariff = conv_obs.exportTariff
        import_tariff = conv_obs.importTariff

        # Price we effectively receive if we sell to the external market.
        # This is the external bid minus the costs of exporting the product.
        external_sell_value = external_bid - export_tariff - transport_fees

        # Price we effectively pay if we buy from the external market.
        # This is the external ask plus the costs of importing the product.
        external_buy_cost = external_ask + import_tariff + transport_fees

        return conv_obs, external_sell_value, external_buy_cost

    def clamp_conversions(self, target: int) -> int:
        # Conversions are limited per timestep.
        # We clamp the requested amount so the order is always legal.
        return max(min(target, self.CONVERSION_LIMIT), -self.CONVERSION_LIMIT)

    def run(self, state: TradingState):
        # The engine expects exactly three return values:
        #   1. result      -> our orders by product
        #   2. conversions -> how many units we want to convert
        #   3. traderData  -> a string we can carry to the next tick
        result = {}
        conversions = 0

        for product in state.order_depths:
            orders: List[Order] = []

            # This lesson only trades Magnificent Macarons.
            if product != self.COMMODITY_SYMBOL:
                result[product] = orders
                continue

            order_depth: OrderDepth = state.order_depths[product]
            current_position = state.position.get(product, 0)

            best_bid, best_ask = self.best_bid_ask(order_depth)
            info = self.conversion_prices(order_depth, state)

            # If we cannot see both markets, stay flat and do nothing.
            if info is None or best_bid is None or best_ask is None:
                result[product] = orders
                continue

            conv_obs, external_sell_value, external_buy_cost = info

            # Local market prices:
            #   best_bid = highest local buy price
            #   best_ask = lowest local sell price
            #
            # We compare those to the adjusted external prices after fees.
            long_arbitrage = external_sell_value - best_ask
            short_arbitrage = best_bid - external_buy_cost

            # Position room tells us how much inventory we can still take.
            room_to_buy = max(0, self.POSITION_LIMIT - current_position)
            room_to_sell = max(0, self.POSITION_LIMIT + current_position)

            print(
                f"[t={state.timestamp}] {product} | pos={current_position} | "
                f"local_bid={best_bid} | local_ask={best_ask} | "
                f"ext_sell={external_sell_value:.1f} | ext_buy={external_buy_cost:.1f} | "
                f"long_edge={long_arbitrage:.1f} | short_edge={short_arbitrage:.1f}"
            )

            # =================================================================
            # 1. LONG ARBITRAGE
            # =================================================================
            # If the external market is rich enough after costs, the local ask
            # is too cheap.
            #
            # That means:
            #   - buy locally
            #   - hold the product as a long position
            #   - use conversions to move inventory across markets when needed
            #
            # In this lesson we keep it simple and only take the best local ask.
            if long_arbitrage > 0 and best_ask is not None and room_to_buy > 0:
                available_volume = abs(order_depth.sell_orders[best_ask])
                buy_volume = min(self.ORDER_SIZE, room_to_buy, available_volume)

                if buy_volume > 0:
                    orders.append(Order(product, best_ask, buy_volume))
                    print(f"  BUY  {buy_volume} @ {best_ask} because local is cheap")

            # =================================================================
            # 2. SHORT ARBITRAGE
            # =================================================================
            # If the external buy cost is low enough after fees, the local bid
            # is too expensive.
            #
            # That means:
            #   - sell locally
            #   - hold the product as a short position
            #   - use conversions to move inventory across markets when needed
            if short_arbitrage > 0 and best_bid is not None and room_to_sell > 0:
                available_volume = order_depth.buy_orders[best_bid]
                sell_volume = min(self.ORDER_SIZE, room_to_sell, available_volume)

                if sell_volume > 0:
                    orders.append(Order(product, best_bid, -sell_volume))
                    print(f"  SELL {sell_volume} @ {best_bid} because local is rich")

            # =================================================================
            # 3. SIMPLE CONVERSION HANDLING
            # =================================================================
            # Conversions are separate from normal orders.
            #
            # A beginner-friendly rule is to use conversions to flatten our
            # inventory back toward zero every tick, while staying inside the
            # round limit.
            #
            # Positive conversions mean we want to move inventory in one
            # direction across the two markets, negative conversions mean the
            # opposite direction. The easiest safe policy is to offset the
            # current position:
            #   long position  -> convert negatively
            #   short position -> convert positively
            #
            # This does not try to be clever. It just shows the mechanism.
            conversions = self.clamp_conversions(-current_position)

            # Store the orders for this product.
            result[product] = orders

        traderData = "LESSON1_MACARONS_BOT_RUNNING"
        return result, conversions, traderData
