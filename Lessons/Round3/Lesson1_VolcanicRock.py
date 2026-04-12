# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 1 - VOLCANIC ROCK: UNDERLYING VS OPTION, AND SIMPLE MEAN REVERSION
# =============================================================================
#
# WHAT THIS LESSON IS FOR
# -----------------------
# Round 3 introduces options.
#
# VOLCANIC_ROCK is the underlying product.
# VOLCANIC_ROCK_VOUCHER is a call option on that underlying.
#
# That relationship matters:
#   - The underlying is the thing itself.
#   - The option is the right to buy the thing later at a fixed strike price.
#
# If the underlying price goes up, the option usually goes up too.
# If the underlying price goes down, the option usually gets cheaper.
# The option is more sensitive, but not one-for-one. That sensitivity is
# called delta.
#
# The main idea in this lesson is simple mean reversion:
#   - compute a theoretical option value from the underlying price
#   - compare that model value to the market price
#   - if the market option looks too cheap, buy it
#   - if the market option looks too expensive, sell it
#
# This is intentionally beginner-friendly code.
# The goal is to make the logic easy to follow, not to be the fanciest bot.
#
# =============================================================================

import math
from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional


class Trader:
    # Position limits from the round notes.
    UNDERLYING_LIMIT = 400
    VOUCHER_LIMIT = 200

    # Default option assumptions for the lesson.
    # The notebook and notes show a 10000 strike example, so we use that as the
    # default when the product name does not include a strike suffix.
    DEFAULT_STRIKE = 10000.0
    DEFAULT_VOLATILITY = 0.16
    TIME_TO_EXPIRY = 0.02

    # If the market option price is farther than this from model value, we trade.
    # This is the "mean reversion" threshold.
    EDGE_THRESHOLD = 10.0

    # Keep trade size small so the lesson stays easy to read.
    ORDER_SIZE = 10

    def norm_cdf(self, x: float) -> float:
        # Standard normal CDF using erf.
        # This is a compact way to turn a z-score into a probability.
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def black_scholes_call(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.0,
    ) -> float:
        # Black-Scholes call option price.
        #
        # Inputs:
        #   spot_price      = current underlying price
        #   strike_price    = fixed price written into the option contract
        #   time_to_expiry  = how long until the option expires
        #   volatility      = how much the underlying tends to move
        #
        # If the option is already expired, the value is just intrinsic value.
        if time_to_expiry <= 0 or volatility <= 0 or spot_price <= 0:
            return max(0.0, spot_price - strike_price)

        sqrt_time = math.sqrt(time_to_expiry)
        d1 = (
            math.log(spot_price / strike_price)
            + (risk_free_rate + 0.5 * volatility * volatility) * time_to_expiry
        ) / (volatility * sqrt_time)
        d2 = d1 - volatility * sqrt_time

        discount = math.exp(-risk_free_rate * time_to_expiry)
        return spot_price * self.norm_cdf(d1) - strike_price * discount * self.norm_cdf(d2)

    def mid_price(self, order_depth: OrderDepth) -> Optional[float]:
        # Best bid = highest price someone wants to pay.
        # Best ask = lowest price someone wants to sell at.
        # Mid price = simple estimate of fair value.
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) / 2

    def best_price(self, order_depth: OrderDepth, side: str) -> Optional[int]:
        # Small helper used when we want a real executable price.
        # "buy" means we need the best ask from the sell book.
        # "sell" means we need the best bid from the buy book.
        if side == "buy" and order_depth.sell_orders:
            return min(order_depth.sell_orders.keys())
        if side == "sell" and order_depth.buy_orders:
            return max(order_depth.buy_orders.keys())
        return None

    def get_strike_from_name(self, product: str) -> float:
        # Lesson-friendly parsing:
        #   VOLCANIC_ROCK_VOUCHER_10000 -> 10000
        #   VOLCANIC_ROCK_VOUCHER        -> default strike
        parts = product.split("_")
        if parts and parts[-1].isdigit():
            return float(parts[-1])
        return self.DEFAULT_STRIKE

    def get_voucher_products(self, state: TradingState) -> List[str]:
        # The round may expose one voucher or several strikes.
        # We simply trade every option-like product we can see.
        products: List[str] = []
        for product in state.order_depths:
            if product.startswith("VOLCANIC_ROCK_VOUCHER") or product == "VOUCHERS":
                products.append(product)
        return products

    def trade_voucher(
        self,
        state: TradingState,
        voucher_product: str,
        rock_fair_value: float,
    ) -> List[Order]:
        orders: List[Order] = []
        order_depth = state.order_depths[voucher_product]
        current_position = state.position.get(voucher_product, 0)

        position_room_buy = max(self.VOUCHER_LIMIT - current_position, 0)
        position_room_sell = max(self.VOUCHER_LIMIT + current_position, 0)

        voucher_mid = self.mid_price(order_depth)
        if voucher_mid is None:
            # We need both sides of the book for a clean comparison.
            return orders

        strike = self.get_strike_from_name(voucher_product)
        theoretical_price = self.black_scholes_call(
            spot_price=rock_fair_value,
            strike_price=strike,
            time_to_expiry=self.TIME_TO_EXPIRY,
            volatility=self.DEFAULT_VOLATILITY,
        )

        # Delta tells us how much the option moves when the underlying moves by 1.
        # A delta near 0.5 means one option behaves like about half a rock share.
        sqrt_time = math.sqrt(self.TIME_TO_EXPIRY)
        d1 = (
            math.log(rock_fair_value / strike)
            + 0.5 * self.DEFAULT_VOLATILITY * self.DEFAULT_VOLATILITY * self.TIME_TO_EXPIRY
        ) / (self.DEFAULT_VOLATILITY * sqrt_time)
        delta = self.norm_cdf(d1)

        price_gap = theoretical_price - voucher_mid

        print(
            f"[t={state.timestamp}] {voucher_product} | pos={current_position} | "
            f"rock={rock_fair_value:.2f} | model={theoretical_price:.2f} | "
            f"market={voucher_mid:.2f} | gap={price_gap:.2f} | delta={delta:.2f}"
        )

        # Mean reversion idea:
        #   - market below model by enough -> buy the cheap option
        #   - market above model by enough -> sell the expensive option
        #
        # We only use a small size, because the lesson is about readability.
        if price_gap > self.EDGE_THRESHOLD and position_room_buy > 0:
            best_ask = self.best_price(order_depth, "buy")
            if best_ask is not None:
                available = abs(order_depth.sell_orders[best_ask])
                buy_qty = min(self.ORDER_SIZE, position_room_buy, available)
                if buy_qty > 0:
                    orders.append(Order(voucher_product, best_ask, buy_qty))
                    print(f"  buy {buy_qty} {voucher_product} @ {best_ask}")

        elif price_gap < -self.EDGE_THRESHOLD and position_room_sell > 0:
            best_bid = self.best_price(order_depth, "sell")
            if best_bid is not None:
                available = order_depth.buy_orders[best_bid]
                sell_qty = min(self.ORDER_SIZE, position_room_sell, available)
                if sell_qty > 0:
                    orders.append(Order(voucher_product, best_bid, -sell_qty))
                    print(f"  sell {sell_qty} {voucher_product} @ {best_bid}")

        # The option is linked to the underlying, so the underlying price is our anchor.
        # We do not add a hedge in this lesson, but the delta printout shows why
        # options and underlying should be thought of together.
        return orders

    def run(self, state: TradingState):
        # This lesson trades the underlying plus any voucher products we can see.
        result: Dict[str, List[Order]] = {}

        rock_product = "VOLCANIC_ROCK"
        rock_depth = state.order_depths.get(rock_product)
        if rock_depth is None:
            return result, 0, ""

        rock_position = state.position.get(rock_product, 0)
        rock_fair_value = self.mid_price(rock_depth)
        if rock_fair_value is None:
            # If one side is missing, we cannot compute a clean fair value.
            return result, 0, ""

        print(
            f"[t={state.timestamp}] {rock_product} | pos={rock_position} | "
            f"mid={rock_fair_value:.2f}"
        )

        # The underlying itself is traded with very simple mean reversion:
        # if it is cheap vs its own mid estimate, buy;
        # if it is expensive, sell.
        rock_orders: List[Order] = []
        rock_buy_room = max(self.UNDERLYING_LIMIT - rock_position, 0)
        rock_sell_room = max(self.UNDERLYING_LIMIT + rock_position, 0)

        best_rock_ask = self.best_price(rock_depth, "buy")
        best_rock_bid = self.best_price(rock_depth, "sell")

        if best_rock_ask is not None and best_rock_bid is not None:
            # For the underlying, we use a tiny threshold around the mid price.
            if best_rock_ask <= rock_fair_value - 1 and rock_buy_room > 0:
                available = abs(rock_depth.sell_orders[best_rock_ask])
                buy_qty = min(self.ORDER_SIZE, rock_buy_room, available)
                if buy_qty > 0:
                    rock_orders.append(Order(rock_product, best_rock_ask, buy_qty))
                    print(f"  buy {buy_qty} {rock_product} @ {best_rock_ask}")

            elif best_rock_bid >= rock_fair_value + 1 and rock_sell_room > 0:
                available = rock_depth.buy_orders[best_rock_bid]
                sell_qty = min(self.ORDER_SIZE, rock_sell_room, available)
                if sell_qty > 0:
                    rock_orders.append(Order(rock_product, best_rock_bid, -sell_qty))
                    print(f"  sell {sell_qty} {rock_product} @ {best_rock_bid}")

        result[rock_product] = rock_orders

        # Trade all voucher-style products that appear in the state.
        for voucher_product in self.get_voucher_products(state):
            result[voucher_product] = self.trade_voucher(state, voucher_product, rock_fair_value)

        return result, 0, ""
