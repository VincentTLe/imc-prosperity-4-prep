# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 4 - VOLCANIC ROCK VOUCHER 10000: INTRO TO OPTION VALUE
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson shows how to think about the VOLCANIC_ROCK_VOUCHER_10000 option.
#
# The voucher is a CALL OPTION on VOLCANIC_ROCK with strike 10000.
# That means:
#   - if VOLCANIC_ROCK finishes above 10000, the option has value
#   - if it finishes below 10000, the option may expire worthless
#
# This lesson focuses on three ideas:
#   1. Intrinsic value
#   2. Extrinsic value
#   3. A simplified "IV scalping" idea
#
# INTRINSIC VALUE
# ---------------
# Intrinsic value is the value the option already has right now.
#
# For a call option:
#   intrinsic = max(spot_price - strike_price, 0)
#
# Example:
#   spot = 10120, strike = 10000
#   intrinsic = 120
#
# If spot is below strike, intrinsic is zero.
#
# EXTRINSIC VALUE
# ---------------
# Extrinsic value is everything above intrinsic value.
# It is the "extra" price traders pay for time and uncertainty.
#
#   extrinsic = option_price - intrinsic
#
# Example:
#   spot = 10120, strike = 10000, option_price = 310
#   intrinsic = 120
#   extrinsic = 190
#
# That extra 190 is time value and volatility value.
#
# FAIR VALUE IN TINY TERMS
# ------------------------
# A simple way to think about option fair value is:
#
#   fair option price = intrinsic value + time value
#
# If the market is asking for too little extrinsic value, the option is cheap.
# If the market is asking for too much extrinsic value, the option is expensive.
#
# SCALED-DOWN IV SCALPING IDEA
# ----------------------------
# "IV" means implied volatility.
#
# A full professional IV scalper tries to:
#   - estimate the option's implied volatility from the market price
#   - compare it with a model or rolling average volatility
#   - buy options when market IV is low
#   - sell options when market IV is high
#
# In real trading, this is often paired with delta hedging in the underlying.
# This lesson keeps it simpler:
#   - we estimate market IV from the option price
#   - we compare it with a rolling model IV
#   - we buy cheap options and sell expensive options
#
# The goal here is not to be clever.
# The goal is to show the logic in a readable way.
#
# =============================================================================

import math
from typing import List, Optional, Tuple

from datamodel import Order, OrderDepth, TradingState


# =============================================================================
# BASIC SETTINGS
# =============================================================================
# Keeping the constants in one place makes the lesson easier to read.
# =============================================================================
UNDERLYING = "VOLCANIC_ROCK"
VOUCHER = "VOLCANIC_ROCK_VOUCHER_10000"
STRIKE_PRICE = 10000
TIME_TO_EXPIRY = 0.02
POSITION_LIMIT = 200
MAX_TRADE_SIZE = 10
IV_EDGE = 0.01
EXTRINSIC_EDGE = 10.0
MIN_IV_HISTORY = 5
IV_HISTORY_SIZE = 20


def best_bid_ask(order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
    """Return the best bid and best ask from an order book."""

    best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
    best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
    return best_bid, best_ask


def mid_price(order_depth: OrderDepth) -> Optional[float]:
    """Return the simple midpoint of the best bid and best ask."""

    best_bid, best_ask = best_bid_ask(order_depth)
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2


def available_sell_volume(order_depth: OrderDepth, price: int) -> int:
    """Sell orders are stored as negative volumes, so we use abs()."""

    return abs(order_depth.sell_orders.get(price, 0))


def available_buy_volume(order_depth: OrderDepth, price: int) -> int:
    """Buy orders already store positive volume."""

    return order_depth.buy_orders.get(price, 0)


def normal_cdf(x: float) -> float:
    """A tiny normal CDF helper using math.erf."""

    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float = 0.0,
) -> float:
    """Black-Scholes call price.

    This is the theoretical price we use as a fair-value reference.
    For a beginner lesson, the important idea is not the formula details.
    The important idea is that higher volatility usually means a higher price.
    """

    if spot_price <= 0 or strike_price <= 0:
        return 0.0

    # If there is no time left, the option is worth only its payoff.
    if time_to_expiry <= 0 or volatility <= 0:
        return max(spot_price - strike_price, 0.0)

    sqrt_time = math.sqrt(time_to_expiry)
    log_moneyness = math.log(spot_price / strike_price)
    variance_adjustment = (risk_free_rate + 0.5 * volatility * volatility) * time_to_expiry

    d1 = (log_moneyness + variance_adjustment) / (volatility * sqrt_time)
    d2 = d1 - volatility * sqrt_time

    discount_factor = math.exp(-risk_free_rate * time_to_expiry)
    return spot_price * normal_cdf(d1) - strike_price * discount_factor * normal_cdf(d2)


def implied_volatility_bisection(
    market_price: float,
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    lower: float = 0.01,
    upper: float = 1.50,
    iterations: int = 40,
) -> float:
    """Estimate implied volatility from a market option price.

    We use a simple bisection search:
    - low volatility gives a cheaper option
    - high volatility gives a more expensive option
    - we search for the volatility that matches the market price
    """

    if market_price <= 0:
        return lower

    low = lower
    high = upper

    for _ in range(iterations):
        mid = (low + high) / 2.0
        model_price = black_scholes_call(spot_price, strike_price, time_to_expiry, mid)

        if model_price > market_price:
            high = mid
        else:
            low = mid

    return (low + high) / 2.0


class Trader:
    """Beginner-friendly voucher trader.

    The class stores a small rolling history of market IVs.
    That gives us a very simple "model IV" to compare against the market.
    """

    def __init__(self) -> None:
        self.recent_market_ivs: List[float] = []

    def _update_iv_history(self, iv: float) -> float:
        """Add a new IV to the rolling list and return the current model IV."""

        self.recent_market_ivs.append(iv)
        if len(self.recent_market_ivs) > IV_HISTORY_SIZE:
            self.recent_market_ivs.pop(0)

        return sum(self.recent_market_ivs) / len(self.recent_market_ivs)

    def _position_room(self, current_position: int) -> Tuple[int, int]:
        """Return how much room we have left to buy and sell."""

        room_to_buy = POSITION_LIMIT - current_position
        room_to_sell = POSITION_LIMIT + current_position
        return room_to_buy, room_to_sell

    def run(self, state: TradingState):
        # ---------------------------------------------------------------------
        # Step 1: grab the two books we need.
        # The voucher is the product we trade.
        # The underlying is the product we use for pricing intuition.
        # ---------------------------------------------------------------------
        result = {}

        underlying_book = state.order_depths.get(UNDERLYING)
        voucher_book = state.order_depths.get(VOUCHER)

        if underlying_book is None or voucher_book is None:
            return result, 1, "LESSON4_VOUCHER_10000"

        underlying_mid = mid_price(underlying_book)
        voucher_mid = mid_price(voucher_book)

        if underlying_mid is None or voucher_mid is None:
            return result, 1, "LESSON4_VOUCHER_10000"

        # ---------------------------------------------------------------------
        # Step 2: compute intrinsic and extrinsic value.
        # This is the heart of the lesson.
        # ---------------------------------------------------------------------
        intrinsic_value = max(underlying_mid - STRIKE_PRICE, 0.0)
        market_extrinsic = max(voucher_mid - intrinsic_value, 0.0)

        # ---------------------------------------------------------------------
        # Step 3: estimate market IV and a simple model IV.
        # We convert the market price into IV, then compare that IV with a
        # rolling average of recent IVs.
        # ---------------------------------------------------------------------
        market_iv = implied_volatility_bisection(
            market_price=voucher_mid,
            spot_price=underlying_mid,
            strike_price=STRIKE_PRICE,
            time_to_expiry=TIME_TO_EXPIRY,
        )

        model_iv = self._update_iv_history(market_iv)
        theoretical_price = black_scholes_call(
            spot_price=underlying_mid,
            strike_price=STRIKE_PRICE,
            time_to_expiry=TIME_TO_EXPIRY,
            volatility=model_iv,
        )
        model_extrinsic = max(theoretical_price - intrinsic_value, 0.0)

        # ---------------------------------------------------------------------
        # Step 4: print the teaching values.
        # These logs are helpful when you run the backtester.
        # ---------------------------------------------------------------------
        current_position = state.position.get(VOUCHER, 0)
        room_to_buy, room_to_sell = self._position_room(current_position)

        print(
            f"[t={state.timestamp}] {VOUCHER} | "
            f"spot={underlying_mid:.1f} | "
            f"market={voucher_mid:.1f} | "
            f"intrinsic={intrinsic_value:.1f} | "
            f"market_extrinsic={market_extrinsic:.1f} | "
            f"model_iv={model_iv:.3f} | "
            f"market_iv={market_iv:.3f} | "
            f"position={current_position}"
        )

        # ---------------------------------------------------------------------
        # Step 5: simplified IV scalping decision.
        #
        # If the market extrinsic value is below our model extrinsic value,
        # the option looks cheap. We buy a little.
        #
        # If the market extrinsic value is above our model extrinsic value,
        # the option looks expensive. We sell a little.
        #
        # This is the core scalping idea:
        # buy cheap volatility, sell rich volatility.
        # ---------------------------------------------------------------------
        orders: List[Order] = []

        if voucher_book.sell_orders:
            best_ask = min(voucher_book.sell_orders)
            ask_volume = available_sell_volume(voucher_book, best_ask)

            if model_extrinsic - market_extrinsic > EXTRINSIC_EDGE:
                buy_size = min(MAX_TRADE_SIZE, room_to_buy, ask_volume)
                if buy_size > 0:
                    print(
                        f"  >> CHEAP VOUCHER: buying {buy_size} @ {best_ask} "
                        f"(market extrinsic below model extrinsic)"
                    )
                    orders.append(Order(VOUCHER, best_ask, buy_size))
                    room_to_buy -= buy_size

        if voucher_book.buy_orders:
            best_bid = max(voucher_book.buy_orders)
            bid_volume = available_buy_volume(voucher_book, best_bid)

            if market_extrinsic - model_extrinsic > EXTRINSIC_EDGE:
                sell_size = min(MAX_TRADE_SIZE, room_to_sell, bid_volume)
                if sell_size > 0:
                    print(
                        f"  >> EXPENSIVE VOUCHER: selling {sell_size} @ {best_bid} "
                        f"(market extrinsic above model extrinsic)"
                    )
                    orders.append(Order(VOUCHER, best_bid, -sell_size))
                    room_to_sell -= sell_size

        # ---------------------------------------------------------------------
        # Step 6: store the orders for the voucher.
        # We do not place orders in the underlying in this beginner lesson.
        # That keeps the code focused on option pricing rather than hedging.
        # ---------------------------------------------------------------------
        if orders:
            result[VOUCHER] = orders

        trader_data = "LESSON4_VOUCHER_10000"
        conversions = 1
        return result, conversions, trader_data
