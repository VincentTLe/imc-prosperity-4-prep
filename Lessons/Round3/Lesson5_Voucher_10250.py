# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 5 - VOLCANIC ROCK VOUCHER 10250: INTRINSIC VALUE, EXTRINSIC VALUE,
# AND A SIMPLE IV-SCALPING BOT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson is the first time we trade an option-style product.
#
# The product we focus on is:
#   - VOLCANIC_ROCK_VOUCHER_10250
#
# Think of it like a call option on VOLCANIC_ROCK with strike 10250.
# That means its value comes from two parts:
#
#   1. INTRINSIC VALUE
#      = the value you would get if you exercised it right now
#      = max(underlying_price - strike, 0)
#
#   2. EXTRINSIC VALUE
#      = extra value above intrinsic value
#      = time value, volatility, and uncertainty
#
# A call option can never be worth less than its intrinsic value for long,
# because if it were, someone could buy it cheaply and immediately exercise it.
#
# THE BIG IDEA
# ------------
# Frankfurt Hedgehogs used a much more advanced version of this idea:
#   - estimate a theoretical option value from the underlying price
#   - compare the market price to that theoretical value
#   - buy options that are too cheap
#   - sell options that are too expensive
#   - avoid overtrading when the signal is noisy
#
# This lesson keeps that idea, but simplifies it heavily:
#   - we compute a toy theoretical price with Black-Scholes
#   - we use intrinsic value as the floor
#   - we call the rest "extrinsic value"
#   - we trade only when the market is clearly cheap or rich
#
# WHY THIS IS USEFUL
# ------------------
# The important intuition is not the exact formula.
# The important intuition is:
#
#   market price = intrinsic value + extrinsic value
#
# If the option is trading close to intrinsic, the extrinsic value is small.
# If the option is trading far above intrinsic, the market is paying a lot for
# time and uncertainty.
#
# A very simplified IV-scalping idea is:
#   - estimate fair option value from the underlying
#   - compare the market to that estimate
#   - buy when the option is underpriced
#   - sell when the option is overpriced
#
# We also keep inventory under control so the bot does not get stuck too long
# in one direction.
# =============================================================================

from datamodel import OrderDepth, TradingState, Order
from statistics import NormalDist
from typing import List, Optional, Tuple
import math


_N = NormalDist()


class Trader:
    # =========================================================================
    # SIMPLE CONSTANTS
    # =========================================================================
    # PRODUCT:
    #   The specific voucher we want to trade in this lesson.
    #
    # UNDERLYING:
    #   The item the voucher is linked to.
    #
    # STRIKE:
    #   The exercise price embedded in the voucher name.
    #
    # POSITION_LIMIT:
    #   The maximum long or short inventory we allow ourselves to hold.
    #
    # TAKE_EDGE:
    #   How far away from fair value an order must be before we immediately
    #   take it.
    #
    # SCALP_EDGE:
    #   A slightly larger threshold used for the "IV scalping" signal.
    # =========================================================================
    PRODUCT = "VOLCANIC_ROCK_VOUCHER_10250"
    UNDERLYING = "VOLCANIC_ROCK"
    STRIKE = 10250

    POSITION_LIMIT = 200
    TAKE_EDGE = 8
    SCALP_EDGE = 20

    # A small fixed volatility assumption for the toy Black-Scholes estimate.
    # This is not meant to be perfect. It is just a beginner-friendly proxy.
    ASSUMED_VOL = 0.30

    # A small time-to-expiry guess. The exact number is less important than the
    # idea: longer time means more extrinsic value.
    ASSUMED_TTE = 0.08

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest visible buy price.
        # Best ask = lowest visible sell price.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # If we can see both sides of the book, use the midpoint.
        # If only one side is visible, fall back to that side.
        best_bid, best_ask = self._best_bid_ask(order_depth)

        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2
        if best_bid is not None:
            return float(best_bid)
        if best_ask is not None:
            return float(best_ask)
        return None

    def _intrinsic_value(self, underlying_mid: float) -> float:
        # Intrinsic value is the "exercise right now" value.
        # For a call option:
        #   intrinsic = max(underlying - strike, 0)
        return max(underlying_mid - self.STRIKE, 0.0)

    def _black_scholes_call(self, s: float, k: float, t: float, vol: float) -> float:
        # A very small Black-Scholes helper for a call option.
        #
        # This gives us a rough theoretical value:
        #   - intrinsic value is built in
        #   - the rest is extrinsic value from time and volatility
        #
        # We keep the implementation explicit so it is easy to read.
        if s <= 0 or k <= 0 or t <= 0 or vol <= 0:
            return max(s - k, 0.0)

        sqrt_t = math.sqrt(t)
        d1 = (math.log(s / k) + 0.5 * vol * vol * t) / (vol * sqrt_t)
        d2 = d1 - vol * sqrt_t

        call_value = s * _N.cdf(d1) - k * _N.cdf(d2)
        return call_value

    def _theoretical_value(self, underlying_mid: float) -> float:
        # This is our toy fair-value estimate for the voucher.
        # In the real strategy, Frankfurt Hedgehogs used a more careful IV model.
        return self._black_scholes_call(
            s=underlying_mid,
            k=self.STRIKE,
            t=self.ASSUMED_TTE,
            vol=self.ASSUMED_VOL,
        )

    def run(self, state: TradingState):
        # The engine expects:
        #   1. result      -> our orders by product
        #   2. conversions -> later-round feature; not used here
        #   3. traderData  -> a string we can pass to the next tick
        result = {}

        # Loop over every tradable product in the snapshot.
        for product in state.order_depths:
            orders: List[Order] = []

            # We only trade the voucher in this lesson.
            if product != self.PRODUCT:
                result[product] = orders
                continue

            option_depth: OrderDepth = state.order_depths[product]
            current_position = state.position.get(product, 0)

            # We also need the underlying price to estimate intrinsic value.
            underlying_depth: Optional[OrderDepth] = state.order_depths.get(self.UNDERLYING)
            underlying_mid = self._mid_price(underlying_depth) if underlying_depth is not None else None

            # If we cannot see the underlying, we cannot price the voucher well.
            if underlying_mid is None:
                result[product] = orders
                continue

            best_bid, best_ask = self._best_bid_ask(option_depth)
            option_mid = self._mid_price(option_depth)

            intrinsic_value = self._intrinsic_value(underlying_mid)
            theoretical_value = self._theoretical_value(underlying_mid)
            extrinsic_value = max(theoretical_value - intrinsic_value, 0.0)

            # Remaining room before we hit the position limit.
            remaining_buy_capacity = max(0, self.POSITION_LIMIT - current_position)
            remaining_sell_capacity = max(0, self.POSITION_LIMIT + current_position)

            print(
                f"[t={state.timestamp}] {product} | "
                f"pos={current_position} | "
                f"underlying_mid={underlying_mid:.1f} | "
                f"intrinsic={intrinsic_value:.1f} | "
                f"extrinsic={extrinsic_value:.1f} | "
                f"theoretical={theoretical_value:.1f} | "
                f"option_mid={(option_mid if option_mid is not None else float('nan')):.1f}"
            )

            # ================================================================
            # 1. INTRINSIC VALUE CHECK
            # ================================================================
            # This is the easiest rule to remember:
            #   - if the option is offered below intrinsic value, it is cheap
            #   - if the market bid is above fair value, it is rich
            #
            # In practice, market prices are not always perfectly clean.
            # We therefore combine the intrinsic floor with our theoretical
            # value estimate.
            # ================================================================

            # Buy if the best ask is clearly cheap.
            # We accept either:
            #   - an ask below intrinsic value, or
            #   - an ask well below our theoretical value
            if best_ask is not None and remaining_buy_capacity > 0:
                cheap_vs_intrinsic = best_ask <= intrinsic_value
                cheap_vs_theory = best_ask <= theoretical_value - self.TAKE_EDGE

                if cheap_vs_intrinsic or cheap_vs_theory:
                    buy_volume = abs(option_depth.sell_orders[best_ask])
                    buy_volume = min(buy_volume, remaining_buy_capacity)

                    if buy_volume > 0:
                        print(
                            f"  >> CHEAP OPTION found! Buying {buy_volume} units @ {best_ask}"
                        )
                        orders.append(Order(product, best_ask, buy_volume))
                        remaining_buy_capacity -= buy_volume

            # Sell if the best bid is clearly expensive.
            if best_bid is not None and remaining_sell_capacity > 0:
                rich_vs_theory = best_bid >= theoretical_value + self.TAKE_EDGE

                if rich_vs_theory:
                    sell_volume = option_depth.buy_orders[best_bid]
                    sell_volume = min(sell_volume, remaining_sell_capacity)

                    if sell_volume > 0:
                        print(
                            f"  >> EXPENSIVE OPTION found! Selling {sell_volume} units @ {best_bid}"
                        )
                        orders.append(Order(product, best_bid, -sell_volume))
                        remaining_sell_capacity -= sell_volume

            # ================================================================
            # 2. SIMPLIFIED IV-SCALPING IDEA
            # ================================================================
            # The "IV scalping" intuition is that the option price should not
            # wander too far away from our fair value estimate.
            #
            # A beginner-friendly version is:
            #   - if the market is much cheaper than fair value, buy
            #   - if the market is much richer than fair value, sell
            #   - otherwise do nothing
            #
            # This is already a form of scalping: we are trying to capture the
            # small edge between market price and theoretical value, not make a
            # big directional prediction.
            #
            # We only use the mid price here as a simple signal. The actual
            # Frankfurt Hedgehogs code used a more detailed rolling comparison
            # to avoid reacting to noise.
            # ================================================================
            if option_mid is not None:
                mispricing = option_mid - theoretical_value

                # If the whole book looks cheap, buy a little more.
                if mispricing <= -self.SCALP_EDGE and remaining_buy_capacity > 0:
                    extra_buy = min(remaining_buy_capacity, 5)
                    print(
                        f"  >> IV-SCALP BUY: mid is {abs(mispricing):.1f} below fair "
                        f"-> buying {extra_buy}"
                    )
                    if extra_buy > 0:
                        # Use the best ask if it exists, otherwise use the mid.
                        price = best_ask if best_ask is not None else int(round(option_mid))
                        orders.append(Order(product, price, extra_buy))
                        remaining_buy_capacity -= extra_buy

                # If the whole book looks rich, sell a little more.
                elif mispricing >= self.SCALP_EDGE and remaining_sell_capacity > 0:
                    extra_sell = min(remaining_sell_capacity, 5)
                    print(
                        f"  >> IV-SCALP SELL: mid is {mispricing:.1f} above fair "
                        f"-> selling {extra_sell}"
                    )
                    if extra_sell > 0:
                        price = best_bid if best_bid is not None else int(round(option_mid))
                        orders.append(Order(product, price, -extra_sell))
                        remaining_sell_capacity -= extra_sell

            # ================================================================
            # 3. INVENTORY CONTROL
            # ================================================================
            # If we are already heavily long, stop buying more.
            # If we are already heavily short, stop selling more.
            #
            # This is the beginner version of risk management.
            # The goal is not to be perfectly hedged.
            # The goal is to avoid accumulating a huge unwanted position while
            # we wait for the option price to move back toward fair value.
            # ================================================================
            if current_position >= int(self.POSITION_LIMIT * 0.8):
                remaining_buy_capacity = 0
            if current_position <= -int(self.POSITION_LIMIT * 0.8):
                remaining_sell_capacity = 0

            # ================================================================
            # 4. OPTIONAL LIGHT MARKET MAKING
            # ================================================================
            # If we still have room after the aggressive trades above, we can
            # place one simple passive order on each side.
            #
            # The goal is not to be fancy. The goal is to show the idea that:
            #   - buy slightly below fair value
            #   - sell slightly above fair value
            # ================================================================
            if remaining_buy_capacity > 0 and best_bid is not None:
                passive_bid_price = min(int(math.floor(theoretical_value)) - 1, best_bid + 1)
                passive_buy = min(remaining_buy_capacity, 2)
                if passive_buy > 0:
                    orders.append(Order(product, passive_bid_price, passive_buy))

            if remaining_sell_capacity > 0 and best_ask is not None:
                passive_ask_price = max(int(math.ceil(theoretical_value)) + 1, best_ask - 1)
                passive_sell = min(remaining_sell_capacity, 2)
                if passive_sell > 0:
                    orders.append(Order(product, passive_ask_price, -passive_sell))

            result[product] = orders

        traderData = "LESSON5_VOUCHER_10250_BOT_RUNNING"
        conversions = 0
        return result, conversions, traderData
