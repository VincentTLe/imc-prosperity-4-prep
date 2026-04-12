# Round 4 - MACARONS: A Beginner Guide to Cross-Exchange Arbitrage

> **Prerequisite:** Read `General_EN.md` first.
> You should also understand order books, position limits, and the idea of fair value from Round 1.

---

# PART 1: WHAT MAKES MACARONS DIFFERENT?

---

## 1. What Are MACARONS?

`MAGNIFICENT_MACARONS` are traded on **two markets**:

- the internal Prosperity exchange
- an external exchange shown through observations

That means you are not just comparing buy and sell prices inside one book.
You are comparing:

- what you can get internally
- what you can get externally
- whether converting between the two still leaves profit after fees

This is cross-exchange arbitrage.

---

## 2. Why This Round Is Interesting

Round 4 is not mainly about prediction.
It is about **price conversion math**.

If one market is cheaper than the other by more than the conversion cost, you can buy in the cheap market and sell in the expensive one.

In plain English:

> If the spread is bigger than the fees, trade.

That is the whole round in one sentence.

---

## 3. The Core Decision

For each tick, ask:

1. What is the best internal buy price?
2. What is the best internal sell price?
3. What is the effective cost to import or export through conversion?
4. Is there enough profit left after fees?

If yes:

- convert and trade

If no:

- do nothing

Frankfurt Hedgehogs' style here was practical:

- compute the conversion cost directly
- only trade when the gap beats the fees
- keep the logic small and explicit

---

# PART 2: UNDERSTANDING CONVERSION

---

## 4. What Is Conversion?

Conversion is moving product between exchanges.

Think of it like this:

- buy macarons in the cheaper market
- move them across the border
- sell them in the more expensive market

But movement is not free.
You pay:

- transport fees
- import tariff or export tariff

So your real cost is not just the visible price.

---

## 5. The Useful Formula

For an import-style trade:

```text
effective import cost = external ask + transport fees + import tariff
```

For an export-style trade:

```text
effective export value = external bid - transport fees - export tariff
```

Beginner version:

- compare internal prices to these effective values
- only trade if the difference is comfortably positive

---

# PART 3: A SIMPLE MACARONS TRADER

---

## 6. Basic Strategy

The simplest safe approach is:

- if internal buy price is above effective import cost, sell internally and convert from outside
- if internal sell price is below effective export value, buy internally and convert out

That sounds complicated, but it is just arbitrage in two directions.

---

## 7. Example Code

```python
from datamodel import Order, OrderDepth, TradingState


def import_cost(obs) -> float:
    return obs.askPrice + obs.transportFees + obs.importTariff


def export_value(obs) -> float:
    return obs.bidPrice - obs.transportFees - obs.exportTariff


class Trader:
    def run(self, state: TradingState):
        product = "MAGNIFICENT_MACARONS"
        orders = []
        conversions = 0
        limit = 75
        min_profit = 2.0

        depth = state.order_depths.get(product, OrderDepth())
        if product not in state.observations.conversionObservations:
            return {product: orders}, conversions, ""

        obs = state.observations.conversionObservations[product]
        position = state.position.get(product, 0)
        buy_capacity = limit - position
        sell_capacity = limit + position

        if depth.buy_orders:
            best_bid = max(depth.buy_orders.keys())
            effective_cost = import_cost(obs)
            profit = best_bid - effective_cost

            if profit > min_profit and sell_capacity > 0:
                qty = min(sell_capacity, depth.buy_orders[best_bid])
                if qty > 0:
                    orders.append(Order(product, best_bid, -qty))
                    conversions += qty

        if depth.sell_orders:
            best_ask = min(depth.sell_orders.keys())
            effective_value = export_value(obs)
            profit = effective_value - best_ask

            if profit > min_profit and buy_capacity > 0:
                qty = min(buy_capacity, abs(depth.sell_orders[best_ask]))
                if qty > 0:
                    orders.append(Order(product, best_ask, qty))
                    conversions -= qty

        return {product: orders}, conversions, ""
```

### What this code is doing

- Reads the internal order book.
- Reads the external conversion observation.
- Calculates whether importing or exporting is profitable.
- Trades only when profit clears a small threshold.
- Keeps position within limits.

---

## 8. Why the Threshold Matters

The threshold protects you from noise.

If your edge is only 0.2 after fees, that is not a real trade.
One bad fill or one small modeling error can erase it.

Frankfurt Hedgehogs were careful here.
They did not trade every tiny mismatch.
They waited for actual arbitrage.

That is the right beginner habit too.

---

# PART 4: WORKING WITH THE EXTERNAL DATA

---

## 9. Where the External Prices Come From

The external market data is available through:

- `state.observations.conversionObservations`

That observation contains the values you need for:

- external bid
- external ask
- transport fees
- import tariff
- export tariff

Do not guess these numbers.
Read them every tick.

---

## 10. A Helpful Mental Model

Think of the external exchange as a second whiteboard.

Internal board:

- buyers and sellers inside Prosperity

External board:

- buyers and sellers outside Prosperity

Your job is to compare the two boards after conversion costs.

If the difference is positive enough, trade.

If not, wait.

---

# PART 5: WALK THROUGH AN EXAMPLE

---

## 11. Example Tick

Suppose:

- internal best bid = 10,120
- external effective import cost = 10,110
- internal best ask = 10,090
- external effective export value = 10,100

Then:

- selling internally after importing from outside makes 10 profit before risk
- buying internally and exporting out makes 10 profit before risk

If your threshold is 2, both look attractive.

If your threshold is 15, neither should trade.

That is a good example of why the threshold is a policy choice.

---

## 12. Position Control

Macarons have a position limit.

That means you cannot just keep converting forever.

Before placing orders, compute:

```text
buy_capacity = limit - current_position
sell_capacity = limit + current_position
```

This prevents limit violations and keeps the bot stable.

---

# PART 6: COMMON MISTAKES

---

## 13. Mistakes Beginners Make

1. Forgetting conversion fees.
2. Trading on raw external price instead of effective price.
3. Ignoring position limits.
4. Treating tiny edges as real arbitrage.
5. Using external red herring data instead of actual price signals.

One especially important lesson from the Frankfurt material:

- sunlight and humidity looked interesting
- but they were not the main edge
- price difference after fees was the real signal

Do not overfit to decorative variables.

---

## 14. Beginner Roadmap

Start with this order:

1. Read internal order book.
2. Read external conversion observation.
3. Compute import cost and export value.
4. Compare against best internal prices.
5. Trade only when profit clears a threshold.
6. Add more careful inventory handling later.

That is enough for a working first bot.

---

*Based on the Round 4 training material and Frankfurt Hedgehogs' cross-exchange approach: compare effective prices, trade only after fees, and keep the logic simple.*
