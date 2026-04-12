# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 3 - VOLCANIC_ROCK_VOUCHER_9750: YOUR FIRST OPTIONS BOT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson teaches a very beginner-friendly way to think about options.
# We focus on one voucher:
#   - VOLCANIC_ROCK_VOUCHER_9750
#
# The big idea is not "predict the future perfectly".
# The big idea is:
#   1. Estimate what the option should be worth
#   2. Compare that to the market price
#   3. Buy when the market is too cheap
#   4. Sell when the market is too expensive
#
# FRANKFURT HEDGEHOGS CONNECTION
# ------------------------------
# The Frankfurt Hedgehogs writeup/code showed that options could be very
# profitable when you trade around implied volatility (IV).
#
# In plain English:
#   - if the market is pricing the option with too little IV, it is too cheap
#   - if the market is pricing the option with too much IV, it is too expensive
#   - that difference is what people call "IV scalping"
#
# This lesson keeps that idea, but strips it down to a simple teaching version:
#   - use Black-Scholes to estimate fair value
#   - compare market price to our fair value
#   - trade small sizes around that estimate
#
# INTRINSIC VALUE VS EXTRINSIC VALUE
# ----------------------------------
# For a call option:
#   intrinsic value = max(underlying_price - strike_price, 0)
#
# This is the "floor" value of the option.
# If the underlying is already above the strike, the option is in the money.
# If the underlying is below the strike, intrinsic value is zero.
#
# extrinsic value = option_price - intrinsic_value
#
# This is the extra value from time, uncertainty, and future upside.
# Beginners often think "the option price is just the intrinsic value".
# That is wrong. Most of the time, a lot of the option price is extrinsic.
#
# FAIR VALUE INTUITION
# --------------------
# A simple way to think about fair value:
#   fair value = intrinsic value + some reasonable extrinsic value
#
# In this lesson, we use Black-Scholes with a fixed target IV to estimate that
# extrinsic value. We are not trying to be perfect. We are trying to be
# consistent and explain the idea clearly.
#
# SIMPLIFIED IV SCALPING
# ----------------------
# A real IV scalper often:
#   - solves for implied volatility from market prices
#   - compares that IV to a target or model IV
#   - trades when the gap is large enough
#
# We keep it simpler here:
#   - estimate the voucher fair price from the underlying and a target IV
#   - buy the voucher if the market is cheaper than that estimate
#   - sell the voucher if the market is richer than that estimate
#
# That is already a useful first version of IV scalping.
# =============================================================================

import math
from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional, Tuple


class Trader:
    # =========================================================================
    # SIMPLE CONSTANTS
    # =========================================================================
    # PRODUCT_NAME:
    #   The voucher we trade in this lesson.
    #
    # UNDERLYING_NAME:
    #   The stock / asset the voucher is written on.
    #
    # STRIKE_PRICE:
    #   The fixed strike price of the call option.
    #
    # POSITION_LIMIT:
    #   Maximum long or short inventory we allow ourselves to hold.
    #
    # TARGET_IV:
    #   Our teaching version of "model volatility".
    #   We do not try to solve IV every tick here.
    #
    # TAKE_EDGE:
    #   How far away from fair value the market must be before we take it.
    #
    # MAKE_SPREAD:
    #   How far away from fair value we place passive quotes.
    #
    # TRADE_SIZE:
    #   Keep the lesson simple by using a small fixed size.
    # =========================================================================
    PRODUCT_NAME = "VOLCANIC_ROCK_VOUCHER_9750"
    UNDERLYING_NAME = "VOLCANIC_ROCK"
    STRIKE_PRICE = 9750
    POSITION_LIMIT = 200
    TARGET_IV = 0.35
    TIME_TO_EXPIRY = 0.25
    RISK_FREE_RATE = 0.0
    TAKE_EDGE = 8.0
    MAKE_SPREAD = 6.0
    TRADE_SIZE = 20

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest price currently offered by buyers.
        # Best ask = lowest price currently offered by sellers.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # Mid price = average of best bid and best ask.
        # We use this as our simplest estimate of "current market price".
        best_bid, best_ask = self._best_bid_ask(order_depth)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid + best_ask) / 2.0

    def _norm_cdf(self, x: float) -> float:
        # Cumulative normal distribution using math.erf.
        # This is enough for Black-Scholes and keeps the lesson self-contained.
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _black_scholes_call_price(
        self,
        spot: float,
        strike: float,
        time_to_expiry: float,
        rate: float,
        volatility: float,
    ) -> float:
        # Black-Scholes gives us a theoretical call option price.
        # For a beginner lesson, this is the easiest way to turn
        # "underlying price + IV idea" into a fair value estimate.
        if spot <= 0.0:
            return 0.0

        # If time or volatility collapses, the option is basically its intrinsic value.
        if time_to_expiry <= 0.0 or volatility <= 0.0:
            return max(spot - strike, 0.0)

        sqrt_t = math.sqrt(time_to_expiry)
        d1 = (
            math.log(spot / strike)
            + (rate + 0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt_t)
        d2 = d1 - volatility * sqrt_t

        discounted_strike = strike * math.exp(-rate * time_to_expiry)
        return spot * self._norm_cdf(d1) - discounted_strike * self._norm_cdf(d2)

    def _intrinsic_value(self, spot: float) -> float:
        # Intrinsic value is the part of the option that is "already there".
        # For a call: max(spot - strike, 0)
        return max(spot - self.STRIKE_PRICE, 0.0)

    def run(self, state: TradingState):
        # The competition engine expects:
        #   1. result      -> our orders by product
        #   2. conversions -> not used in this lesson
        #   3. traderData  -> a string carried from one tick to the next
        result = {}

        # We loop over all available products, but only trade the voucher here.
        for product in state.order_depths:
            orders: List[Order] = []

            # Leave all non-voucher products untouched.
            if product != self.PRODUCT_NAME:
                result[product] = orders
                continue

            voucher_depth: OrderDepth = state.order_depths[product]
            underlying_depth = state.order_depths.get(self.UNDERLYING_NAME)
            current_position = state.position.get(product, 0)

            # If the underlying is missing, we cannot estimate option fair value.
            if underlying_depth is None:
                result[product] = orders
                continue

            voucher_best_bid, voucher_best_ask = self._best_bid_ask(voucher_depth)
            voucher_mid = self._mid_price(voucher_depth)
            underlying_mid = self._mid_price(underlying_depth)

            # Without both sides of the underlying book, we cannot build a clean fair value.
            if underlying_mid is None:
                result[product] = orders
                continue

            intrinsic = self._intrinsic_value(underlying_mid)
            fair_value = self._black_scholes_call_price(
                spot=underlying_mid,
                strike=self.STRIKE_PRICE,
                time_to_expiry=self.TIME_TO_EXPIRY,
                rate=self.RISK_FREE_RATE,
                volatility=self.TARGET_IV,
            )

            # Extrinsic value is the "extra" part above intrinsic value.
            # It comes from time value and uncertainty.
            model_extrinsic = max(fair_value - intrinsic, 0.0)

            # Position management:
            # If we are long, we should lean a little more toward selling.
            # If we are short, we should lean a little more toward buying.
            inventory_shift = current_position / 50.0

            remaining_buy_capacity = max(0, self.POSITION_LIMIT - current_position)
            remaining_sell_capacity = max(0, self.POSITION_LIMIT + current_position)

            print(
                f"[t={state.timestamp}] {product} | "
                f"pos={current_position} | "
                f"underlying_mid={underlying_mid:.1f} | "
                f"intrinsic={intrinsic:.1f} | "
                f"fair={fair_value:.1f} | "
                f"extrinsic={model_extrinsic:.1f} | "
                f"market_mid={voucher_mid}"
            )

            # =================================================================
            # 1. TAKE CHEAP ORDERS
            # =================================================================
            # If the best ask is clearly below our fair value, the market is
            # offering us the option too cheaply.
            #
            # In IV terms, this usually means the market is implying lower IV
            # than our target IV. That is the "cheap IV" side of scalping.
            if voucher_best_ask is not None and voucher_best_ask <= fair_value - self.TAKE_EDGE:
                available_volume = abs(voucher_depth.sell_orders[voucher_best_ask])
                buy_volume = min(self.TRADE_SIZE, remaining_buy_capacity, available_volume)

                if buy_volume > 0:
                    orders.append(Order(product, voucher_best_ask, buy_volume))
                    remaining_buy_capacity -= buy_volume

            # If the best bid is clearly above our fair value, the market is
            # paying too much for the option.
            #
            # In IV terms, this means the market is implying higher IV than our
            # target IV. That is the "rich IV" side of scalping.
            if voucher_best_bid is not None and voucher_best_bid >= fair_value + self.TAKE_EDGE:
                available_volume = voucher_depth.buy_orders[voucher_best_bid]
                sell_volume = min(self.TRADE_SIZE, remaining_sell_capacity, available_volume)

                if sell_volume > 0:
                    orders.append(Order(product, voucher_best_bid, -sell_volume))
                    remaining_sell_capacity -= sell_volume

            # =================================================================
            # 2. MAKE PASSIVE QUOTES
            # =================================================================
            # After taking obvious mispricings, we also post our own quotes.
            # This is the market-making part of the lesson.
            #
            # We quote around fair value, but we shift our prices a little
            # based on inventory so we do not keep leaning the same direction.
            bid_price = int(fair_value - self.MAKE_SPREAD - inventory_shift)
            ask_price = int(fair_value + self.MAKE_SPREAD - inventory_shift)

            # Keep the quotes sensible if the fair value is small or noisy.
            bid_price = max(1, bid_price)
            ask_price = max(bid_price + 1, ask_price)

            if remaining_buy_capacity > 0:
                bid_size = min(self.TRADE_SIZE, remaining_buy_capacity)
                orders.append(Order(product, bid_price, bid_size))

            if remaining_sell_capacity > 0:
                ask_size = min(self.TRADE_SIZE, remaining_sell_capacity)
                orders.append(Order(product, ask_price, -ask_size))

            result[product] = orders

        traderData = "LESSON3_VOUCHER_BOT_RUNNING"
        conversions = 0
        return result, conversions, traderData
