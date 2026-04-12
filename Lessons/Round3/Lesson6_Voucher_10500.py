# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 6 - VOLCANIC_ROCK_VOUCHER_10500: INTRINSIC VALUE, EXTRINSIC VALUE,
#            AND A SIMPLE IV-SCALPING IDEA
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson is a beginner-friendly guide to trading the
# VOLCANIC_ROCK_VOUCHER_10500 option.
#
# The underlying asset is VOLCANIC_ROCK.
# The voucher is a call option with strike 10500.
#
# The three ideas we want to teach are:
#   1. Intrinsic value
#   2. Extrinsic value
#   3. A simplified IV-scalping idea
#
# INTRINSIC VALUE
# ---------------
# Intrinsic value is the value the option already has right now.
#
# For a call option:
#   intrinsic = max(underlying_price - strike_price, 0)
#
# Example:
#   underlying = 10620, strike = 10500
#   intrinsic = 120
#
# If the underlying is below the strike, intrinsic value is zero.
#
# EXTRINSIC VALUE
# ---------------
# Extrinsic value is everything above intrinsic value.
# It is the part of the option price that comes from:
#   - time remaining
#   - uncertainty
#   - expected future movement
#
#   extrinsic = option_price - intrinsic
#
# Example:
#   underlying = 10620
#   voucher_price = 310
#   intrinsic = 120
#   extrinsic = 190
#
# That extra 190 is the "time and volatility premium".
#
# FAIR VALUE INTUITION
# --------------------
# A simple option fair value can be written as:
#
#   fair option price = intrinsic value + extrinsic value
#
# If the market price is too low versus our fair value, the voucher is cheap.
# If the market price is too high versus our fair value, the voucher is rich.
#
# SIMPLE IV-SCALPING IDEA
# -----------------------
# IV means implied volatility.
#
# A real option trader often:
#   - converts the market price into an implied volatility
#   - compares that implied volatility to a model or average volatility
#   - buys options when market IV looks cheap
#   - sells options when market IV looks rich
#
# That is called IV scalping.
#
# This lesson keeps the idea simple:
#   - estimate the option's market IV from the current quote
#   - keep a rolling average of past IVs as our model IV
#   - buy when market IV is below model IV
#   - sell when market IV is above model IV
#
# We do NOT add a hedge in the underlying here.
# The goal is to make the pricing idea easy to follow first.
#
# =============================================================================

import math
from statistics import NormalDist
from typing import List, Optional, Tuple

from datamodel import Order, OrderDepth, TradingState


class Trader:
    # -------------------------------------------------------------------------
    # BASIC SETTINGS
    # -------------------------------------------------------------------------
    UNDERLYING = "VOLCANIC_ROCK"
    VOUCHER = "VOLCANIC_ROCK_VOUCHER_10500"
    STRIKE = 10500.0

    # Position limit from the round notes.
    POSITION_LIMIT = 200

    # Keep trade sizes small so the lesson stays readable.
    MAX_ORDER_SIZE = 10

    # If the market IV is far enough away from our rolling model IV, we trade.
    IV_EDGE = 0.02

    # We use a fixed time-to-expiry estimate to keep the lesson simple.
    # In the real competition solution, this would be updated carefully.
    TIME_TO_EXPIRY = 5 / 365

    # Fixed volatility guess used when we turn IV back into a fair price.
    # The rolling IV average will move over time.
    STARTING_VOLATILITY = 0.25

    # Rolling history length for the "model IV" average.
    IV_HISTORY_SIZE = 20

    _N = NormalDist()

    def __init__(self) -> None:
        # We keep a small rolling list of market IV values.
        # This gives us a simple reference point for the IV scalper.
        self.recent_market_ivs: List[float] = []

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest buy price.
        # Best ask = lowest sell price.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # A clean mid price needs both sides of the book.
        best_bid, best_ask = self._best_bid_ask(order_depth)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid + best_ask) / 2

    def _normal_cdf(self, x: float) -> float:
        # Standard normal CDF.
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _black_scholes_call(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.0,
    ) -> float:
        # Black-Scholes call option value.
        #
        # The formula looks technical, but the idea is simple:
        # higher volatility means the option is usually worth more.
        if spot_price <= 0:
            return 0.0

        # If there is no time left or volatility is zero, the option is worth
        # only its intrinsic value.
        if time_to_expiry <= 0 or volatility <= 0:
            return max(spot_price - strike_price, 0.0)

        sqrt_time = math.sqrt(time_to_expiry)
        denom = volatility * sqrt_time
        if denom <= 0:
            return max(spot_price - strike_price, 0.0)

        d1 = (
            math.log(spot_price / strike_price)
            + (risk_free_rate + 0.5 * volatility * volatility) * time_to_expiry
        ) / denom
        d2 = d1 - denom

        discounted_strike = strike_price * math.exp(-risk_free_rate * time_to_expiry)
        return spot_price * self._normal_cdf(d1) - discounted_strike * self._normal_cdf(d2)

    def _implied_vol_bisection(
        self,
        market_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        lower: float = 0.01,
        upper: float = 1.50,
        iterations: int = 40,
    ) -> float:
        # Convert a market option price into an implied volatility estimate.
        #
        # We use a simple bisection search:
        #   low volatility -> cheaper option
        #   high volatility -> more expensive option
        # The IV we want is the volatility that makes the model price match the
        # market price as closely as possible.
        if market_price <= 0 or spot_price <= 0:
            return lower

        low = lower
        high = upper

        for _ in range(iterations):
            mid = (low + high) / 2.0
            model_price = self._black_scholes_call(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                volatility=mid,
            )

            if model_price > market_price:
                high = mid
            else:
                low = mid

        return (low + high) / 2.0

    def _update_iv_history(self, market_iv: float) -> float:
        # Add the latest market IV to our rolling history and return the mean.
        self.recent_market_ivs.append(market_iv)
        if len(self.recent_market_ivs) > self.IV_HISTORY_SIZE:
            self.recent_market_ivs.pop(0)

        return sum(self.recent_market_ivs) / len(self.recent_market_ivs)

    def _remaining_capacity(self, current_position: int) -> Tuple[int, int]:
        # How much room do we have left to buy or sell?
        buy_room = max(self.POSITION_LIMIT - current_position, 0)
        sell_room = max(self.POSITION_LIMIT + current_position, 0)
        return buy_room, sell_room

    def run(self, state: TradingState):
        # The engine expects:
        #   1. result      -> dict of orders by product
        #   2. conversions -> not used here
        #   3. traderData  -> string memory between ticks
        result = {}

        underlying_depth = state.order_depths.get(self.UNDERLYING)
        voucher_depth = state.order_depths.get(self.VOUCHER)

        # If either book is missing, we cannot do a clean option pricing step.
        if underlying_depth is None or voucher_depth is None:
            return result, 0, "LESSON6_VOUCHER_10500"

        underlying_mid = self._mid_price(underlying_depth)
        voucher_mid = self._mid_price(voucher_depth)

        if underlying_mid is None or voucher_mid is None:
            return result, 0, "LESSON6_VOUCHER_10500"

        # ---------------------------------------------------------------------
        # INTRINSIC VALUE
        # ---------------------------------------------------------------------
        # This is the value the call option already has "right now".
        intrinsic_value = max(underlying_mid - self.STRIKE, 0.0)

        # The amount paid above intrinsic is the extrinsic value.
        market_extrinsic = max(voucher_mid - intrinsic_value, 0.0)

        # ---------------------------------------------------------------------
        # IMPLIED VOLATILITY
        # ---------------------------------------------------------------------
        # We take the market price, turn it into IV, then compare that IV to a
        # rolling average of previous IVs.
        market_iv = self._implied_vol_bisection(
            market_price=voucher_mid,
            spot_price=underlying_mid,
            strike_price=self.STRIKE,
            time_to_expiry=self.TIME_TO_EXPIRY,
        )

        model_iv = self._update_iv_history(market_iv)
        model_price = self._black_scholes_call(
            spot_price=underlying_mid,
            strike_price=self.STRIKE,
            time_to_expiry=self.TIME_TO_EXPIRY,
            volatility=model_iv if model_iv > 0 else self.STARTING_VOLATILITY,
        )
        model_extrinsic = max(model_price - intrinsic_value, 0.0)

        current_position = state.position.get(self.VOUCHER, 0)
        buy_room, sell_room = self._remaining_capacity(current_position)

        print(
            f"[t={state.timestamp}] {self.VOUCHER} | "
            f"spot={underlying_mid:.1f} | "
            f"market={voucher_mid:.1f} | "
            f"intrinsic={intrinsic_value:.1f} | "
            f"market_extrinsic={market_extrinsic:.1f} | "
            f"model_extrinsic={model_extrinsic:.1f} | "
            f"market_iv={market_iv:.3f} | "
            f"model_iv={model_iv:.3f} | "
            f"pos={current_position}"
        )

        orders: List[Order] = []

        # ---------------------------------------------------------------------
        # SIMPLIFIED IV SCALPING RULE
        # ---------------------------------------------------------------------
        # If market IV is below our model IV, the option looks cheap.
        # Buy the option at the best ask.
        if voucher_depth.sell_orders:
            best_ask = min(voucher_depth.sell_orders.keys())
            available_volume = abs(voucher_depth.sell_orders[best_ask])

            if model_iv - market_iv > self.IV_EDGE:
                buy_size = min(self.MAX_ORDER_SIZE, buy_room, available_volume)
                if buy_size > 0:
                    orders.append(Order(self.VOUCHER, best_ask, buy_size))
                    print(
                        f"  >> cheap IV: buying {buy_size} @ {best_ask} "
                        f"(market IV below model IV)"
                    )

        # If market IV is above our model IV, the option looks rich.
        # Sell the option at the best bid.
        if voucher_depth.buy_orders:
            best_bid = max(voucher_depth.buy_orders.keys())
            available_volume = voucher_depth.buy_orders[best_bid]

            if market_iv - model_iv > self.IV_EDGE:
                sell_size = min(self.MAX_ORDER_SIZE, sell_room, available_volume)
                if sell_size > 0:
                    orders.append(Order(self.VOUCHER, best_bid, -sell_size))
                    print(
                        f"  >> rich IV: selling {sell_size} @ {best_bid} "
                        f"(market IV above model IV)"
                    )

        # ---------------------------------------------------------------------
        # WHY THIS WORKS AS A LESSON
        # ---------------------------------------------------------------------
        # We are not trying to build a full professional options desk here.
        # We only want the core intuition:
        #   - intrinsic value gives the hard floor
        #   - extrinsic value is the premium for time and uncertainty
        #   - implied volatility is a compact way to compare option richness
        #
        # Once you understand this, you can layer on hedging, skew, and more
        # advanced pricing ideas later.
        result[self.VOUCHER] = orders

        traderData = "LESSON6_VOUCHER_10500_BOT_RUNNING"
        conversions = 0
        return result, conversions, traderData
