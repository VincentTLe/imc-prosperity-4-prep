# Round 1 — RAINFOREST_RESIN: Your First Trading Bot

> **Prerequisite:** You have already read the General Guide (Order Book, Tick, TradingState, `run()`, etc.).
> If not, please read General_EN.md first.

---

# PART 1: UNDERSTANDING RESIN

---

## 1. What is RAINFOREST_RESIN?

In Round 1 of IMC Prosperity 4, you will trade **3 products**:

| Product | Difficulty | Characteristic |
|---------|-----------|----------------|
| **RAINFOREST_RESIN** | Easiest | Fair value is fixed = 10,000 |
| KELP | Medium | Fair value changes continuously |
| SQUID_INK | Hardest | Fair value fluctuates wildly |

**RAINFOREST_RESIN** (called "Resin" for short) is the **EASIEST** product to trade. Why? Because its true value is **ALWAYS** exactly **10,000 XIRECs**. It never changes. Ever.

Think of it this way:

> **Imagine you're at a gold market:**
>
> There's a gold bar that **everyone knows** is worth exactly 10,000 coins. This price is written on a big sign in the middle of the market. Nobody argues about it.
>
> But in the market, some people are in a hurry and need cash fast — they sell the gold bar for 9,997 coins (3 coins cheaper).
> And some eager buyers are willing to pay 10,003 coins to buy right away (3 coins more expensive).
>
> **You're the smart person standing in the middle:**
> - See someone selling at 9,997 → BUY immediately (3 coins below value → profit of 3)
> - See someone buying at 10,003 → SELL immediately (3 coins above value → profit of 3)
>
> That's the entire Resin strategy. Really, that's all there is.

**The Golden Rule:**

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║   RESIN VALUE = 10,000 XIRECs (ALWAYS)           ║
║                                                  ║
║   → Buy BELOW 10,000 = PROFIT                   ║
║   → Sell ABOVE 10,000 = PROFIT                  ║
║   → Buy/Sell AT 10,000 = Break even              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

**Position Limit: ±50 units**

You can hold a maximum of **50 units** of Resin at any point in time. This means:
- Maximum: +50 (holding 50 units — "long")
- Minimum: -50 (owing 50 units — "short")

> **Example:** If you currently hold +30 Resin, you can only buy 20 more units (30 + 20 = 50).
> But you can sell up to 80 units (from +30, selling 80 gets you to -50).

---

## 2. Why is Resin the Easiest?

Let's compare the 3 products:

```
RAINFOREST_RESIN:
  Value: ──────────────────────── 10,000 ──────────────────────── (flat line)

KELP:
  Value: ~~~~/\~~~~\/~~~~~/\~~~~/\~~~~\/~~~~~  (gentle waves)

SQUID_INK:
  Value: ~~~/\~~\/~~~~/\\/\~~~~~/\/\~~\//\~~~  (wild waves)
```

With Resin, you **ALWAYS KNOW** the true value is 10,000. No calculations needed, no predictions, no worries. Just:

1. Is anyone selling below 10,000? → Buy
2. Is anyone buying above 10,000? → Sell

**It's that simple.**

With KELP, the value changes every tick — you have to **calculate** the true value before making decisions. With SQUID_INK, the value jumps unpredictably.

> **Important:** The Frankfurt Hedgehogs team (ranked #2 globally, Prosperity 3) earned approximately **~39,000 SeaShells/round** from Resin alone. "Easy" doesn't mean "low profit." It's your most stable income source.

---

# PART 2: BASIC STRATEGY — AGGRESSIVE TAKING (LESSON 1)

---

## 3. Core Idea: Buy Low, Sell High

This is the simplest idea in trading:

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   Someone SELLING below 10,000 → BUY now (cheaper than FV)  ║
║   Someone BUYING above 10,000 → SELL now (pricier than FV)  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

Let's slow down with an everyday example:

> **Imagine you sell orange juice:**
>
> You know a glass of orange juice is worth exactly **$5.00**.
>
> **Scenario 1:** Someone comes and says "I'll sell you this orange juice for $4.80."
> → You buy it immediately! Because you can resell it for $5.00 and profit $0.20.
>
> **Scenario 2:** Someone comes and says "I want to buy orange juice. I'll pay $5.20."
> → You sell immediately! Because you can buy another one for $5.00, profiting $0.20.
>
> **Scenario 3:** Someone says "I'll buy/sell at $5.00."
> → Do nothing. Price equals value → no profit.

In Prosperity, the "orange juice" is Resin, "$5.00" is 10,000 XIRECs, and the "buyers and sellers" are other bots in the market.

**Why does this strategy work?**

The Prosperity market has **market maker bots** — they always place buy/sell orders around 10,000. Sometimes, they place orders at imperfect prices (9,997 or 10,003), creating opportunities for you.

Additionally, there are **taker bots** — they buy/sell at any price, sometimes creating great opportunities.

---

## 4. Step-by-Step Code — Building Your First Bot

This is the most important section. We'll build a Resin trading bot **from scratch**, and I'll explain **EVERY SINGLE LINE** in detail.

### The Complete Bot:

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if product == "RAINFOREST_RESIN":
                # --- Configuration ---
                FAIR_VALUE = 10000
                LIMIT = 50

                # --- Step 1: Read current position ---
                current_pos = state.position.get(product, 0)
                max_buy = LIMIT - current_pos
                max_sell = LIMIT + current_pos

                # --- Step 2: Check sell side (look for BUY opportunities) ---
                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    if best_ask < FAIR_VALUE:
                        volume = abs(order_depth.sell_orders[best_ask])
                        buy_amount = min(max_buy, volume)
                        if buy_amount > 0:
                            orders.append(Order(product, best_ask, buy_amount))
                            max_buy -= buy_amount

                # --- Step 3: Check buy side (look for SELL opportunities) ---
                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    if best_bid > FAIR_VALUE:
                        volume = order_depth.buy_orders[best_bid]
                        sell_amount = min(max_sell, volume)
                        if sell_amount > 0:
                            orders.append(Order(product, best_bid, -sell_amount))
                            max_sell -= sell_amount

            result[product] = orders

        return result, 1, ""
```

### DETAILED Explanation of Every Line:

---

**Lines 1-2: Import libraries**

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List
```

- `OrderDepth`: Contains Order Book information (who's buying/selling at what price).
- `TradingState`: Contains ALL market information at the current moment (position, order book, recent trades, etc.).
- `Order`: Used to create your buy/sell orders.
- `List`: Python's list type.

> **If you skip this line?** The code will crash because Python doesn't know what `OrderDepth`, `TradingState`, or `Order` are.

---

**Lines 4-5: Declare the Trader class and run() method**

```python
class Trader:
    def run(self, state: TradingState):
```

- You **MUST** have a class named `Trader` with a method called `run()`.
- The Prosperity system calls `run()` every tick (100 times/second) and passes in `state` — all the market information.
- `self` is a required parameter for every Python class method. Don't worry about it.

> **If you rename the class?** The system can't find your bot → your bot doesn't run.

---

**Line 6: Create the result dictionary**

```python
        result = {}
```

`result` is a dictionary that will hold all your orders for EACH product. At the end, you return `result` to the system.

Structure of `result`:
```python
result = {
    "RAINFOREST_RESIN": [Order(...), Order(...), ...],
    "KELP": [Order(...), ...],
    "SQUID_INK": [Order(...), ...]
}
```

> **If you forget to create `result`?** Nothing to return → your bot places no orders.

---

**Lines 8-10: Loop through each product**

```python
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
```

- `state.order_depths` is a dictionary containing the Order Book for EVERY product.
- `for product in state.order_depths:` loops through each product (RAINFOREST_RESIN, KELP, SQUID_INK).
- `order_depth` is the Order Book for the current product. It contains:
  - `order_depth.sell_orders`: Dictionary {price: negative_quantity} — pending sell orders
  - `order_depth.buy_orders`: Dictionary {price: positive_quantity} — pending buy orders
- `orders` is your order list for this product (starts empty).

> **Concrete example:**
> ```python
> order_depth.sell_orders = {9997: -30, 10001: -20, 10002: -50}
> #  Price 9997: 30 units are being sold (negative = sell)
> #  Price 10001: 20 units are being sold
> #  Price 10002: 50 units are being sold
>
> order_depth.buy_orders = {9998: 50, 9999: 5, 10003: 15}
> #  Price 9998: someone wants to buy 50 units (positive = buy)
> #  Price 9999: someone wants to buy 5 units
> #  Price 10003: someone wants to buy 15 units
> ```

---

**Lines 12-14: Only process Resin + Configuration**

```python
            if product == "RAINFOREST_RESIN":
                FAIR_VALUE = 10000
                LIMIT = 50
```

- `if product == "RAINFOREST_RESIN":` — only apply this logic to Resin (other products need different strategies).
- `FAIR_VALUE = 10000` — the true value of Resin, ALWAYS 10,000.
- `LIMIT = 50` — maximum position limit.

> **Why use CONSTANTS instead of raw numbers?**
> Instead of writing `10000` everywhere in the code, using `FAIR_VALUE` makes:
> 1. Code easier to read
> 2. Changes only need to happen in one place (e.g., for a different product)
> 3. Avoids typos (9000 instead of 10000)

---

**Lines 16-18: Read current position and calculate limits**

```python
                current_pos = state.position.get(product, 0)
                max_buy = LIMIT - current_pos
                max_sell = LIMIT + current_pos
```

This is **CRITICALLY IMPORTANT** — calculating how much you can still buy/sell.

**`current_pos = state.position.get(product, 0)`**

- `state.position` is a dictionary holding how many units you hold for each product.
- `.get(product, 0)` means: "Get the position for this product. If it doesn't exist (never traded), return 0."

**`max_buy = LIMIT - current_pos`**

How many more can you buy? = Limit - Current position.

| current_pos | max_buy = 50 - pos | Explanation |
|-------------|---------------------|-------------|
| 0 | 50 | Holding nothing → can buy up to 50 |
| 10 | 40 | Holding 10 → can only buy 40 more |
| 50 | 0 | Full! Can't buy any more |
| -20 | 70 | Short 20 → can buy 70 (from -20 to +50) |
| -50 | 100 | Maximum short → can buy 100 (from -50 to +50) |

**`max_sell = LIMIT + current_pos`**

How many more can you sell? = Limit + Current position.

| current_pos | max_sell = 50 + pos | Explanation |
|-------------|----------------------|-------------|
| 0 | 50 | Holding nothing → can sell up to 50 |
| 10 | 60 | Holding 10 → can sell 60 (from +10 to -50) |
| 50 | 100 | Maximum long → can sell 100 (from +50 to -50) |
| -20 | 30 | Short 20 → can only sell 30 more |
| -50 | 0 | Full! Can't sell any more |

> **Why must you calculate max_buy and max_sell?**
>
> If you don't calculate and try to buy too much, the system will **AUTOMATICALLY REJECT** orders that exceed the limit.
> Worse, rejected orders give no clear notification — you miss opportunities without knowing why.
>
> **Think of it like this:** You have a bag that can only carry 50 oranges. You're currently carrying 30.
> If you try to buy 30 more (total 60), the seller will say "Your bag isn't big enough" and refuse the sale.

---

**Lines 20-27: Step 2 — Check sell side (find BUY opportunities)**

```python
                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    if best_ask < FAIR_VALUE:
                        volume = abs(order_depth.sell_orders[best_ask])
                        buy_amount = min(max_buy, volume)
                        if buy_amount > 0:
                            orders.append(Order(product, best_ask, buy_amount))
                            max_buy -= buy_amount
```

This is where you **LOOK FOR CHEAP BUYS**.

**`if order_depth.sell_orders:`** — Check if anyone is selling Resin. If the order book is empty (nobody selling), skip.

**`best_ask = min(order_depth.sell_orders.keys())`** — Find the LOWEST sell price. This is the best price you can buy at.

> **Example:** `sell_orders = {9997: -30, 10001: -20, 10002: -50}`
> `min(9997, 10001, 10002) = 9997` ← Lowest sell price is 9,997

**`if best_ask < FAIR_VALUE:`** — Is the lowest sell price below 10,000?
- 9,997 < 10,000? **YES!** → Buying opportunity!
- If best_ask were 10,001 → 10,001 < 10,000? **NO** → Skip (buying would be a loss).

**`volume = abs(order_depth.sell_orders[best_ask])`** — Get the quantity being sold at that price.

> **Why `abs()`?** Because `sell_orders` stores quantities as **NEGATIVE numbers** (Prosperity convention).
> Example: `sell_orders[9997] = -30` means 30 units are for sale. `abs(-30) = 30`.

**`buy_amount = min(max_buy, volume)`** — How much to buy? Take the SMALLER of:
- How much you CAN still buy (`max_buy`)
- How much is being sold (`volume`)

> **Example 1:** `max_buy = 40`, `volume = 30` → `min(40, 30) = 30` → Buy all 30 (seller runs out)
>
> **Example 2:** `max_buy = 10`, `volume = 30` → `min(10, 30) = 10` → Only buy 10 (your capacity runs out)

**`if buy_amount > 0:`** — Only place an order if you're actually buying something.

**`orders.append(Order(product, best_ask, buy_amount))`** — Create a BUY order:
- `product`: "RAINFOREST_RESIN"
- `best_ask`: Buy price (9,997)
- `buy_amount`: Quantity to buy (30) — **POSITIVE = BUY**

**`max_buy -= buy_amount`** — Update remaining buying capacity.

> **Concrete example:**
> `max_buy = 40`, bought 30 → `max_buy = 40 - 30 = 10` (can still buy 10 more)

---

**Lines 29-36: Step 3 — Check buy side (find SELL opportunities)**

```python
                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    if best_bid > FAIR_VALUE:
                        volume = order_depth.buy_orders[best_bid]
                        sell_amount = min(max_sell, volume)
                        if sell_amount > 0:
                            orders.append(Order(product, best_bid, -sell_amount))
                            max_sell -= sell_amount
```

Same as Step 2 but **reversed** — looking for **EXPENSIVE BUYERS** to sell to.

**`best_bid = max(order_depth.buy_orders.keys())`** — Find the HIGHEST buy price. This is the best price you can sell at.

> **Example:** `buy_orders = {9998: 50, 9999: 5, 10003: 15}`
> `max(9998, 9999, 10003) = 10003` ← Highest buy price is 10,003

**`if best_bid > FAIR_VALUE:`** — Is the highest buy price above 10,000?
- 10,003 > 10,000? **YES!** → Selling opportunity!

**`volume = order_depth.buy_orders[best_bid]`** — Get the buy quantity.

> **Note:** No `abs()` needed because `buy_orders` already stores **POSITIVE numbers**.

**`sell_amount = min(max_sell, volume)`** — How much to sell?

**`Order(product, best_bid, -sell_amount)`** — Create a SELL order:
- `-sell_amount`: **NEGATIVE = SELL**. If `sell_amount = 15`, the order is `Order("RAINFOREST_RESIN", 10003, -15)`.

---

**Line 38: Save orders to result**

```python
            result[product] = orders
```

Save the order list for this product into `result`.

---

**Line 40: Return the result**

```python
        return result, 1, ""
```

Returns 3 values:
1. `result`: Dictionary containing all your orders
2. `1`: Trader data — data you want to save between ticks (1 = nothing special)
3. `""`: Empty string — no log output

> **Note:** In Prosperity 4, the second value is called "traderData" (int or string). Either `1` or `""` works. Later, when you need to save state between ticks, you'll use this field.

---

## 5. Walking Through a Complete Tick — Step by Step

Let's "run" the bot in our heads with a concrete scenario. This is the best way to understand the code.

### The Scenario:

```
Tick t=500 (5th second):

Current position: position = +10 (holding 10 units of Resin)

Order Book:
  sell_orders = {9997: -30, 10001: -20}
  buy_orders  = {10003: 15, 9999: 40}
```

### Running Through Each Step:

**Step 0: Setup**

```
product = "RAINFOREST_RESIN"   ← matches, enter the if block
FAIR_VALUE = 10000
LIMIT = 50
```

**Step 1: Calculate limits**

```
current_pos = state.position.get("RAINFOREST_RESIN", 0) = 10

max_buy  = LIMIT - current_pos = 50 - 10 = 40   ← can buy 40 more
max_sell = LIMIT + current_pos = 50 + 10 = 60   ← can sell 60 more
```

> **Explanation:** You're holding +10. From +10 to +50 is 40 units (buying room). From +10 to -50 is 60 units (selling room).

**Step 2: Check sell side**

```
sell_orders = {9997: -30, 10001: -20}

best_ask = min(9997, 10001) = 9997

9997 < 10000? YES! → BUY opportunity!

volume = abs(sell_orders[9997]) = abs(-30) = 30

buy_amount = min(max_buy, volume) = min(40, 30) = 30
  (30 units for sale, you buy all 30; you have room for 40, so OK)

buy_amount > 0? YES!

→ Create order: Order("RAINFOREST_RESIN", 9997, +30)   ← BUY 30 units at 9997

max_buy = 40 - 30 = 10   ← can still buy 10 more
```

> **In plain English:** 30 units of Resin are being sold at 9,997 (3 below fair value per unit). You buy all 30 units. Potential profit: 30 x 3 = 90 XIRECs.

**Step 3: Check buy side**

```
buy_orders = {10003: 15, 9999: 40}

best_bid = max(10003, 9999) = 10003

10003 > 10000? YES! → SELL opportunity!

volume = buy_orders[10003] = 15

sell_amount = min(max_sell, volume) = min(60, 15) = 15
  (someone wants to buy 15 units, sell all of them)

sell_amount > 0? YES!

→ Create order: Order("RAINFOREST_RESIN", 10003, -15)   ← SELL 15 units at 10003

max_sell = 60 - 15 = 45   ← can still sell 45 more
```

> **In plain English:** Someone wants to buy 15 units of Resin at 10,003 (3 above fair value per unit). You sell them 15 units. Potential profit: 15 x 3 = 45 XIRECs.

**Result of this tick:**

```
Order 1: BUY  30 units @ 9997   (cost: 30 x 9997 = 299,910)
Order 2: SELL 15 units @ 10003  (revenue: 15 x 10003 = 150,045)

Profit from the matched pair:
  15 units x (10003 - 9997) = 15 x 6 = 90 XIRECs

  (The remaining 15 units from the buy don't have a matching sell yet,
   but they still have potential profit since bought below fair value)

New position: 10 + 30 - 15 = +25 (now holding 25 units of Resin)
```

> **What just happened?**
>
> In just 1 tick (0.01 seconds), your bot:
> 1. Bought 30 Resin cheap (price 9,997, value 10,000 → profit 3/unit)
> 2. Sold 15 Resin expensive (price 10,003, value 10,000 → profit 3/unit)
> 3. Earned at least 90 XIRECs in "guaranteed" profit
>
> Multiply by thousands of ticks per round → accumulates to tens of thousands of XIRECs!

---

## 6. Limitations of the Basic Strategy

The bot above works well, but has several weaknesses:

### 6.1. Only "takes" existing orders — doesn't "make" new ones

The bot only finds existing orders in the Order Book and "eats" them. It never **places passive orders** for others to eat.

```
Basic bot:
  → Sees sell order at 9997 → BUY (takes the sell)
  → Sees buy order at 10003 → SELL (takes the buy)
  → No good opportunity? → DOES NOTHING → wastes the tick!

Advanced bot (Frankfurt):
  → Sees sell order at 9997 → BUY (takes the sell)
  → Sees buy order at 10003 → SELL (takes the buy)
  → No good opportunity? → PLACES PASSIVE ORDERS at 9998/10002 → WAITS for others
```

### 6.2. Only looks at best price — ignores deeper levels

```
sell_orders = {9995: -10, 9997: -30, 10001: -20}

Basic bot:
  best_ask = 9997 → BUY 30 units
  → IGNORES 9995! (also cheap but not checked)

Advanced bot:
  9995 < 10000 → BUY 10 units
  9997 < 10000 → BUY 30 units
  → BUYS ALL orders below 10000!
```

### 6.3. No inventory management

If the bot buys continuously and hits +50, it gets "stuck" — can't buy anymore even if there's a great opportunity.

### 6.4. Actual Results

| Strategy | Profit/round | Notes |
|----------|-------------|-------|
| Basic bot (Lesson 1) | ~15,000-20,000 XIRECs | Only taking, only best price |
| Frankfurt bot | ~39,000 XIRECs | Taking + Making + Inventory management |

→ Frankfurt bot earns roughly **2x more** on the same product!

---

# PART 3: LEVELING UP — LEARNING FROM FRANKFURT HEDGEHOGS

> **Frankfurt Hedgehogs** ranked **#2 globally** in Prosperity 3.
> They earned ~39,000 SeaShells/round from Resin alone.
> They publicly shared their strategy — and we'll learn from them.

---

## 7. Wall Mid — A More Accurate Fair Value Estimate

### The Problem with Regular mid_price

In an Order Book, `mid_price` is calculated as (best buy price + best sell price) / 2.

But there's a problem: **taker bots skew the mid_price**.

Let's look at an example:

```
NORMAL situation:
══════════════════════════════════════════════
  Sell: 10002(-50)  10001(-5)
  ─────────────── Mid price ─────────────────
  Buy:   9999(5)    9998(50)
══════════════════════════════════════════════

  best_ask = 10001       best_bid = 9999
  mid_price = (10001 + 9999) / 2 = 10000.0    ← CORRECT!
```

But when a taker bot places a buy order at 10,000:

```
WITH TAKER BOT:
══════════════════════════════════════════════
  Sell: 10002(-50)  10001(-5)
  ─────────────── Mid price ─────────────────
  Buy:  10000(3)    9998(50)       ← taker bot buys 3 units @ 10000
══════════════════════════════════════════════

  best_ask = 10001       best_bid = 10000
  mid_price = (10001 + 10000) / 2 = 10000.5    ← WRONG! Price got pulled up!
```

The true value is still 10,000, but `mid_price` says 10,000.5 because the taker bot pulled `best_bid` up.

### The Solution: Wall Mid

**The idea:** Instead of looking at the best prices (easily skewed), look at the **OUTERMOST** prices — these are usually from market maker bots (large, stable).

```
   Sell: 10002(-50)  10001(-5)
                         ↑ best_ask (easily skewed by takers)
         ↑ ask_wall = MAX sell price (stable, from market maker)

   Buy:  10000(3)    9998(50)
         ↑ best_bid (easily skewed by takers)
                        ↑ bid_wall = MIN buy price (stable, from market maker)
```

**The Formula:**

```
bid_wall = min(buy_orders.keys())      ← OUTERMOST buy price (lowest)
ask_wall = max(sell_orders.keys())     ← OUTERMOST sell price (highest)
wall_mid = (bid_wall + ask_wall) / 2   ← midpoint of the two "walls"
```

**Calculation example:**

```
sell_orders = {10001: -5, 10002: -50}
buy_orders  = {10000: 3,  9998: 50}

bid_wall = min(10000, 9998) = 9998
ask_wall = max(10001, 10002) = 10002

wall_mid = (9998 + 10002) / 2 = 10000.0    ← ACCURATE!
```

Compare with `mid_price`:
```
mid_price = (10001 + 10000) / 2 = 10000.5    ← Skewed by 0.5
wall_mid  = (9998 + 10002) / 2  = 10000.0    ← Accurate!
```

> **Think of it like this:**
>
> In a room, there are many people standing (the orders).
> The people standing against the walls are **STABLE** — they always stand there (market maker).
> The people walking around in the middle move constantly (taker bots).
>
> If you want to find the **center of the room**, measure the distance between the two walls — not between two people walking around!

**Code:**

```python
def get_walls(self, order_depth):
    """Calculate wall_mid — the stable center value"""
    # bid_wall: outermost buy (lowest) — usually from market maker
    bid_wall = min(order_depth.buy_orders.keys())

    # ask_wall: outermost sell (highest) — usually from market maker
    ask_wall = max(order_depth.sell_orders.keys())

    # wall_mid: average of the two walls — best estimate of true value
    wall_mid = (bid_wall + ask_wall) / 2

    return bid_wall, wall_mid, ask_wall
```

### Why Does Wall Mid Matter?

| Situation | mid_price | wall_mid | Correct? |
|-----------|-----------|----------|----------|
| Normal | 10000.0 | 10000.0 | Both correct |
| Taker pulls bid up | 10000.5 | 10000.0 | Only wall_mid correct |
| Taker pushes ask down | 9999.5 | 10000.0 | Only wall_mid correct |

For Resin, wall_mid **almost always** returns 10,000. But when you move to KELP (changing price), wall_mid becomes the **ONLY TOOL** to know the current fair value.

> **Summary:**
>
> `wall_mid` = look at the two walls (large market maker orders) to find the center.
> Not affected by small taker bots in the middle.
> For Resin: wall_mid ≈ 10,000 (always).
> For KELP: wall_mid = the only way to know fair value.

---

## 8. Taking + Making — The Two-Phase Strategy

This is the **biggest difference** between the basic bot and the Frankfurt bot.

### Phase 1: TAKING (eat existing orders)

Same as the basic bot, but **better**:
- Scans **ALL** price levels (not just best_ask/best_bid)
- Uses `wall_mid` instead of hardcoded 10,000
- Adds inventory flattening logic

### Phase 2: MAKING (place passive orders)

AFTER eating all good orders, place passive orders at good positions and **WAIT** for others to eat them.

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   PHASE 1: TAKING (eat profitable orders immediately)          ║
║   ──────────────────────────────────────────                   ║
║   Scan sell_orders: price < wall_mid - 1 → BUY now             ║
║   Scan buy_orders:  price > wall_mid + 1 → SELL now            ║
║                                                                ║
║   PHASE 2: MAKING (place passive orders to earn more)          ║
║   ──────────────────────────────────────────                   ║
║   Place BUY at bid_wall + 1 (overbid — jump ahead)            ║
║   Place SELL at ask_wall - 1 (undercut — jump ahead)           ║
║   → Wait for taker bots to fill your orders                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

> **Think of it like being at a market:**
>
> **Phase 1 (Taking):** You walk around the market, buying cheap fruit when you see it, selling expensive fruit when someone offers.
>
> **Phase 2 (Making):** After walking the whole market, you set up a small stall with signs:
> "BUYING oranges at $4.90" (higher than other buyers at $4.80 → you get priority)
> "SELLING oranges at $5.10" (cheaper than other sellers at $5.20 → you get priority)
> Then you SIT AND WAIT. When someone urgently needs to buy/sell, they come to YOUR stall FIRST.

### Simplified Frankfurt Code:

```python
class Trader:
    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            if product == "RAINFOREST_RESIN":
                LIMIT = 50

                # Read position
                position = state.position.get(product, 0)
                max_buy = LIMIT - position
                max_sell = LIMIT + position

                buy_orders = order_depth.buy_orders    # {price: positive_qty}
                sell_orders = order_depth.sell_orders   # {price: negative_qty}

                # --- Calculate wall_mid ---
                bid_wall = min(buy_orders.keys())
                ask_wall = max(sell_orders.keys())
                wall_mid = (bid_wall + ask_wall) / 2

                # ============================================
                # PHASE 1: TAKING — Eat all profitable orders
                # ============================================

                # 1a. Scan ALL sell orders (find BUY opportunities)
                for price in sorted(sell_orders.keys()):
                    # sell_orders[price] is negative, abs() to get quantity
                    volume = abs(sell_orders[price])

                    if price <= wall_mid - 1:
                        # Price is at least 1 below fair value → BUY!
                        buy_qty = min(max_buy, volume)
                        if buy_qty > 0:
                            orders.append(Order(product, price, buy_qty))
                            max_buy -= buy_qty

                    elif price <= wall_mid and position < 0:
                        # Price at fair value + currently short → buy to flatten
                        buy_qty = min(max_buy, volume, abs(position))
                        if buy_qty > 0:
                            orders.append(Order(product, price, buy_qty))
                            max_buy -= buy_qty
                            position += buy_qty

                # 1b. Scan ALL buy orders (find SELL opportunities)
                for price in sorted(buy_orders.keys(), reverse=True):
                    volume = buy_orders[price]

                    if price >= wall_mid + 1:
                        # Price is at least 1 above fair value → SELL!
                        sell_qty = min(max_sell, volume)
                        if sell_qty > 0:
                            orders.append(Order(product, price, -sell_qty))
                            max_sell -= sell_qty

                    elif price >= wall_mid and position > 0:
                        # Price at fair value + currently long → sell to flatten
                        sell_qty = min(max_sell, volume, position)
                        if sell_qty > 0:
                            orders.append(Order(product, price, -sell_qty))
                            max_sell -= sell_qty
                            position -= sell_qty

                # ============================================
                # PHASE 2: MAKING — Place passive orders
                # ============================================

                # Overbid: place BUY 1 tick above bid_wall
                bid_price = bid_wall + 1
                # Undercut: place SELL 1 tick below ask_wall
                ask_price = ask_wall - 1

                # Safety: only place if still profitable
                if bid_price < wall_mid and max_buy > 0:
                    orders.append(Order(product, bid_price, max_buy))

                if ask_price > wall_mid and max_sell > 0:
                    orders.append(Order(product, ask_price, -max_sell))

            result[product] = orders

        return result, 1, ""
```

### Detailed Explanation of Each Part:

**Phase 1a: Scan ALL sell orders**

```python
for price in sorted(sell_orders.keys()):
```

Instead of only looking at `best_ask` (lowest sell price), the bot scans **ALL** sell price levels, from lowest to highest.

> **Example:**
> ```
> sell_orders = {9995: -10, 9997: -30, 10001: -20}
> sorted keys = [9995, 9997, 10001]
>
> Price 9995: 9995 <= 10000 - 1 = 9999? YES → BUY 10 units
> Price 9997: 9997 <= 9999? YES → BUY 30 units
> Price 10001: 10001 <= 9999? NO → Stop scanning
>
> Total: BUY 40 units (vs only 30 if only looking at best_ask=9997)
> ```

**Flatten logic (inventory flattening):**

```python
elif price <= wall_mid and position < 0:
    buy_qty = min(max_buy, volume, abs(position))
```

If you're currently **short** (position < 0) and there are sell orders at wall_mid → buy to get back to 0.

> **Example:** Position = -20, sell order at price 10000 (= wall_mid).
> → Buy 20 units at 10000 to "unwind" the short position.
> → No profit, no loss, but **frees up capacity** for the next profitable trade.

**Phase 2: Place passive orders**

```python
bid_price = bid_wall + 1    # Overbid
ask_price = ask_wall - 1    # Undercut
```

Place a BUY at `bid_wall + 1` and a SELL at `ask_wall - 1`. These prices "jump ahead" of the market maker.

> **Example:**
> ```
> bid_wall = 9997, ask_wall = 10003
>
> bid_price = 9997 + 1 = 9998   ← Place BUY at 9998
> ask_price = 10003 - 1 = 10002  ← Place SELL at 10002
>
> wall_mid = (9997 + 10003) / 2 = 10000
>
> 9998 < 10000? YES → safe to place buy order
> 10002 > 10000? YES → safe to place sell order
> ```

### Comparison Table:

| Feature | Basic Bot (Lesson 1) | Frankfurt Bot |
|---------|---------------------|---------------|
| Taking | Only best_ask / best_bid | Scans ALL profitable price levels |
| Making | None | Places passive orders at bid_wall+1 / ask_wall-1 |
| Fair value | Hardcoded 10,000 | wall_mid (flexible) |
| Inventory handling | None | Flattens at wall_mid |
| Result | ~15,000-20,000/round | ~39,000/round |

---

## 9. Overbidding & Undercutting — Winning Priority for Passive Orders

When placing passive orders (making), you want YOUR order to be **FILLED FIRST** over others. How?

### Order Priority Rules

In Prosperity, when there are multiple buy orders at different prices, the one with the **HIGHEST PRICE** gets filled first. Similarly, sell orders with the **LOWEST PRICE** get filled first.

```
Current Order Book:
  Sell: 10003(-50), 10002(-5)     ← ask_wall = 10003
  Buy:  9997(50),   9998(5)       ← bid_wall = 9997

Market maker orders:
  Buy @ 9997 (50 units)    ← the buy "wall"
  Sell @ 10003 (50 units)  ← the sell "wall"

Frankfurt bot places "jump ahead" orders:
  Buy @ 9998 (overbid: +1 above bid_wall)   ← "jump" in front of the buy wall
  Sell @ 10002 (undercut: -1 below ask_wall) ← "jump" in front of the sell wall
```

When a taker bot arrives:

```
Taker bot wants to SELL Resin:
  → Looks for the highest buy order
  → Finds YOUR buy at 9998 (higher than market maker at 9997)
  → Sells to YOU first! ← You get filled before the market maker!

Taker bot wants to BUY Resin:
  → Looks for the lowest sell order
  → Finds YOUR sell at 10002 (lower than market maker at 10003)
  → Buys from YOU first! ← You get filled before the market maker!
```

> **Think of it like a supermarket:**
>
> There are 2 stalls selling oranges:
> - Stall A sells at $5.20 (market maker)
> - Stall B (yours) sells at $5.10 (undercut)
>
> Customer walks in → sees your stall is cheaper → buys from you first!
>
> Similarly, there are 2 people wanting to buy oranges:
> - Person A offers $4.80 (market maker)
> - You offer $4.90 (overbid)
>
> Orange seller arrives → sees you're offering more → sells to you first!

### Safety Check

**IMPORTANT:** Only overbid/undercut if the resulting price is still PROFITABLE.

```python
# Only overbid if the new buy price is still BELOW wall_mid
overbid_price = bid_wall + 1
if overbid_price < wall_mid:      # Still below fair value → profitable
    bid_price = overbid_price     # Safe to place
else:
    bid_price = bid_wall          # Don't overbid, keep original

# Only undercut if the new sell price is still ABOVE wall_mid
undercut_price = ask_wall - 1
if undercut_price > wall_mid:     # Still above fair value → profitable
    ask_price = undercut_price    # Safe to place
else:
    ask_price = ask_wall          # Don't undercut, keep original
```

> **Safe example:**
> ```
> bid_wall = 9997, ask_wall = 10003, wall_mid = 10000
>
> overbid_price = 9998
> 9998 < 10000? YES → Safe, place buy at 9998  (profit 2/unit)
>
> undercut_price = 10002
> 10002 > 10000? YES → Safe, place sell at 10002 (profit 2/unit)
> ```
>
> **UNSAFE example:**
> ```
> bid_wall = 9999, ask_wall = 10001, wall_mid = 10000
>
> overbid_price = 10000
> 10000 < 10000? NO → Don't overbid! (buying at fair value = no profit)
>
> undercut_price = 10000
> 10000 > 10000? NO → Don't undercut! (selling at fair value = no profit)
> ```

---

## 10. Inventory Flattening — Clearing Excess Inventory

### The Problem: Position "Lock-up"

Imagine your bot keeps buying and hits position +50 (maximum). Now:

```
Position: +50

max_buy  = 50 - 50 = 0    ← CAN'T BUY ANYMORE!
max_sell = 50 + 50 = 100

Amazing opportunity appears: Resin selling at 9990!
→ But max_buy = 0 → can't buy → MISSED!
```

Similarly, if position is -50:

```
Position: -50

max_buy  = 50 + 50 = 100
max_sell = 50 - 50 = 0    ← CAN'T SELL ANYMORE!

Amazing opportunity: Someone buying Resin at 10010!
→ But max_sell = 0 → can't sell → MISSED!
```

### The Solution: Flatten at Fair Value

When position is too skewed, buy/sell at exactly `wall_mid` (fair value) to **free up capacity**.

```python
# Currently long + buyer at wall_mid → SELL to reduce position
if price >= wall_mid and position > 0:
    sell_qty = min(max_sell, volume, position)
    orders.append(Order(product, price, -sell_qty))
    position -= sell_qty

# Currently short + seller at wall_mid → BUY to increase position
if price <= wall_mid and position < 0:
    buy_qty = min(max_buy, volume, abs(position))
    orders.append(Order(product, price, buy_qty))
    position += buy_qty
```

> **Philosophy:** Flatten at fair value → **no profit, no loss** → but **FREES CAPACITY** for the next profitable trade.

### Concrete Example:

```
Current position: +45 (nearly full!)
max_buy = 50 - 45 = 5     ← can only buy 5 more
max_sell = 50 + 45 = 95

Someone is buying at 10000 (= wall_mid) with volume = 20

→ Flatten: SELL 20 units at 10000
  (sell at most = min(95, 20, 45) = 20)

New position: +45 - 20 = +25
max_buy = 50 - 25 = 25    ← now can buy 25!
max_sell = 50 + 25 = 75

→ Capacity went from 5 to 25! Ready for the next opportunity!
```

> **Think of it like this:**
>
> You have a fridge that only holds 50 oranges. Currently storing 45.
> Someone says "I'll buy oranges at $5.00" (the fair price).
> You sell 20 oranges at $5.00 → no profit, no loss.
> But now your fridge has room for 25 oranges → if cheap oranges come tomorrow, you can buy more!

---

## 11. How the System Processes Orders — The Key Secret

Understanding the **ORDER OF PROCESSING** is crucial for understanding why Making (Phase 2) works.

### Processing Order Each Tick:

```
╔══════════════════════════════════════════════════════════════╗
║ Step 1: Clear ALL old orders (orders only live for 1 tick)   ║
║                                                              ║
║ Step 2: Market maker bots place orders → create "walls"      ║
║                                                              ║
║ Step 3: Some taker bots trade                                ║
║                                                              ║
║ Step 4: YOUR BOT places orders (taking + making)             ║
║         → You see the Order Book after step 3                ║
║         → Taking orders execute immediately                  ║
║         → Making orders are placed into the Order Book       ║
║                                                              ║
║ Step 5: MORE taker bots trade                                ║
║         → Can EAT your making orders!                        ║
║                                                              ║
║ Step 6: Tick ends. Back to step 1.                           ║
╚══════════════════════════════════════════════════════════════╝
```

### Why Does This Matter?

**Your making orders are placed at Step 4, and taker bots at Step 5 can EAT them.**

If you don't place making orders (like the basic bot), you MISS all the opportunity from step 5.

> **Example:**
> ```
> Step 2: Market maker places buy @ 9997 (50 units)
> Step 3: (nothing happens)
> Step 4: Your bot:
>   - Taking: buys 30 units @ 9997 (someone was selling cheap)
>   - Making: places buy @ 9998 (overbid market maker)
>            places sell @ 10002 (undercut market maker)
> Step 5: Taker bot wants to sell Resin
>   → Finds your buy @ 9998 (higher than market maker @ 9997)
>   → SELLS TO YOU! ← You earned extra profit!
> ```

### Key Takeaways:

1. **Speed doesn't matter** — You always see the full Order Book snapshot before deciding. It's not "whoever is fastest wins."

2. **Orders only live for 1 tick** — No need to worry about "canceling old orders." Every tick starts fresh.

3. **Making has real opportunity** — Taker bots at step 5 can fill your making orders, creating additional profit.

> **This is WHY Frankfurt ALWAYS places making orders (Phase 2)** — the taker bots at step 5 can fill them, earning extra profit that the basic bot (Phase 1 only) misses entirely.

---

## 12. Why Did Frankfurt Hedgehogs Win?

Frankfurt shared 5 core principles in their writeup:

### Principle 1: Deep Understanding Before Coding

> *"Placed enormous emphasis on deep structural understanding of each product."*
> — Frankfurt Hedgehogs

They didn't jump into coding right away. They spent time **understanding** how the market works:
- How do market maker bots place orders?
- How do taker bots behave?
- What's the order processing sequence?
- How is fair value determined?

**Lesson for you:** Before coding, read and understand thoroughly. Reading this guide is the right first step!

### Principle 2: Simple Strategies, Few Parameters

> *"Focused on simple, robust strategies, minimizing parameters whenever possible."*

Their Resin strategy only has:
- `wall_mid` (automatically calculated from Order Book)
- Overbid/undercut by 1 tick
- Flatten at wall_mid

No Machine Learning. No complex formulas. No 10 parameters to tune.

**Lesson:** Simple and effective beats complex and confusing.

### Principle 3: No Overfitting

> *"If you can't explain why a strategy should work from first principles, any outperformance in historical data is probably noise."*

If you can't explain **WHY** a strategy works, good backtest results are just **luck**. It won't work on new data.

**Example:**
- GOOD: "I buy below 10,000 because Resin is always worth 10,000" → Explainable → Good strategy
- BAD: "I buy when RSI < 30 because backtesting showed profit" → Can't explain why RSI works → Probably luck

### Principle 4: Good Tools = Fast Analysis

Frankfurt built custom dashboards to analyze results. You can use:
- **Jmerle Backtester** (available in the project)
- **Visualizer** (visualizer.py file)
- Log files for debugging

### Principle 5: Learn from the Past

Frankfurt read previous winners' writeups — and now you're reading Frankfurt's writeup. The circle continues!

### Frankfurt PnL Breakdown (Reference):

| Product | PnL/round | Strategy |
|---------|-----------|----------|
| **Resin** | **~39,000** | **Market making (taking + making)** |
| Kelp | ~5,000 | Market making (dynamic wall_mid) |
| Squid Ink | ~8,000 | Following trader Olivia |
| Baskets | ~50,000 | Statistical arbitrage (ETF vs components) |
| Options | ~100,000-150,000 | IV scalping |
| Macarons | ~80,000-100,000 | Locational arbitrage |

> **Note:** Resin is ~39,000/round — not the highest earner, but the **MOST STABLE**. Frankfurt's Resin strategy virtually **never lost money**.

---

# PART 4: NEXT STEPS

---

## 13. Summary of What You've Learned

You've gone from 0 to understanding a high-level Resin trading strategy:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   LEVEL 1: Basic Bot (Lesson 1)                                  ║
║   ─────────────────────────────                                  ║
║   • Buy below 10,000, sell above 10,000                          ║
║   • Only looks at best_ask and best_bid                          ║
║   • No passive order placement (making)                          ║
║   • Result: ~15,000-20,000 XIRECs/round                         ║
║                                                                  ║
║   LEVEL 2: Frankfurt Bot                                         ║
║   ─────────────────────                                          ║
║   • Uses wall_mid instead of hardcoded 10,000                    ║
║   • Scans ALL profitable price levels (not just best price)      ║
║   • Places passive orders (making) with overbid/undercut         ║
║   • Flattens position at wall_mid to free capacity               ║
║   • Result: ~39,000 XIRECs/round                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Concepts Covered:

| # | Concept | Meaning |
|---|---------|---------|
| 1 | Fixed Fair Value | Resin is always = 10,000 XIRECs |
| 2 | Position Limit | Max ±50, must calculate max_buy/max_sell |
| 3 | Aggressive Taking | Eat profitable orders from the Order Book |
| 4 | Wall Mid | Average of outermost prices on both sides = stable fair value |
| 5 | Overbid/Undercut | Jump ahead of market maker by +1/-1 for priority |
| 6 | Making (Passive Orders) | Place waiting orders for taker bots to fill |
| 7 | Inventory Flattening | Unwind position at fair value to free capacity |
| 8 | Order Processing Sequence | Market maker → Taker → You → Taker (fills your making orders) |

---

## 14. Practice Exercises

Try these exercises to solidify your understanding:

### Exercise 1: Run the Basic Bot
1. Open `Lesson1_Resin.py` (or create a new file from the code in Section 4)
2. Run with the backtester: `python backtester.py`
3. Check the PnL result — should be around 15,000-20,000/round

### Exercise 2: Change the Threshold
1. Try changing `FAIR_VALUE = 10000` to `9999` or `10001`
2. Run the backtest again — does PnL increase or decrease?
3. **Think:** Why is 10,000 the best value?

### Exercise 3: Add Making (Phase 2)
1. Take the basic bot from Exercise 1
2. Add passive order placement code after the taking section:
   ```python
   # After taking is done, add:
   bid_price = best_bid_wall + 1  # (you need to calculate bid_wall first)
   ask_price = best_ask_wall - 1
   # Place orders...
   ```
3. Run the backtest and compare PnL with the taking-only bot

### Exercise 4: Implement wall_mid
1. Write the `get_walls()` function as shown in Section 7
2. Print wall_mid every tick (use logger)
3. Verify that wall_mid is almost always = 10,000 for Resin

### Exercise 5: Add Inventory Flattening
1. Add the flatten logic from Section 10
2. Run the backtest — is the position more "stable"?
3. Does PnL increase?

> **Tip:** Do each exercise ONE AT A TIME, check the result, then move to the next. Don't try all 5 at once!

---

## 15. Coming Next: KELP

After mastering Resin, the next product is **KELP**.

### Similarities and Differences:

| | Resin | KELP |
|--|-------|------|
| Fair value | **Fixed** = 10,000 | **Changes** every tick (random walk) |
| wall_mid | Always ≈ 10,000 (optional) | **REQUIRED** to know fair value |
| Strategy | Buy below 10K, sell above 10K | Buy below wall_mid, sell above wall_mid |
| Difficulty | Easy | Medium |

### How is KELP Different?

With Resin, you can "cheat" by hardcoding `FAIR_VALUE = 10000`. With KELP, the price changes continuously — you **MUST calculate wall_mid** every tick.

```
KELP fair value over time:
  t=0:   2050
  t=100: 2055
  t=200: 2048
  t=300: 2060
  t=400: 2045
  ...

Can't hardcode! Must calculate wall_mid every tick!
```

But the good news is: **Frankfurt's KELP strategy is nearly identical to Resin** — just replace `FAIR_VALUE = 10000` with `wall_mid` calculated from the Order Book. All other logic (taking, making, overbid, undercut, flatten) is exactly the same.

> **Next up:** Read the Round1_Kelp guide when available (to be written later).

---

*Based on Lesson 1 + Frankfurt Hedgehogs strategy (Top 2, Prosperity 3). Updated for Prosperity 4.*
