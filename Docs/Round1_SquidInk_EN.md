# Round 1 - SQUID_INK: Follow the Signal, Not the Noise

> **Prerequisite:** You have already read the General Guide and the KELP guide.
> If not, please read `General_EN.md` and `Round1_Kelp_EN.md` first.

---

# PART 1: UNDERSTANDING SQUID_INK

---

## 1. What is SQUID_INK?

In Round 1 of IMC Prosperity 4, you will trade 3 products:

| Product | Difficulty | Characteristic |
|---------|-----------|----------------|
| RAINFOREST_RESIN | Easiest | Fair value is fixed = 10,000 |
| KELP | Medium | Fair value changes continuously |
| **SQUID_INK** | Hardest | Fair value and signals are noisier |

SQUID_INK is the product where the market stops being "just compare to a clean fair value."

Instead, you start asking:

> "Is there a repeated behavior I can follow?"

Frankfurt Hedgehogs' writeup and the study notes point to the same core lesson:

- some traders leave directional footprints
- if you can recognize those footprints, you can trade with them
- if the signal needs memory, store it in `traderData`

This guide uses a beginner-friendly version of that idea:

- watch the day's running low and high
- look for a 15-lot trade at one of those extremes
- remember the signal across ticks
- move toward the matching position target

That is the whole lesson in one sentence:

> Do not predict everything. Detect one reliable signal and follow it.

**Position Limit: +-50 units**

---

## 2. Why is SQUID_INK Harder?

KELP is hard because the fair value moves.

SQUID_INK is harder because the market can be noisy, fast, and directionally deceptive.

You usually do not want to:

- guess a perfect top
- guess a perfect bottom
- overtrade every wiggle

You want to:

1. detect a pattern that matters
2. remember it
3. act only when the signal is strong enough

Frankfurt Hedgehogs' real advantage here was not "magic prediction."
It was disciplined signal extraction.

### The teaching version of that idea

In this lesson, the signal is:

- if a 15-lot trade happens at the day's low, treat it as a buy signal
- if a 15-lot trade happens at the day's high, treat it as a sell signal

That is a simplified proxy for the kind of directional counterparty reasoning Frankfurt used.

---

# PART 2: BASIC STRATEGY - USE MEMORY AND FOLLOW THE EXTREME

---

## 3. Core Idea: The Signal Matters More Than the Last Price

The basic strategy is not:

- "buy because price went down"
- "sell because price went up"

The basic strategy is:

- track the running low and running high for the day
- notice when a large trade happens exactly at one of those extremes
- treat that as a directional clue
- hold the signal until the market invalidates it

That is much closer to how a real signal-based bot should think.

Frankfurt Hedgehogs used persisted state to make this kind of logic durable across ticks. That is why `traderData` matters here.

---

## 4. Step-by-Step Code - Building the SQUID_INK Bot

Here is the full beginner-friendly bot from the lesson:

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List
import json


class Trader:
    PRODUCT = "SQUID_INK"
    POSITION_LIMIT = 50
    SIGNAL_TRADE_SIZE = 15
    DAY_LENGTH = 1_000_000

    def get_day_index(self, timestamp: int) -> int:
        return timestamp // self.DAY_LENGTH

    def load_memory(self, state: TradingState) -> dict:
        if not state.traderData:
            return {}

        try:
            memory = json.loads(state.traderData)
            if isinstance(memory, dict):
                return memory
        except Exception:
            pass

        return {}

    def save_memory(self, memory: dict) -> str:
        return json.dumps(memory, separators=(",", ":"))

    def start_new_day_memory(self, day_index: int) -> dict:
        return {
            "day_index": day_index,
            "running_low": None,
            "running_high": None,
            "signal_side": 0,
            "signal_price": None,
        }

    def get_best_bid_ask(self, order_depth: OrderDepth):
        best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
        return best_bid, best_ask

    def update_running_extremes(self, memory: dict, trades) -> None:
        running_low = memory["running_low"]
        running_high = memory["running_high"]

        for trade in trades:
            price = trade.price
            if running_low is None or price < running_low:
                running_low = price
            if running_high is None or price > running_high:
                running_high = price

        memory["running_low"] = running_low
        memory["running_high"] = running_high

    def detect_extreme_signal(self, memory: dict, trades) -> None:
        running_low = memory["running_low"]
        running_high = memory["running_high"]

        if running_low is None or running_high is None:
            return

        if running_low == running_high:
            return

        for trade in trades:
            if abs(trade.quantity) != self.SIGNAL_TRADE_SIZE:
                continue

            if trade.price == running_low:
                memory["signal_side"] = 1
                memory["signal_price"] = trade.price
            elif trade.price == running_high:
                memory["signal_side"] = -1
                memory["signal_price"] = trade.price

    def invalidate_stale_signal(self, memory: dict) -> None:
        signal_side = memory.get("signal_side", 0)
        signal_price = memory.get("signal_price")
        running_low = memory.get("running_low")
        running_high = memory.get("running_high")

        if signal_side == 1 and signal_price is not None:
            if running_low is not None and running_low < signal_price:
                memory["signal_side"] = 0
                memory["signal_price"] = None
        elif signal_side == -1 and signal_price is not None:
            if running_high is not None and running_high > signal_price:
                memory["signal_side"] = 0
                memory["signal_price"] = None

    def trade_towards_target(self, product: str, order_depth: OrderDepth, current_position: int, target_position: int) -> List[Order]:
        orders: List[Order] = []
        best_bid, best_ask = self.get_best_bid_ask(order_depth)
        position_gap = target_position - current_position

        if position_gap > 0 and best_ask is not None:
            buy_volume = min(position_gap, abs(order_depth.sell_orders[best_ask]))
            if buy_volume > 0:
                orders.append(Order(product, best_ask, buy_volume))
        elif position_gap < 0 and best_bid is not None:
            sell_volume = min(-position_gap, order_depth.buy_orders[best_bid])
            if sell_volume > 0:
                orders.append(Order(product, best_bid, -sell_volume))

        return orders

    def run(self, state: TradingState):
        memory = self.load_memory(state)
        current_day = self.get_day_index(state.timestamp)

        if memory.get("day_index") != current_day:
            memory = self.start_new_day_memory(current_day)
        else:
            memory.setdefault("running_low", None)
            memory.setdefault("running_high", None)
            memory.setdefault("signal_side", 0)
            memory.setdefault("signal_price", None)

        result = {}

        for product in state.order_depths:
            orders: List[Order] = []

            if product == self.PRODUCT:
                order_depth = state.order_depths[product]
                recent_trades = state.market_trades.get(product, [])

                self.update_running_extremes(memory, recent_trades)
                self.detect_extreme_signal(memory, recent_trades)
                self.invalidate_stale_signal(memory)

                signal_side = memory.get("signal_side", 0)
                target_position = {
                    1: self.POSITION_LIMIT,
                    -1: -self.POSITION_LIMIT,
                }.get(signal_side, 0)

                current_position = state.position.get(product, 0)
                orders = self.trade_towards_target(
                    product,
                    order_depth,
                    current_position,
                    target_position,
                )

            result[product] = orders

        traderData = self.save_memory(memory)
        conversions = 1
        return result, conversions, traderData
```

### DETAILED Explanation of the Important Parts:

**Imports**

```python
import json
```

This is the key difference from KELP.
SQUID_INK needs memory, so we serialize and deserialize `traderData`.

**Constants**

```python
PRODUCT = "SQUID_INK"
POSITION_LIMIT = 50
SIGNAL_TRADE_SIZE = 15
DAY_LENGTH = 1_000_000
```

- `PRODUCT` keeps the bot focused
- `POSITION_LIMIT` is the risk cap
- `SIGNAL_TRADE_SIZE` defines the trade size we care about
- `DAY_LENGTH` lets us reset the daily memory cleanly

**Memory loading**

```python
memory = json.loads(state.traderData)
```

That is the whole point of `traderData`:

- the game gives you a string
- you store structured state in it
- the state survives into the next tick

**Running extremes**

```python
if running_low is None or price < running_low:
    running_low = price
```

and

```python
if running_high is None or price > running_high:
    running_high = price
```

This keeps the day-long low and high updated every tick.

**Signal detection**

```python
if abs(trade.quantity) != self.SIGNAL_TRADE_SIZE:
    continue
```

We only care about the specific trade size that the lesson uses as a clue.

**Signal invalidation**

If a new low appears after a buy-at-low signal, the old signal is stale.
If a new high appears after a sell-at-high signal, the old signal is stale.

That keeps the bot from clinging to an outdated setup.

**Target-based execution**

```python
target_position = {
    1: self.POSITION_LIMIT,
    -1: -self.POSITION_LIMIT,
}.get(signal_side, 0)
```

This is the simplest possible signal-following rule:

- buy signal -> go max long
- sell signal -> go max short
- no signal -> go back toward flat

---

## 5. Walking Through One Tick

Suppose the day has seen these trades:

- 5020
- 5008
- 4995
- 5031

Now a 15-lot trade prints exactly at 4995.

Step by step:

1. running low becomes 4995
2. running high becomes 5031
3. the 15-lot trade at 4995 matches the low
4. the bot sets `signal_side = 1`
5. the target position becomes `+50`
6. the bot buys toward the long limit

If later a new higher high appears and the signal becomes stale, the bot clears it.

That is the difference between a one-tick reaction and a persistent signal-based strategy:

- one-tick reaction forgets too quickly
- persistent memory keeps the signal alive until it is invalidated

---

## 6. Limitations of the Basic Strategy

This version is intentionally simple.

### 6.1. It uses a simplified signal

The lesson turns a complicated directional idea into a clean daily-extreme rule.

### 6.2. It does not inspect every possible counterparty pattern

Frankfurt Hedgehogs' real logic was more detailed than this teaching version.

### 6.3. It only moves toward one target

That is good for learning, but not the final word on SQUID_INK execution.

### 6.4. It can hold a signal too long if the market regime changes

That is why signal invalidation matters, and why better versions need stronger filters.

### 6.5. It is still explainable

That is the important part:

- there is a reason for every state update
- there is a reason for every target
- there is a reason for every trade

---

# PART 3: LEVELING UP - LEARNING FROM FRANKFURT HEDGEHOGS

---

## 7. Why `traderData` Is the Real Upgrade

Frankfurt Hedgehogs understood that some signals do not fit in one tick.

That is why `traderData` matters:

- it lets you remember what you saw
- it lets you carry a signal forward
- it lets you update your view without starting from zero each tick

In SQUID_INK, memory is part of the edge.

Without memory, you can only react.
With memory, you can follow a regime.

---

## 8. Daily Extremes as a Beginner Signal

The lesson uses running lows and highs because they are easy to understand.

Why does this help?

- a repeated trade at the day low suggests someone wants to buy there
- a repeated trade at the day high suggests someone wants to sell there
- that creates a directional bias you can follow

This is not the only possible SQUID_INK signal.
It is just the cleanest one to learn first.

The Frankfurt lesson here is the same as in the other products:

- do not overcomplicate the first version
- make the signal obvious
- only then consider a stronger model

---

## 9. Persistent State vs Stateless Reaction

This is the most important conceptual difference from Resin and KELP.

Resin:

- no memory needed
- fair value is fixed

KELP:

- no memory needed for the first version
- fair value is recomputed every tick

SQUID_INK:

- memory matters
- the signal must survive from one tick to the next

That is why the code:

1. loads memory
2. updates it
3. uses it for trading
4. saves it back

This is the smallest possible example of stateful trading logic.

---

## 10. Follow the Signal, Then Control Risk

Frankfurt Hedgehogs did not just "buy because it looked bullish."
They paired the signal with execution discipline.

In the lesson bot, the discipline is:

- if the signal says long, move toward +50
- if the signal says short, move toward -50
- if the signal disappears, move back toward zero

That makes the bot easy to reason about.
It also keeps the position from drifting without purpose.

---

## 11. Why Frankfurt Hedgehogs Won

The broader Frankfurt lesson is:

### Principle 1: Find a repeatable signal

Do not invent a signal just because it is clever.

### Principle 2: Remember it properly

If the signal spans ticks, persist it in `traderData`.

### Principle 3: Trade with discipline

Turn the signal into a clear target, not a vague guess.

### Principle 4: Invalidate stale ideas

A signal that is no longer supported should be cleared.

### Principle 5: Keep it explainable

If you cannot explain why the bot should buy or sell, the logic is too weak.

That is why this SQUID_INK guide stays simple.

---

# PART 4: NEXT STEPS

---

## 12. Summary of What You Learned

You now have the Round 1 SQUID_INK teaching bot:

1. Track the day's running low and high
2. Look for a 15-lot trade at one of those extremes
3. Persist the signal in `traderData`
4. Trade toward a position target based on the signal
5. Clear the signal when the setup becomes stale

### Concepts Covered

| # | Concept | Meaning |
|---|---------|---------|
| 1 | Signal trading | Follow a reliable pattern instead of every price move |
| 2 | Running extremes | Track the day's low and high |
| 3 | Memory in `traderData` | Carry signal state across ticks |
| 4 | Signal invalidation | Clear stale setups when the market changes |
| 5 | Target execution | Translate signal into a clear position goal |

---

## 13. Practice Exercises

Try these one at a time:

### Exercise 1: Print the memory

Print `running_low`, `running_high`, and `signal_side` every tick.

### Exercise 2: Change the signal size

Try `SIGNAL_TRADE_SIZE = 10` or `20` and see how much noisier the strategy becomes.

### Exercise 3: Remove invalidation

Comment out `invalidate_stale_signal()` and see what happens when the market regime changes.

### Exercise 4: Add a neutral zone

Instead of jumping straight to `+50` or `-50`, try targeting `+25` and `-25` first.

### Exercise 5: Reset memory more carefully

Experiment with different day boundaries and observe how the bot behaves around a new day.

---

## 14. Coming Next: Putting Round 1 Together

At this point, Round 1 is complete:

- Resin taught you fixed fair value
- KELP taught you moving fair value
- SQUID_INK taught you signal memory

If you understand those three ideas, you understand the foundation of the whole round.

> **Next step:** combine these lessons into your own first full Round 1 trader.

---

*Based on Lesson 3 + Frankfurt Hedgehogs strategy notes (Top 2, Prosperity 3). Updated for Prosperity 4.*
