# Round 1 - KELP: Your First Moving Fair Value Bot

> **Prerequisite:** You have already read the General Guide (Order Book, Tick, TradingState, `run()`, etc.).
> If not, please read `General_EN.md` first.

---

# PART 1: UNDERSTANDING KELP

---

## 1. What is KELP?

In Round 1 of IMC Prosperity 4, you will trade 3 products:

| Product | Difficulty | Characteristic |
|---------|-----------|----------------|
| RAINFOREST_RESIN | Easiest | Fair value is fixed = 10,000 |
| **KELP** | Medium | Fair value changes continuously |
| SQUID_INK | Hardest | Fair value is harder to infer |

KELP is the first product where you cannot just hardcode one magic number and call it a day.

With Resin, the fair value never changes. With KELP, the fair value moves over time, so your bot must estimate it again every tick.

Think of it like this:

> **Imagine a shop where the "correct" price moves during the day.**
>
> Sometimes the fair price is 2,050.
> A few ticks later it is 2,058.
> Then 2,046.
>
> If you keep using yesterday's number, you will trade badly.
> If you re-read the order book every tick, you stay close to the real value.

The key lesson for KELP is simple:

1. Estimate fair value from the book
2. Buy when the market offers KELP below fair value
3. Sell when the market bids above fair value
4. Keep your inventory under control

**Position Limit: +-50 units**

That means:
- Maximum long: +50
- Maximum short: -50

---

## 2. Why is KELP Harder Than Resin?

Resin is easy because you already know the answer: 10,000.

KELP is harder because you have to answer a new question every tick:

> "What is the fair value right now?"

The market gives you clues. Frankfurt Hedgehogs used a very teachable idea called **wall mid**:

- find the outer wall on the bid side
- find the outer wall on the ask side
- average them

That gives you a smooth estimate of fair value that reacts to the current order book.

### Resin vs KELP

```
Resin:
  Fair value = 10000, always flat

KELP:
  Fair value = moving line that changes with the book
```

If you understand this one difference, you understand the whole product:

- Resin: "compare everything to 10,000"
- KELP: "compare everything to the current wall mid"

> **Important:** Frankfurt Hedgehogs treated KELP as a market-making problem, not a prediction contest. Their advantage came from reading the book well, pricing fair value well, and controlling inventory well.

---

# PART 2: BASIC STRATEGY - WALL MID + TAKING + MAKING

---

## 3. Core Idea: Trade Around Fair Value

The beginner strategy is:

1. Compute fair value
2. Take obvious mispricings
3. Place passive orders near the fair value

In plain English:

- If someone is selling much cheaper than fair value, buy it
- If someone is buying much more expensive than fair value, sell it
- If nothing is clearly mispriced, quote near fair value and wait

This is the same basic market-making rhythm Frankfurt Hedgehogs used:

- **take** profitable orders that are already there
- **make** new orders that sit just inside the book
- **flatten** inventory when it gets too large

---

## 4. Step-by-Step Code - Building the KELP Bot

Here is the full beginner-friendly bot from the lesson:

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional, Tuple


class Trader:
    POSITION_LIMIT = 50
    TAKE_EDGE = 1
    FLATTEN_LEVEL = 40

    def _best_bid_ask(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[int]]:
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        return best_bid, best_ask

    def _wall_mid(self, order_depth: OrderDepth) -> Tuple[Optional[int], Optional[float], Optional[int]]:
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None, None, None

        bid_wall = min(order_depth.buy_orders.keys())
        ask_wall = max(order_depth.sell_orders.keys())
        fair_value = (bid_wall + ask_wall) / 2
        return bid_wall, fair_value, ask_wall

    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            orders: List[Order] = []

            if product != "KELP":
                result[product] = orders
                continue

            order_depth: OrderDepth = state.order_depths[product]
            current_position = state.position.get(product, 0)

            best_bid, best_ask = self._best_bid_ask(order_depth)
            bid_wall, fair_value, ask_wall = self._wall_mid(order_depth)

            if fair_value is None:
                result[product] = orders
                continue

            remaining_buy_capacity = max(0, self.POSITION_LIMIT - current_position)
            remaining_sell_capacity = max(0, self.POSITION_LIMIT + current_position)

            if best_ask is not None and best_ask <= fair_value - self.TAKE_EDGE:
                buy_volume = min(remaining_buy_capacity, abs(order_depth.sell_orders[best_ask]))
                if buy_volume > 0:
                    orders.append(Order(product, best_ask, buy_volume))
                    remaining_buy_capacity -= buy_volume

            if best_bid is not None and best_bid >= fair_value + self.TAKE_EDGE:
                sell_volume = min(remaining_sell_capacity, order_depth.buy_orders[best_bid])
                if sell_volume > 0:
                    orders.append(Order(product, best_bid, -sell_volume))
                    remaining_sell_capacity -= sell_volume

            if current_position >= self.FLATTEN_LEVEL:
                remaining_buy_capacity = 0
            if current_position <= -self.FLATTEN_LEVEL:
                remaining_sell_capacity = 0

            bid_price = bid_wall + 1
            ask_price = ask_wall - 1

            if best_bid is not None and best_bid + 1 < fair_value:
                bid_price = max(bid_price, best_bid + 1)
            if best_ask is not None and best_ask - 1 > fair_value:
                ask_price = min(ask_price, best_ask - 1)

            if remaining_buy_capacity > 0:
                orders.append(Order(product, int(bid_price), remaining_buy_capacity))
            if remaining_sell_capacity > 0:
                orders.append(Order(product, int(ask_price), -remaining_sell_capacity))

            result[product] = orders

        return result, 0, "LESSON2_KELP_BOT_RUNNING"
```

### DETAILED Explanation of the Important Parts:

**Imports**

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional, Tuple
```

- `OrderDepth` gives the order book
- `TradingState` gives the full market snapshot
- `Order` creates buy and sell orders
- `Optional` and `Tuple` help us describe helper return values cleanly

**Class constants**

```python
POSITION_LIMIT = 50
TAKE_EDGE = 1
FLATTEN_LEVEL = 40
```

- `POSITION_LIMIT` is the hard risk cap
- `TAKE_EDGE` says we only take obviously good prices
- `FLATTEN_LEVEL` is the point where we stop leaning harder in the same direction

**Wall mid**

```python
bid_wall = min(order_depth.buy_orders.keys())
ask_wall = max(order_depth.sell_orders.keys())
fair_value = (bid_wall + ask_wall) / 2
```

This is the Frankfurt Hedgehogs idea in its simplest form:

- the deepest bid tells you where buyers are still serious
- the deepest ask tells you where sellers are still serious
- averaging them gives a smoother fair value than using only best bid / best ask

**Taking**

```python
if best_ask is not None and best_ask <= fair_value - self.TAKE_EDGE:
```

If the cheapest ask is below fair value, buy it.

```python
if best_bid is not None and best_bid >= fair_value + self.TAKE_EDGE:
```

If the best bid is above fair value, sell into it.

**Making**

```python
bid_price = bid_wall + 1
ask_price = ask_wall - 1
```

These are passive quotes that sit just inside the visible book.

The goal is not to be clever. The goal is to stay near fair value and give other bots a price to hit.

---

## 5. Walking Through One Tick

Suppose the book looks like this:

```text
Buy orders:  {2048: 20, 2046: 30}
Sell orders: {2058: -10, 2060: -20}
Current position: 0
```

Step by step:

1. `bid_wall = 2046`
2. `ask_wall = 2060`
3. `fair_value = (2046 + 2060) / 2 = 2053`
4. `best_ask = 2058`
5. `best_bid = 2048`

Now the bot checks:

- Is `2058 <= 2052`? No, so it does not take the ask
- Is `2048 >= 2054`? No, so it does not take the bid

Then it quotes:

- buy at `2047`
- sell at `2059`

That is the whole rhythm:

1. Estimate fair value
2. Take if the market is obviously wrong
3. Otherwise, quote just inside the book

---

## 6. Limitations of the Basic Strategy

This bot is good for learning, but it is still simple.

### 6.1. It depends on the book being visible on both sides

If one side is missing, the bot cannot compute wall mid and just waits.

### 6.2. It only uses a single fair value estimate

The real market may need more smoothing, but this version keeps the math easy.

### 6.3. It does not persist memory

That is fine for KELP. We do not need traderData for this lesson.

### 6.4. It only uses the top-level idea

It does not scan the whole book or build a more advanced inventory model.

### 6.5. Actual result

The important thing is not that the code is fancy. The important thing is that it is explainable:

- fair value comes from the book
- taking captures obvious edge
- making earns spread
- inventory stays controlled

---

# PART 3: LEVELING UP - LEARNING FROM FRANKFURT HEDGEHOGS

---

## 7. Why Wall Mid Matters

Frankfurt Hedgehogs did not use a blind midpoint. They used the book itself to estimate value.

Why is that better?

- the inside best bid and best ask can be distorted by tiny spoof-like orders
- the outer visible walls often give a more stable reference
- a better fair value means better taking decisions and better passive quotes

In other words:

- bad fair value -> bad quotes
- good fair value -> better pricing

That is why wall mid is the first upgrade over the Resin bot.

---

## 8. Taking + Making = Two Ways to Earn

The basic bot earns in two different ways:

### Phase 1: Taking

Buy cheap asks and sell expensive bids immediately.

### Phase 2: Making

Post passive orders around fair value and let other bots come to you.

This is exactly the Frankfurt mindset:

- do not wait for one perfect trade
- use both sides of the market
- let your orders work while you keep reading the book

If you only take, you miss spread.
If you only make, you may miss easy edge.
If you do both, you get a more robust bot.

---

## 9. Overbidding and Undercutting

Passive orders only matter if they get priority.

Frankfurt-style logic is:

- if the book is too weak on the bid side, improve the bid by 1 tick
- if the book is too weak on the ask side, improve the ask by 1 tick

That is what this part does:

```python
if best_bid is not None and best_bid + 1 < fair_value:
    bid_price = max(bid_price, best_bid + 1)

if best_ask is not None and best_ask - 1 > fair_value:
    ask_price = min(ask_price, best_ask - 1)
```

The point is not to cross the fair value blindly.
The point is to get in front of the current queue when it is still safe.

---

## 10. Inventory Flattening

This is one of the most important habits in trading.

If you become too long, stop adding more long inventory.
If you become too short, stop adding more short inventory.

That is why the lesson bot uses:

```python
if current_position >= self.FLATTEN_LEVEL:
    remaining_buy_capacity = 0
if current_position <= -self.FLATTEN_LEVEL:
    remaining_sell_capacity = 0
```

Frankfurt Hedgehogs were careful about this because good PnL is not enough if you get stuck at the position limit.

Good inventory control means:

- you can keep taking new opportunities
- you avoid being trapped on one side
- your bot behaves consistently over many ticks

---

## 11. How the Market Processes Your Orders

This is the key operational idea.

Every tick, the bot:

1. reads the book
2. computes fair value
3. places orders
4. those orders live for one tick
5. the next tick starts fresh

That means your making orders can be hit by later traders in the same tick.

So the passive quotes are not "dead money".
They are live opportunities.

---

## 12. Why Frankfurt Hedgehogs Won

Their KELP-style reasoning was strong because it was:

### Principle 1: Simple

They used a clear fair value estimate and a small number of rules.

### Principle 2: Stable

Wall mid is less noisy than a naive midpoint.

### Principle 3: Explainable

You can justify every order in plain English.

### Principle 4: Inventory-aware

They did not chase edge without respecting risk.

### Principle 5: Repeatable

The same logic works tick after tick.

That is the real lesson:

> A good KELP bot is not a prediction machine.
> It is a disciplined reader of the order book.

---

# PART 4: NEXT STEPS

---

## 13. Summary of What You Learned

You now have the KELP version of the Resin lesson:

```
Resin:
  Fair value = fixed number

KELP:
  Fair value = wall mid from the order book
```

The bot is built from four ideas:

1. Estimate fair value
2. Take obvious edge
3. Make passive quotes
4. Control inventory

That is enough to write a solid beginner KELP trader.

### Concepts Covered

| # | Concept | Meaning |
|---|---------|---------|
| 1 | Moving fair value | The right price changes every tick |
| 2 | Wall mid | Average of the visible bid and ask walls |
| 3 | Taking | Buy below fair value, sell above fair value |
| 4 | Making | Place passive orders near fair value |
| 5 | Overbid / undercut | Improve price by 1 tick for queue priority |
| 6 | Flattening | Stop adding risk when inventory gets large |

---

## 14. Practice Exercises

Try these one at a time:

### Exercise 1: Print wall mid

Add a print statement and check whether the fair value moves smoothly.

### Exercise 2: Change TAKE_EDGE

Try `TAKE_EDGE = 0` and `TAKE_EDGE = 2`.
See how often the bot takes orders.

### Exercise 3: Remove making

Comment out the passive bid/ask orders and compare results.

### Exercise 4: Move the flatten level

Try `FLATTEN_LEVEL = 30` and `FLATTEN_LEVEL = 45`.
Watch how inventory changes.

### Exercise 5: Change the quote offset

Try quoting `bid_wall + 2` and `ask_wall - 2`.
Ask yourself whether you still get fills.

---

## 15. Coming Next: SQUID_INK

After KELP, the next product is SQUID_INK.

KELP teaches you how to adapt to a moving fair value.
SQUID_INK teaches you how to follow a signal and remember it across ticks.

> **Next up:** Read `Round1_SquidInk_EN.md`.

---

*Based on Lesson 2 + Frankfurt Hedgehogs strategy (Top 2, Prosperity 3). Updated for Prosperity 4.*
