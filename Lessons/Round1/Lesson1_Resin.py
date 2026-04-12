# -*- coding: utf-8 -*-
# =============================================================================
# LESSON 1 — RAINFOREST RESIN: YOUR FIRST TRADING BOT
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This is the brain of your trading robot. Every single "tick" (moment in
# time), the competition's system calls your run() function and gives you a
# snapshot of the market. You look at the prices, make a decision, and return
# a list of buy/sell orders.
#
# WHAT IS A MARKET? (Think of it like a marketplace)
# ---------------------------------------------------
# Imagine a fruit market. Some people want to BUY apples, some want to SELL
# them. Everyone shouts their price:
#   - "I'll pay $9.98 for apples!"  → this is a BID  (buyer's offer)
#   - "I'm selling apples for $10.02!" → this is an ASK (seller's offer)
#
# In Prosperity 4, instead of apples we trade "RAINFOREST_RESIN", and instead
# of dollars we use "SeaShells" (the in-game currency).
#
# WHAT IS FAIR VALUE?
# -------------------
# For Rainforest Resin, the true value is ALWAYS 10,000 SeaShells.
# This is your golden rule. If someone sells it CHEAPER than 10,000 → BUY.
# If someone pays MORE than 10,000 for it → SELL to them.
# This is called "market making" or "statistical arbitrage".
#
# HOW DO YOU MAKE PROFIT?
# -----------------------
# Example:
#   - You see someone selling at 9,998 → you buy 10 units at 9,998
#   - You see someone buying at 10,002 → you sell 10 units at 10,002
#   - Profit = (10,002 - 9,998) × 10 = 40 SeaShells  ✓
#
# =============================================================================

from datamodel import OrderDepth, TradingState, Order
from typing import List


class Trader:
    # =========================================================================
    # THE TRADER CLASS
    # =========================================================================
    # In Python, a "class" is like a blueprint for an object.
    # Think of it as the instruction manual for your robot.
    # The competition engine creates ONE instance of this class and calls
    # run() repeatedly — once per timestep.
    #
    # Example timeline:
    #   t=100  → engine calls Trader.run(state at t=100)  → you return orders
    #   t=200  → engine calls Trader.run(state at t=200)  → you return orders
    #   t=300  → ...and so on, up to thousands of timesteps
    # =========================================================================

    def run(self, state: TradingState):
        # =====================================================================
        # WHAT IS 'state'?
        # =====================================================================
        # 'state' is a snapshot of the entire market RIGHT NOW.
        # It is of type TradingState (defined in datamodel.py).
        # Key things inside state:
        #
        #   state.timestamp          → current time, e.g. 100, 200, 300 ...
        #   state.order_depths       → dict of {product: OrderDepth}
        #                              each OrderDepth has the order book
        #   state.position           → dict of {product: your_current_inventory}
        #
        # Example: if state.position = {"RAINFOREST_RESIN": 25}
        #          it means you currently hold 25 units of Resin.
        # =====================================================================

        # 'result' is a dictionary where we collect our final orders.
        # Key   = product name (string)
        # Value = list of Order objects to send for that product
        #
        # Example: result = {"RAINFOREST_RESIN": [Order("RAINFOREST_RESIN", 9998, 10)]}
        # means: buy 10 units of Resin at price 9998.
        result = {}

        # =====================================================================
        # LOOP OVER ALL PRODUCTS CURRENTLY TRADEABLE
        # =====================================================================
        # state.order_depths is a dictionary.
        # In Lesson 1, it usually contains just one product: "RAINFOREST_RESIN".
        # In later rounds, there will be more products (KELP, SQUID_INK, etc.)
        # so looping lets your bot handle all of them automatically.
        #
        # Example iteration:
        #   product = "RAINFOREST_RESIN"
        #   order_depth = state.order_depths["RAINFOREST_RESIN"]
        # =====================================================================
        for product in state.order_depths:

            # -----------------------------------------------------------------
            # GRAB THE ORDER BOOK FOR THIS PRODUCT
            # -----------------------------------------------------------------
            # OrderDepth has two dictionaries:
            #   .buy_orders  = {price: volume}  — people who WANT to buy
            #   .sell_orders = {price: volume}  — people who WANT to sell
            #                                    (volumes are NEGATIVE here!)
            #
            # Example order book for RAINFOREST_RESIN:
            #   buy_orders  = {9999: 20, 9998: 15, 9997: 5}
            #                  "20 people will buy at 9999,
            #                   15 people will buy at 9998" ...
            #   sell_orders = {10001: -25, 10002: -10}
            #                  "25 available to buy at 10001,
            #                   10 available at 10002" ...
            # -----------------------------------------------------------------
            order_depth: OrderDepth = state.order_depths[product]

            # This list will collect every order WE want to place this timestep.
            # We add Order objects to it, then hand it back to the engine.
            orders: List[Order] = []

            # =================================================================
            # PRODUCT: RAINFOREST_RESIN
            # STRATEGY: FAIR VALUE = 10,000  (it never changes!)
            # Rule: Buy if price < 10000, Sell if price > 10000
            # =================================================================
            if product == 'RAINFOREST_RESIN':

                # -------------------------------------------------------------
                # STEP 1 — CHECK YOUR CURRENT POSITION (INVENTORY MANAGEMENT)
                # -------------------------------------------------------------
                # Your "position" is how many units of Resin you currently own.
                #   positive number → you OWN that many (you're LONG)
                #   negative number → you OWE that many (you're SHORT)
                #   zero            → you hold nothing
                #
                # Example: current_position = 30
                #   means you bought 30 units earlier and still hold them.
                #
                # THE POSITION LIMIT:
                # The rules say you can hold AT MOST +80 (long) or -80 (short).
                # Violating this = your order gets rejected!
                # So BEFORE placing any order, check how much room you have.
                #
                # Example calculations:
                #   current_position =  30 → max_buy_volume  = 80 - 30  = 50
                #                            max_sell_volume = -80 - 30 = -110  (unused; capped by available sellers)
                #   current_position = -20 → max_buy_volume  = 80 -(-20) = 100 (but market won't have 100 sellers)
                #                            max_sell_volume = -80-(-20) = -60
                # -------------------------------------------------------------
                current_position = state.position.get(product, 0)
                # .get(product, 0) safely returns 0 if we have no position yet.

                max_buy_volume  = 80 - current_position   # how many MORE we can buy
                max_sell_volume = -80 - current_position  # how many MORE we can sell (negative!)

                # Print a debug line — visible in the terminal and backtester logs
                print(f"[t={state.timestamp}] {product} | "
                      f"Position: {current_position} | "
                      f"Room to buy: {max_buy_volume} | "
                      f"Room to sell: {max_sell_volume}")

                # -------------------------------------------------------------
                # STEP 2 — SCAN THE SELL SIDE: FIND CHEAP SELLERS (BUY OPPORTUNITY)
                # -------------------------------------------------------------
                # sell_orders shows what other traders are OFFERING to sell at.
                # We want to find the LOWEST ask price (cheapest seller).
                #
                # min(sell_orders.keys()) gives the cheapest price available.
                #
                # Decision rule:
                #   If cheapest_ask < 10000 → that person is selling BELOW fair value
                #   → We buy from them immediately and will profit when the price
                #     returns to 10,000.
                #
                # Example:
                #   sell_orders = {9997: -30, 10001: -20}
                #   best_ask_price = min(9997, 10001) = 9997
                #   9997 < 10000 → BUY! We get a 3 SeaShell profit per unit.
                # -------------------------------------------------------------
                if len(order_depth.sell_orders) > 0:

                    best_ask_price = min(order_depth.sell_orders.keys())

                    if best_ask_price < 9999:  # <-- TRY CHANGING 10000 to 9999 and see what happens!

                        # How many units is that seller offering?
                        # sell_orders store negative volumes (e.g. -30), so we
                        # use abs() to get the positive number for math purposes.
                        #
                        # Example: sell_orders[9997] = -30
                        #   abs(-30) = 30 → they offer 30 units
                        available_volume = abs(order_depth.sell_orders[best_ask_price])

                        # We can't buy MORE than:
                        #   (a) what's available from the seller, AND
                        #   (b) our remaining capacity (max_buy_volume)
                        # min() picks the smaller of the two to stay safe.
                        #
                        # Example: available_volume=30, max_buy_volume=50 → buy 30
                        # Example: available_volume=30, max_buy_volume=10 → buy 10 (capacity capped!)
                        buy_amount = min(max_buy_volume, available_volume)

                        if buy_amount > 0:
                            print(f"  >> CHEAP ASK found! Buying {buy_amount} units @ {best_ask_price}")

                            # Create a BUY order:
                            #   Order(product_name, price, quantity)
                            #   POSITIVE quantity = BUY
                            buy_order = Order(product, best_ask_price, buy_amount)
                            orders.append(buy_order)

                            # Update our remaining capacity IMMEDIATELY.
                            # This prevents accidentally over-buying if there are
                            # multiple cheap sellers in the same timestep.
                            # Example: we just bought 30 → max_buy_volume goes from 50 to 20
                            max_buy_volume -= buy_amount

                # -------------------------------------------------------------
                # STEP 3 — SCAN THE BUY SIDE: FIND EXPENSIVE BUYERS (SELL OPPORTUNITY)
                # -------------------------------------------------------------
                # buy_orders shows what other traders are WILLING to pay.
                # We want to find the HIGHEST bid price (most generous buyer).
                #
                # max(buy_orders.keys()) gives the highest bid.
                #
                # Decision rule:
                #   If highest_bid > 10000 → someone is paying ABOVE fair value
                #   → We sell to them immediately and lock in a profit.
                #
                # Example:
                #   buy_orders = {10003: 15, 9999: 40}
                #   best_bid_price = max(10003, 9999) = 10003
                #   10003 > 10000 → SELL! We earn 3 SeaShells per unit above fair value.
                # -------------------------------------------------------------
                if len(order_depth.buy_orders) > 0:

                    best_bid_price = max(order_depth.buy_orders.keys())

                    if best_bid_price > 10001:  # <-- TRY CHANGING 10000 to 10001 and see what happens!

                        # How many units does this buyer want?
                        # buy_orders have POSITIVE volumes.
                        available_volume = order_depth.buy_orders[best_bid_price]

                        # We can sell at most:
                        #   (a) what the buyer wants, AND
                        #   (b) our remaining sell capacity (abs because it's negative)
                        #
                        # Example: available_volume=15, abs(max_sell_volume)=80 → sell 15
                        sell_amount_positive = min(abs(max_sell_volume), available_volume)

                        if sell_amount_positive > 0:
                            print(f"  >> EXPENSIVE BID found! Selling {sell_amount_positive} units @ {best_bid_price}")

                            # Create a SELL order:
                            #   NEGATIVE quantity = SELL  (this is how the exchange knows it's a sell)
                            sell_order = Order(product, best_bid_price, -sell_amount_positive)
                            orders.append(sell_order)

                            # Update sell capacity — we've used some of it
                            max_sell_volume += sell_amount_positive

            # -----------------------------------------------------------------
            # ATTACH ORDERS FOR THIS PRODUCT TO THE RESULT PAYLOAD
            # -----------------------------------------------------------------
            # After processing one product, we store its orders in the result
            # dictionary using the product name as the key.
            #
            # Example after this line:
            #   result = {"RAINFOREST_RESIN": [Order(...buy...), Order(...sell...)]}
            # -----------------------------------------------------------------
            result[product] = orders

        # =====================================================================
        # RETURN VALUES (REQUIRED BY THE ENGINE)
        # =====================================================================
        # The competition engine expects EXACTLY 3 return values:
        #
        #   1. result       (dict)  — your orders per product
        #   2. conversions  (int)   — used in later rounds for currency conversion;
        #                             just use 1 for now
        #   3. traderData   (str)   — a string you can use to pass information
        #                             from one timestep to the next (like a memo)
        #                             In later rounds you'll store things like
        #                             "my last mid price was 10002" here.
        #
        # EXPERIMENT IDEA:
        #   Change traderData to something like f"pos={current_position}"
        #   and watch it appear in the logs!
        # =====================================================================
        traderData = "LESSON1_BOT_RUNNING"
        conversions = 1

        return result, conversions, traderData
