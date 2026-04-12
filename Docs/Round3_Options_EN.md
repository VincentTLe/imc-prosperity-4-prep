# Round 3 - OPTIONS: Your First Black-Scholes Trading Guide

> **Prerequisite:** Read `General_EN.md` first, and ideally understand the Round 1 Resin guide.
> Options are much easier once you already know how to read an order book and think in fair value.

---

# PART 1: WHAT ARE OPTIONS?

---

## 1. What is an Option?

An option is a contract that gives you the **right**, but not the obligation, to buy or sell something later at a fixed price.

In Prosperity, the important product is:

- `VOLCANIC_ROCK` = the underlying asset
- `VOLCANIC_ROCK_VOUCHERS` = the option contract

Think of a voucher like a movie ticket:

- If the movie becomes very popular, the ticket is worth more than you paid.
- If the movie becomes unpopular, the ticket may still be worth something, but less.

That is the basic idea of an option:

- If the underlying goes up, a call option usually becomes more valuable.
- If time passes, the option loses value.
- If volatility is higher, the option is usually worth more.

The Frankfurt Hedgehogs style in options was simple:

1. Estimate fair option value.
2. Compare market price to fair value.
3. Buy when the option is cheap.
4. Sell when the option is expensive.
5. Hedge the underlying risk if needed.

---

## 2. Why Options Feel Hard

Options are harder than Resin because the fair value is not fixed.

You do **not** get to say "this product is always worth 10,000" and stop there.

Instead, option value depends on:

- underlying spot price
- strike price
- time to expiry
- volatility
- interest rate

That sounds scary, but the useful beginner version is simple:

> Compute model value, compare to market, trade the difference.

That is the whole game.

---

## 3. The Core Idea

The market gives you a price for the voucher.
Your job is to decide whether that price is:

- too cheap, or
- too expensive

If the market price is below your model price:

- buy the voucher

If the market price is above your model price:

- sell the voucher

The model most teams used for the first pass is **Black-Scholes**.

---

# PART 2: BLACK-SCHOLES, WITHOUT THE PAIN

---

## 4. The Only Formula You Really Need

For a European call option:

```text
C = S * N(d1) - K * exp(-rT) * N(d2)
```

Where:

- `C` = option price
- `S` = spot price of the underlying
- `K` = strike price
- `T` = time to expiry
- `r` = risk-free rate
- `sigma` = volatility
- `N(x)` = normal CDF

And:

```text
d1 = [ln(S / K) + (r + sigma^2 / 2) * T] / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)
```

If that feels like too much, remember the beginner interpretation:

- higher `S` means the option is worth more
- higher `K` means the option is worth less
- higher `sigma` means the option is worth more
- more time means the option is worth more

That is the intuition you need before coding.

---

## 5. A Practical Trading Rule

Use a model fair value and a small edge threshold.

Example:

- if market ask is at least 2 below model value, buy
- if market bid is at least 2 above model value, sell

This avoids overtrading on tiny noise.

For beginners, the rule should look like this:

```text
if market_price < fair_value - edge:
    buy
elif market_price > fair_value + edge:
    sell
```

Keep the logic boring and robust.

---

# PART 3: BUILDING A SIMPLE OPTIONS BOT

---

## 6. First Bot: Compare Market Price to Model Price

Below is a small beginner-friendly pattern. It is not the full competition solution, but it shows the structure clearly.

```python
from datamodel import Order, OrderDepth, TradingState
from typing import List
import math


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K)

    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


class Trader:
    def run(self, state: TradingState):
        orders = []

        product = "VOLCANIC_ROCK_VOUCHERS"
        underlying = "VOLCANIC_ROCK"
        limit = 100
        edge = 2.0

        if product not in state.order_depths or underlying not in state.order_depths:
            return {product: orders}, 0, ""

        voucher_depth = state.order_depths[product]
        rock_depth = state.order_depths[underlying]

        if not voucher_depth.buy_orders or not voucher_depth.sell_orders:
            return {product: orders}, 0, ""

        if not rock_depth.buy_orders or not rock_depth.sell_orders:
            return {product: orders}, 0, ""

        spot = (max(rock_depth.buy_orders.keys()) + min(rock_depth.sell_orders.keys())) / 2
        market_bid = max(voucher_depth.buy_orders.keys())
        market_ask = min(voucher_depth.sell_orders.keys())
        model_value = black_scholes_call(spot, K=10000, T=0.02, r=0.0, sigma=0.16)

        position = state.position.get(product, 0)
        buy_capacity = limit - position
        sell_capacity = limit + position

        if market_ask < model_value - edge and buy_capacity > 0:
            qty = min(buy_capacity, abs(voucher_depth.sell_orders[market_ask]))
            if qty > 0:
                orders.append(Order(product, market_ask, qty))

        if market_bid > model_value + edge and sell_capacity > 0:
            qty = min(sell_capacity, voucher_depth.buy_orders[market_bid])
            if qty > 0:
                orders.append(Order(product, market_bid, -qty))

        return {product: orders}, 0, ""
```

### What this bot does

- Uses Black-Scholes to estimate voucher fair value.
- Uses the underlying `VOLCANIC_ROCK` to estimate spot price.
- Buys vouchers when the market is cheap.
- Sells vouchers when the market is expensive.
- Respects position limits.

---

## 7. Why This Works

Options traders usually do not need perfect pricing.

They need:

- a decent fair value estimate
- a consistent edge filter
- good risk control

If the market is selling vouchers below your model value, you have a positive expected edge.
If it is buying them above your model value, you can sell into that edge.

Frankfurt Hedgehogs were strong here because they stayed disciplined:

- use model value
- trade only meaningful mispricings
- do not chase every tick

That is the right beginner mindset too.

---

# PART 4: SIMPLE HEDGING INTUITION

---

## 8. Why Hedging Matters

Options are not just about betting on price.
They are also about managing risk.

If you buy a call option, your position usually gains when the underlying rises.
But if the underlying moves too much in one direction, the option's value changes because of **delta**.

Beginner version:

- long option = you have directional exposure
- hedge = offset some of that exposure with the underlying

If you ignore hedging completely, you may be right on valuation but still lose money from a bad price move.

---

## 9. A Simple Delta Hedge Shape

Do not overcomplicate this at first.

The basic idea is:

```text
if you are long options and delta is positive:
    sell some underlying

if you are short options and delta is negative:
    buy some underlying
```

That reduces the effect of a small spot move.

For a first bot, it is fine to start with:

- trade options only
- add hedging later

But if you want to improve quickly, hedging is the next thing to learn.

---

# PART 5: WALK THROUGH AN EXAMPLE

---

## 10. Example Tick

Suppose:

- `VOLCANIC_ROCK` spot is about `10,000`
- your Black-Scholes model says the voucher should be worth `90`
- the market asks `82`
- the market bids `96`

Then:

- market ask `82 < 90 - 2` -> buy
- market bid `96 > 90 + 2` -> sell

That means the market is offering both sides with enough edge to trade.

The only question left is position and risk limits.

---

## 11. What Goes in traderData?

Options often benefit from persistence.

Use `traderData` for small saved state such as:

- previous spot estimate
- rolling volatility estimate
- last model price
- hedge inventory

Keep it small and JSON-safe.

Do **not** store huge arrays blindly.

---

# PART 6: COMMON MISTAKES

---

## 12. Mistakes That Waste Time

1. Using a fixed price instead of a model price.
2. Forgetting that time to expiry changes every tick.
3. Ignoring the underlying and trading vouchers blind.
4. Overtrading tiny mispricings with no edge threshold.
5. Forgetting to manage position limits.
6. Treating Black-Scholes as magic instead of a model.

The model is not the strategy.
The strategy is:

- estimate value
- compare to market
- trade the difference

---

## 13. Beginner Roadmap

If you are starting from zero:

1. Implement `norm_cdf()`.
2. Implement `black_scholes_call()`.
3. Read both order books.
4. Compute model value.
5. Trade only when the edge is large enough.
6. Add hedging after the core loop works.

That is enough to get a working first version.

---

*Based on the Round 3 training material and Frankfurt Hedgehogs' options approach: model fair value, trade mispricings, and keep risk controlled.*
