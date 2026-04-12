# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 2 - VOLCANIC_ROCK_VOUCHER_9500: CALL OPTIONS, INTRINSIC VALUE,
#           AND SIMPLE FAIR-VALUE MEAN REVERSION
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This lesson is the first time we trade an option-style product.
#
# The underlying asset is VOLCANIC_ROCK.
# The product we trade here is VOLCANIC_ROCK_VOUCHER_9500.
#
# Think of the voucher like a call option:
#   - if VOLCANIC_ROCK goes above 9500, the voucher has intrinsic value
#   - if VOLCANIC_ROCK is below 9500, the voucher can still be worth money
#     because there is time left for the underlying to move
#
# THE THREE IMPORTANT IDEAS
# -------------------------
# 1. Intrinsic value
#    This is the "always there" part of the option.
#    For a call option with strike 9500:
#       intrinsic = max(underlying_price - 9500, 0)
#
# 2. Extrinsic value
#    This is the extra value on top of intrinsic value.
#    It comes from time remaining, volatility, and uncertainty.
#    Option price = intrinsic value + extrinsic value
#
# 3. Fair value intuition
#    If the voucher trades far above our model price, it is expensive.
#    If it trades far below our model price, it is cheap.
#    That is the whole mean-reversion idea:
#       - buy cheap options
#       - sell expensive options
#
# WHY THIS LESSON IS USEFUL
# -------------------------
# Frankfurt Hedgehogs and other top teams used more advanced option logic.
# They priced options with a Black-Scholes style model and then traded when
# the market price drifted away from that value.
#
# This lesson keeps the same core intuition, but strips it down:
#   - estimate underlying price from the order book
#   - compute a simple theoretical option price
#   - compare market price vs theoretical price
#   - buy below fair value, sell above fair value
#
# We also show the intrinsic / extrinsic split in the debug output so you can
# see why the voucher is priced the way it is.
# =============================================================================

from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional, Tuple
from statistics import NormalDist
import math


class Trader:
    # ---------------------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------------------
    # We only trade the 9500 voucher in this lesson.
    PRODUCT = "VOLCANIC_ROCK_VOUCHER_9500"
    UNDERLYING = "VOLCANIC_ROCK"
    STRIKE = 9500

    # The competition position limit for each voucher is 200 units.
    POSITION_LIMIT = 200

    # How far the market price must be from fair value before we take it.
    # This keeps the lesson simple and avoids trading every tiny fluctuation.
    TAKE_EDGE = 1

    # If inventory gets too large, stop leaning harder in the same direction.
    # That is the beginner version of risk control.
    FLATTEN_LEVEL = 150

    # A simple, fixed volatility assumption.
    # In a real solution you might estimate this from data or implied vol.
    VOLATILITY = 0.25

    # We keep the model simple by using a fixed time-to-expiry estimate.
    # The real competition solution would update this carefully over time.
    TIME_TO_EXPIRY = 5 / 365

    # Risk-free rate is ignored here to keep the math readable.
    RISK_FREE_RATE = 0.0

    _N = NormalDist()

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        # Best bid = highest price someone is willing to pay.
        # Best ask = lowest price someone is willing to sell for.
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # A normal mid price needs both sides of the book.
        # If one side is missing, we return None and skip trading this tick.
        best_bid, best_ask = self._best_bid_ask(order_depth)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid + best_ask) / 2

    def _black_scholes_call(self, spot: float) -> Tuple[float, float]:
        # This is the simplified option-pricing model.
        #
        # call_price = theoretical fair value
        # delta      = how sensitive the option is to the underlying price
        #
        # We use the standard Black-Scholes call formula:
        #   d1 = [ln(S/K) + (r + 0.5*sigma^2)T] / (sigma*sqrt(T))
        #   d2 = d1 - sigma*sqrt(T)
        #   call = S*N(d1) - K*exp(-rT)*N(d2)
        #
        # The math looks heavy, but the idea is simple:
        #   - intrinsic value is the "already in the money" part
        #   - extrinsic value is the extra time value from uncertainty
        if spot <= 0:
            return 0.0, 0.0

        if self.TIME_TO_EXPIRY <= 0:
            intrinsic = max(spot - self.STRIKE, 0.0)
            return intrinsic, 1.0 if spot > self.STRIKE else 0.0

        sigma = self.VOLATILITY
        t = self.TIME_TO_EXPIRY
        sqrt_t = math.sqrt(t)

        # Guard against division by zero if someone changes the constants.
        denom = sigma * sqrt_t
        if denom <= 0:
            intrinsic = max(spot - self.STRIKE, 0.0)
            return intrinsic, 1.0 if spot > self.STRIKE else 0.0

        d1 = (math.log(spot / self.STRIKE) + (self.RISK_FREE_RATE + 0.5 * sigma * sigma) * t) / denom
        d2 = d1 - denom

        discounted_strike = self.STRIKE * math.exp(-self.RISK_FREE_RATE * t)
        call_price = spot * self._N.cdf(d1) - discounted_strike * self._N.cdf(d2)
        delta = self._N.cdf(d1)
        return call_price, delta

    def _format_value_split(self, market_mid: float, intrinsic: float, theo: float) -> str:
        # Helpful debug string so we can see the decomposition directly.
        extrinsic = theo - intrinsic
        market_extrinsic = market_mid - intrinsic
        return (
            f"mkt={market_mid:.1f} | "
            f"intrinsic={intrinsic:.1f} | "
            f"model_extrinsic={extrinsic:.1f} | "
            f"mkt_extrinsic={market_extrinsic:.1f} | "
            f"theo={theo:.1f}"
        )

    def run(self, state: TradingState):
        # The engine expects:
        #   1. result      -> orders by product
        #   2. conversions -> not used here
        #   3. traderData  -> a string for optional memory
        result = {}

        for product in state.order_depths:
            orders: List[Order] = []

            # We only trade the voucher in this lesson.
            if product != self.PRODUCT:
                result[product] = orders
                continue

            voucher_depth: OrderDepth = state.order_depths[product]
            underlying_depth: Optional[OrderDepth] = state.order_depths.get(self.UNDERLYING)

            current_position = state.position.get(product, 0)
            remaining_buy_capacity = max(0, self.POSITION_LIMIT - current_position)
            remaining_sell_capacity = max(0, self.POSITION_LIMIT + current_position)

            # If we are already very long or very short, stop leaning harder.
            if current_position >= self.FLATTEN_LEVEL:
                remaining_buy_capacity = 0
            if current_position <= -self.FLATTEN_LEVEL:
                remaining_sell_capacity = 0

            best_bid, best_ask = self._best_bid_ask(voucher_depth)
            market_mid = self._mid_price(voucher_depth)

            # We need the underlying mid price to price the option.
            if underlying_depth is None:
                result[product] = orders
                continue

            underlying_mid = self._mid_price(underlying_depth)
            if underlying_mid is None or market_mid is None:
                result[product] = orders
                continue

            # -----------------------------------------------------------------
            # INTRINSIC VALUE
            # -----------------------------------------------------------------
            # A call option on strike 9500 is worth at least:
            #   max(underlying_mid - 9500, 0)
            #
            # This is the "exercise now" value.
            intrinsic_value = max(underlying_mid - self.STRIKE, 0.0)

            # -----------------------------------------------------------------
            # EXTRINSIC VALUE / FAIR VALUE
            # -----------------------------------------------------------------
            # The voucher can also be worth more than intrinsic value because
            # there is still time left for the underlying to move.
            #
            # We use Black-Scholes as a clean teaching model.
            theo_price, delta = self._black_scholes_call(underlying_mid)
            extrinsic_value = theo_price - intrinsic_value

            print(
                f"[t={state.timestamp}] {product} | "
                f"S={underlying_mid:.1f} | "
                f"{self._format_value_split(market_mid, intrinsic_value, theo_price)} | "
                f"delta={delta:.2f} | pos={current_position}"
            )

            # -----------------------------------------------------------------
            # 1. TAKE CHEAP OFFERS
            # -----------------------------------------------------------------
            # If someone is selling below fair value, buy from them.
            if best_ask is not None:
                if best_ask <= theo_price - self.TAKE_EDGE:
                    available_volume = abs(voucher_depth.sell_orders[best_ask])
                    buy_volume = min(remaining_buy_capacity, available_volume)

                    if buy_volume > 0:
                        orders.append(Order(product, best_ask, buy_volume))
                        remaining_buy_capacity -= buy_volume

            # If someone is buying above fair value, sell to them.
            if best_bid is not None:
                if best_bid >= theo_price + self.TAKE_EDGE:
                    available_volume = voucher_depth.buy_orders[best_bid]
                    sell_volume = min(remaining_sell_capacity, available_volume)

                    if sell_volume > 0:
                        orders.append(Order(product, best_bid, -sell_volume))
                        remaining_sell_capacity -= sell_volume

            # -----------------------------------------------------------------
            # 2. SIMPLE PASSIVE MAKING
            # -----------------------------------------------------------------
            # If nothing obvious is available, we still want to place a quote
            # around fair value so that the market can come to us.
            #
            # This is the mean-reversion idea in its simplest form:
            #   - the market price wiggles around fair value
            #   - if we quote slightly inside fair value, we can get filled
            #     when the market reverts
            bid_quote = int(math.floor(theo_price)) - 1
            ask_quote = int(math.ceil(theo_price)) + 1

            # Keep passive quotes on the correct side of the theoretical price.
            # We do not want to accidentally cross ourselves.
            if best_bid is not None:
                bid_quote = max(bid_quote, best_bid + 1)
            if best_ask is not None:
                ask_quote = min(ask_quote, best_ask - 1)

            # If the market is already tight, ensure the quotes still make sense.
            if bid_quote >= ask_quote:
                bid_quote = int(math.floor(theo_price)) - 1
                ask_quote = int(math.ceil(theo_price)) + 1

            if remaining_buy_capacity > 0:
                orders.append(Order(product, bid_quote, remaining_buy_capacity))

            if remaining_sell_capacity > 0:
                orders.append(Order(product, ask_quote, -remaining_sell_capacity))

            # A final teaching note in the code:
            #   intrinsic value tells us the minimum worth of the voucher now.
            #   extrinsic value tells us the extra time-and-volatility premium.
            #   the model price is the number we compare against the market.
            #
            # If the market moves too far away from the model price, that is
            # the mean-reversion opportunity.
            _ = extrinsic_value  # kept explicit for readability in the lesson

            result[product] = orders

        traderData = "LESSON2_VOUCHER_9500_BOT_RUNNING"
        conversions = 0
        return result, conversions, traderData
