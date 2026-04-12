# General Guide — IMC Prosperity 4 Fundamentals

> **Who is this for?** Anyone who wants to participate in IMC Prosperity 4 — even if you have never coded in Python, never traded, or have no math background. This guide explains EVERYTHING from scratch.

---

## Table of Contents

- [Part 1: Introduction](#part-1-introduction)
  - [1. What is IMC Prosperity?](#1-what-is-imc-prosperity)
  - [2. Prosperity 4 vs Previous Versions](#2-prosperity-4-vs-previous-versions)
- [Part 2: Markets and the Exchange](#part-2-markets-and-the-exchange)
  - [3. What is an Exchange?](#3-what-is-an-exchange)
  - [4. Order Book](#4-order-book)
  - [5. Order Types](#5-order-types)
  - [6. Order Matching — How Orders Get Filled](#6-order-matching--how-orders-get-filled)
- [Part 3: Simulation System](#part-3-simulation-system)
  - [7. Tick — The Unit of Time](#7-tick--the-unit-of-time)
  - [8. TradingState — Your Information Package Each Tick](#8-tradingstate--your-information-package-each-tick)
  - [9. Position Limit](#9-position-limit)
  - [10. The run() Function — Your Bot's Heart](#10-the-run-function--your-bots-heart)
  - [11. traderData — Memory Between Ticks](#11-traderdata--memory-between-ticks)
- [Part 4: Learning Roadmap](#part-4-learning-roadmap)
  - [12. Roadmap from Round 1 to Round 5](#12-roadmap-from-round-1-to-round-5)
- [Part 5: Reference](#part-5-reference)
  - [13. Common Mistakes](#13-common-mistakes)
  - [14. Submission Checklist](#14-submission-checklist)
  - [15. Glossary](#15-glossary)

---

# PART 1: INTRODUCTION

---

## 1. What is IMC Prosperity?

### Think of it like this...

You know coding competitions like HackerRank or LeetCode? IMC Prosperity is also a competition, but instead of solving algorithm puzzles, you **write Python code to control a trading robot**.

Imagine this: you are at a busy farmer's market. There are many people buying and selling fruit. You hire a helper (your robot), and you write a set of instructions on a piece of paper: "If you see mangoes under $2, buy them. If someone offers more than $2.50, sell." Your helper follows these instructions automatically, without you standing there.

IMC Prosperity is similar — but instead of fruit, you buy and sell **virtual financial products** (like stocks or commodities). And instead of writing on paper, you write in **Python**.

### Competition Details

- **5 rounds** over about **15 days**
- Each round adds new products, but old ones remain
- You submit just **1 Python file** per round — this file contains your bot's entire logic
- Your bot trades automatically in a **simulation**:
  - Testing: **1,000 iterations**
  - Final scoring: **10,000 iterations**
- Currency: **XIRECs** (Prosperity 4's currency)
- Goal: **earn as many XIRECs as possible**

### Simple Example

Suppose your bot buys 1 unit of RAINFOREST_RESIN at 9,998 XIRECs, then sells it at 10,002 XIRECs. You just earned:

```
Profit = 10,002 - 9,998 = 4 XIRECs
```

Do that 10,000 times a day, at 4 XIRECs each = 40,000 XIRECs/day. Sounds small, but it adds up enormously!

> **Real-world analogy:** Imagine you sell water bottles in front of a school. You buy each bottle for $0.50 and sell for $1.00. Each bottle gives you $0.50 profit. If you sell 100 bottles a day, that's $50/day. Your bot does the same thing — but much faster and completely automatically!

### Why Participate?

1. **Learn Python** through a real project (not boring exercises)
2. **Learn about finance** and how markets work
3. **Job opportunities** at IMC Trading — one of the world's largest trading firms
4. **Prizes** for top-ranking teams
5. **Fun** — the competition is designed like a game with an engaging storyline

---

## 2. Prosperity 4 vs Previous Versions

Prosperity 4 has some changes compared to previous versions. This matters because many tutorials and code samples online are from Prosperity 3 or earlier.

| | Prosperity 3 (Frankfurt examples) | Prosperity 4 (current) |
|---|---|---|
| **Currency** | SeaShells | **XIRECs** |
| **Round 2+** | Not required | **Need bid() method** |
| **traderData** | No stated limit | **Max 50,000 characters** |
| **Simulation** | — | **1,000 test / 10,000 final** |
| **Position limits** | Fixed | **May vary — check each round** |

> **Important note:** This guide uses code from **Frankfurt Hedgehogs** (team ranked #2, Prosperity 3) as examples. Their code is from Prosperity 3, so when you see `SeaShells`, think `XIRECs`, and you may need to adjust some small details for Prosperity 4.

### Why Use Frankfurt's Code?

Frankfurt Hedgehogs were one of the best teams in Prosperity 3. They shared their code and strategies publicly. Learning from actual top-team code is the fastest way to understand how to do things right.

> **Things to remember:**
> - Replace `SeaShells` with `XIRECs` in your thinking
> - If using Round 2+ in Prosperity 4, you need to write a `bid()` method — details in round-specific guides
> - Always check that `traderData` doesn't exceed 50,000 characters

---

# PART 2: MARKETS AND THE EXCHANGE

---

## 3. What is an Exchange?

### Real-World Example

Imagine you go to a **currency exchange booth at an airport**. You want to exchange USD for another currency. The booth will have:
- **Bid price:** "We buy 1 USD for 0.92 EUR" — this is the price they're willing to pay you
- **Ask price:** "We sell 1 USD for 0.95 EUR" — this is the price you must pay to buy from them

The **difference** between these two prices (0.95 - 0.92 = 0.03 EUR) is how the exchange booth makes money. In English, this gap is called the **spread**.

### The Exchange in Prosperity

In IMC Prosperity, the **Exchange** is a **simulated central marketplace** where:
- Your bot trades alongside **other bots** (created by IMC and other competitors)
- Everything is automated — you **don't click any buttons**
- Your bot sends **buy/sell orders**, and the system automatically matches compatible orders

```
         ┌─────────────────────────────┐
         │       EXCHANGE              │
         │                             │
   You → │  Your bot  ↔  IMC bot #1   │
         │            ↔  IMC bot #2   │
         │            ↔  IMC bot #3   │
         │            ↔  Rival bots   │
         └─────────────────────────────┘
```

### Everything Happens Automatically

This is the most important thing to understand: once the competition is running, you **cannot intervene**. Your bot runs on the code you wrote. It's like teaching a robot how to work, then watching it do the job — you can't jump in and grab the controls mid-way.

> **Analogy:** Think of it like programming a washing machine. You set: wash 30 minutes, rinse twice, spin dry. The machine does exactly that — you can't stop it mid-cycle to change settings. Your trading bot works the same way!

---

## 4. Order Book

### Imagine a Whiteboard

Think of the Order Book as a **big whiteboard** placed at the center of a market. On one side are people who want to **buy**, on the other side are people who want to **sell**. Everyone writes on the board: "I want to buy/sell X units at price Y."

When a buyer and seller agree on a price, they trade and erase their names from the board. People who haven't matched yet stay on the board, waiting.

### Visualization for RAINFOREST_RESIN

Suppose RAINFOREST_RESIN has a fair value of about 10,000 XIRECs. Here's what the Order Book might look like:

```
============================================================
               ORDER BOOK: RAINFOREST_RESIN
============================================================

  SELL SIDE (sell_orders):         ← People wanting to SELL
  ┌─────────────────────────────────────────────────┐
  │  Price 10,002  →  25 units     ← ask_wall       │
  │  Price 10,001  →  10 units     ← best_ask       │
  └─────────────────────────────────────────────────┘

  ──────── FAIR VALUE ≈ 10,000 ────────

  BUY SIDE (buy_orders):          ← People wanting to BUY
  ┌─────────────────────────────────────────────────┐
  │  Price  9,999  →  10 units     ← best_bid       │
  │  Price  9,998  →  20 units     ← bid_wall       │
  └─────────────────────────────────────────────────┘

============================================================
```

**How to read this:**

- **Sell side (sell_orders):** Someone is willing to sell 10 units at 10,001, and 25 units at 10,002
- **Buy side (buy_orders):** Someone is willing to buy 10 units at 9,999, and 20 units at 9,998
- **No one has traded yet** because the highest buyer (9,999) is still below the cheapest seller (10,001)

### In Python Code

In Prosperity, the Order Book is represented as 2 dictionaries:

```python
# Get the order book for RAINFOREST_RESIN
order_depth = state.order_depths["RAINFOREST_RESIN"]

# =====================================================
# SELL SIDE (sell_orders)
# CRITICAL NOTE: Volumes are NEGATIVE!!!
# IMC convention: sell_orders have negative volumes
# =====================================================
order_depth.sell_orders = {
    10001: -10,    # 10 units for sale at 10,001
                   # Volume is -10 (negative!) because it's a sell order
    10002: -25,    # 25 units for sale at 10,002
                   # This is the "ask_wall" = furthest sell price
}

# =====================================================
# BUY SIDE (buy_orders)
# Volumes are POSITIVE (normal)
# =====================================================
order_depth.buy_orders = {
    9999: 10,      # 10 units wanted at 9,999
                   # This is the "best_bid" = highest buy price
    9998: 20,      # 20 units wanted at 9,998
                   # This is the "bid_wall" = furthest buy price
}
```

> **WARNING:** This is the **#1 most common mistake** for beginners! `sell_orders` have **NEGATIVE** volumes. When you want to know how many units are for sale, you must use `abs()`:
> ```python
> # WRONG — gives you a negative number!
> quantity = order_depth.sell_orders[10001]   # → -10
>
> # CORRECT — use abs() to get the positive number
> quantity = abs(order_depth.sell_orders[10001])   # → 10
> ```

### Order Book Terminology Table

| Term | Meaning | Code |
|------|---------|------|
| **best_ask** | Cheapest seller (best price for a buyer) | `min(sell_orders.keys())` |
| **best_bid** | Highest buyer (best price for a seller) | `max(buy_orders.keys())` |
| **spread** | Gap between best_ask and best_bid | `best_ask - best_bid` |
| **mid_price** | Middle price | `(best_ask + best_bid) / 2` |
| **bid_wall** | Furthest buy price (usually large volume) | `min(buy_orders.keys())` |
| **ask_wall** | Furthest sell price (usually large volume) | `max(sell_orders.keys())` |
| **wall_mid** | Average of the two walls | `(bid_wall + ask_wall) / 2` |

### Computing These Values in Code

```python
order_depth = state.order_depths["RAINFOREST_RESIN"]

# Best ask = cheapest sell price
best_ask = min(order_depth.sell_orders.keys())  # → 10,001

# Best bid = highest buy price
best_bid = max(order_depth.buy_orders.keys())   # → 9,999

# Spread = gap between them
spread = best_ask - best_bid                     # → 2

# Mid price = halfway point
mid_price = (best_ask + best_bid) / 2            # → 10,000.0

# Volume at best_ask (remember to use abs()!)
ask_volume = abs(order_depth.sell_orders[best_ask])  # → 10

# Volume at best_bid
bid_volume = order_depth.buy_orders[best_bid]        # → 10
```

### "Crossed" vs "Uncrossed" Book

Normally, `best_bid < best_ask` — no one agrees on a price yet. This is called an **uncrossed book** (normal state).

```
Uncrossed (normal):
  Cheapest seller: 10,001
  Highest buyer:    9,999
  → No trade because 9,999 < 10,001
```

Sometimes, someone sends a buy order priced higher than the lowest seller (or vice versa). When `best_bid >= best_ask`, this is called a **crossed book** — and trading happens immediately!

```
Crossed (trade happens immediately):
  Cheapest seller: 10,000
  Highest buyer:   10,001
  → Matches immediately because 10,001 >= 10,000!
```

> **Real-world analogy:** You're at a market, and you see mangoes priced at $2.00. You shout "I'll pay $2.50!" — obviously the seller agrees immediately because you're offering more than they asked. That's a crossed book — the trade happens instantly.

> **What just happened?** The Order Book is like a bulletin board at a market. One side posts buy prices, the other posts sell prices. When buy price >= sell price, a trade happens. Your bot reads this board every tick to decide whether to buy or sell.

---

## 5. Order Types

### In the Real World, There Are 3 Order Types

Before talking about Prosperity, let's understand the 3 basic order types in real trading:

**1. Market Order:**
- "Buy immediately, at whatever the current price is!"
- Like walking into a store and saying: "Give me 1 kg of mangoes, I don't care about the price"
- Advantage: you get the item right away
- Disadvantage: you might pay a high price

**2. Limit Order:**
- "Buy, but only at price X or lower"
- Like saying: "I'll only buy mangoes if they're $2.00 or less"
- Advantage: you control the price
- Disadvantage: you might not get any if no one sells at that price

**3. Stop Order:**
- "When the price hits X, automatically place an order"
- Like telling someone: "If mangoes go above $3.00, sell all my mangoes"
- Used for cutting losses or locking in profits

### Prosperity ONLY Uses Limit Orders!

In Prosperity, you can **only place Limit Orders**. This is actually simpler — you always specify a price:

```python
# How to create an order in Prosperity
Order(product, price, quantity)

# Example: Buy 5 RAINFOREST_RESIN at price 9,998
Order("RAINFOREST_RESIN", 9998, 5)      # POSITIVE quantity = BUY

# Example: Sell 3 RAINFOREST_RESIN at price 10,002
Order("RAINFOREST_RESIN", 10002, -3)    # NEGATIVE quantity = SELL
```

> **Important note:**
> - `quantity > 0` means **BUY**
> - `quantity < 0` means **SELL**
> - Forgetting the negative sign when selling is a very common mistake!

### 2 Behaviors of a Limit Order

Even though there's only 1 order type, it behaves in 2 different ways depending on the price you set:

| Type | English Name | Meaning | When it happens | Example |
|------|-------------|---------|-----------------|---------|
| **Aggressive** | Taking | "Eat" existing orders from the book | BUY price >= best_ask, or SELL price <= best_bid | Buy at 10,001 when best_ask = 10,001 → fills immediately! |
| **Passive** | Making | Post an order and wait | BUY price < best_ask, or SELL price > best_bid | Buy at 9,999 when best_ask = 10,001 → waits for someone to sell at 9,999 |

#### Illustrated Examples:

```
Current Order Book:
  best_ask = 10,001 (10 units for sale)
  best_bid = 9,999  (10 units wanted)
```

**Case 1 — Aggressive (Taking):**
```python
# You want to buy IMMEDIATELY
# Set BUY price = 10,001 (matching best_ask)
Order("RAINFOREST_RESIN", 10001, 5)
# → Fills immediately: 5 units from the seller at 10,001
# → You pay 5 x 10,001 = 50,005 XIRECs
```

**Case 2 — Passive (Making):**
```python
# You want to buy at a CHEAPER price
# Set BUY price = 9,999 (matching best_bid)
Order("RAINFOREST_RESIN", 9999, 5)
# → Does NOT fill — your order sits on the order book
# → Waits until someone sells at 9,999 or lower
# → But remember: the order expires at the end of the tick!
```

> **Real-world analogy:**
> - **Aggressive** is like going to the market and saying: "I'll take it at your price." You get the goods right away but might pay more.
> - **Passive** is like writing your price on a board: "I want to buy at this price." Then you sit and wait. You might get a better deal, but someone might never sell to you.

> **What just happened?** In Prosperity, you only use Limit Orders. If you set a "good" price (buy high, sell low), it fills immediately (aggressive). If you set a "waiting" price (buy low, sell high), it sits on the book (passive). Every order only lives for 1 tick.

---

## 6. Order Matching — How Orders Get Filled

### Priority Rule: Price First, Then Time

When there are multiple orders on the book, which ones get matched first? IMC uses **Price-Time Priority**:

**Step 1 — Best price first:**
- If you send a SELL order, the system finds the BUY order with the HIGHEST price first
- If you send a BUY order, the system finds the SELL order with the LOWEST price first
- Reason: you always get the best possible price!

**Step 2 — Same price, earliest order first (FIFO):**
- If 2 orders have the same price, the one that arrived first gets matched first
- Like standing in line at a movie theater — first come, first served

### Concrete Example

Suppose the order book has these BUY orders:
```
Order A: BUY 10 units at 9,999 (arrived first)
Order B: BUY  5 units at 10,000
Order C: BUY  8 units at 9,999 (arrived after Order A)
```

Now you send a SELL order for 20 units at 9,998. What happens?

```
Step 1: Match with Order B (price 10,000 — highest, best for seller)
        → You sell 5 units at 10,000
        → Remaining: 20 - 5 = 15 units to sell

Step 2: Match with Order A (price 9,999, arrived before Order C)
        → You sell 10 units at 9,999
        → Remaining: 15 - 10 = 5 units to sell

Step 3: Match with Order C (price 9,999, arrived after Order A)
        → You sell 5 units at 9,999
        → Remaining: 0 — fully filled!

Result: Order C has 3 units left unfilled (8 - 5 = 3)
```

> **Note:** You placed a sell at 9,998 but got matched at 10,000 and 9,999 — **better prices** than you asked! In Prosperity, you always get the **best available price**.

### Partial Fills

If your order is larger than the available volume, only part of it gets filled. The remainder **is not carried over** — it disappears at the end of the tick.

```python
# You send a buy order for 20 units at 10,001
# But only 10 units are for sale at 10,001
# → Only 10 units get filled
# → The remaining 10 units DISAPPEAR (not carried to next tick)
```

### In Prosperity

- All your bot's orders within 1 tick are processed together
- Orders **do not carry over** to the next tick — every tick starts fresh
- If an order doesn't fully fill this tick, the unfilled part is canceled

> **Real-world analogy:** Think of an auction. The highest bidder wins. If two people bid the same amount, whoever raised their hand first wins. And if you want to buy 10 items but only 5 are available, you only get 5 — there's no "hold the other 5 for next time."

> **What just happened?** The matching system uses this rule: best price first, same price means earliest order first. Orders can partially fill. In Prosperity, every order only lives for 1 tick — unfilled portions disappear.

---

# PART 3: SIMULATION SYSTEM

---

## 7. Tick — The Unit of Time

### Prosperity Does NOT Run in Real-Time

In real trading, everything happens continuously — prices change every second, every millisecond. But in Prosperity, time is divided into discrete **steps** called **ticks**.

Think of it like this: watching a movie is continuous time. But a **flipbook** (those books where you flip pages to see animation) is frame-by-frame — each page is one step. Prosperity is like a flipbook — each "page" is one tick.

### How Ticks Work

```
Tick 100  →  Tick 200  →  Tick 300  →  ...  →  Tick 999,900  →  Tick 1,000,000
   │            │            │
   │            │            └── System calls run() for the 3rd time
   │            └── System calls run() for the 2nd time
   └── System calls run() for the 1st time
```

- **Timestamp increases by 100 each tick:** 100, 200, 300, 400...
- Each tick, the system calls your `run()` function once
- You receive market information **at that moment** and return orders
- About **10,000 ticks** per trading day in the final simulation

### Every Tick is a "Fresh Start"

This is crucial: **orders from the previous tick do not exist in the next tick**. Each tick, your bot starts from scratch:

```
Tick 100:
  - You place a buy order for 10 units at 9,999
  - Only 5 units get filled
  - The other 5 → GONE

Tick 200:
  - Orders from tick 100 are GONE
  - You must place new orders if you want to continue buying
  - Your bot "wakes up" with a fresh state
```

> **Analogy:** Think of the movie Groundhog Day (or 50 First Dates). Every morning your bot wakes up with no memory of yesterday. The only thing it knows is what's written in `traderData` (like a note left on the nightstand).

### Processing Speed

Your bot must return results **quickly**. If your code takes too long, you may be penalized or skipped. Write simple, efficient code.

> **What just happened?** Time in Prosperity is divided into steps called ticks. Each tick, your bot receives new information and places new orders. Old orders vanish. Your bot has no natural memory between ticks.

---

## 8. TradingState — Your Information Package Each Tick

### What Does the System Send Your Bot?

Each tick, before your bot makes decisions, the system sends it an information package called `TradingState`. This package contains **everything you need to know** about the market at that moment.

Imagine you're the director of a company. Every morning, your assistant sends you a **summary report**: market prices, inventory levels, yesterday's transactions, your own notes from the day before. That's exactly what `TradingState` is.

### TradingState Structure

```python
def run(self, state: TradingState):
    # What does state contain?

    state.timestamp
    # Current tick number: 100, 200, 300...
    # Like the market's clock

    state.order_depths
    # Order books for all products
    # A dictionary: {"RAINFOREST_RESIN": OrderDepth(...), "KELP": OrderDepth(...)}
    # This is the most important info — tells you who is buying/selling what

    state.position
    # Your current position (inventory)
    # A dictionary: {"RAINFOREST_RESIN": 25, "KELP": -10}
    # Positive = you're holding, Negative = you owe
    # If a product isn't here, you DON'T have it in this dict (use .get()!)

    state.traderData
    # A string you sent from the previous tick
    # This is the ONLY "note" you can leave for yourself
    # First tick: this is an empty string ""

    state.market_trades
    # OTHER bots' trades from the previous tick
    # {"KELP": [Trade(symbol, price, quantity, buyer, seller, timestamp), ...]}
    # Helps you see "who bought what, at what price"

    state.own_trades
    # YOUR trades from the previous tick
    # Same format as market_trades but only your filled orders

    state.observations
    # External data (used in later rounds)
    # Example: prices from other exchanges, economic data
```

### Reading Position Safely

This is a very common mistake: if you haven't traded a product yet, it is **not in** `state.position`. If you access it directly, you get a **KeyError**!

```python
# ======================================
# WRONG — crashes if you haven't traded yet!
# ======================================
pos = state.position["RAINFOREST_RESIN"]
# KeyError: 'RAINFOREST_RESIN'   ← ERROR!

# ======================================
# CORRECT — use .get() with a default value
# ======================================
pos = state.position.get("RAINFOREST_RESIN", 0)
# If you have a position → returns the position (e.g., 25)
# If you don't have one → returns 0
```

### What Does Position Mean?

```python
pos = state.position.get("RAINFOREST_RESIN", 0)

# pos = 25  → You're HOLDING 25 units (long)
#             Like having 25 mangoes in your warehouse

# pos = 0   → You're holding nothing
#             Empty warehouse

# pos = -15 → You OWE 15 units (short)
#             Like having sold 15 mangoes you didn't own yet
#             → You need to buy 15 mangoes to pay back the debt
```

> **Real-world analogy:** Think of it like managing a warehouse:
> - **Positive:** You have stock in the warehouse → want to sell for profit
> - **Zero:** Warehouse is empty → free to buy or sell
> - **Negative:** You "borrowed" stock and already sold it → need to buy it back to repay

### Watching market_trades to Learn from Other Bots

```python
# Who traded KELP in the previous tick?
if "KELP" in state.market_trades:
    for trade in state.market_trades["KELP"]:
        print(f"  {trade.buyer} bought from {trade.seller}")
        print(f"  Price: {trade.price}, Quantity: {trade.quantity}")
        # Example: "Olivia bought from Bot_A, Price 2050, Quantity 5"
        # → Olivia is an "informed trader" — you might want to follow her!
```

> **What just happened?** Each tick, your bot receives a TradingState containing: order books, your position, your note from last tick, other bots' trades, and your own trades. Use `.get("PRODUCT", 0)` to read position safely.

---

## 9. Position Limit

### You Cannot Buy/Sell Unlimited Amounts

In the real world, if you have enough money, you can buy as much as you want. But in Prosperity, each product has a **position limit** — you can only hold up to ±N units.

### Think of It Like Warehouse Capacity

Imagine you have a warehouse that can hold **50 mangoes**:
- You can store **up to 50** mangoes (long +50)
- You can also "owe" **up to 50** mangoes (short -50)
- Total range is -50 to +50

```
         Position Limit = 50
  ←───────────────┼───────────────→
  -50            0             +50
  (max debt)   (empty)      (max stock)
```

### Limits for Each Product

| Product | Limit |
|---------|-------|
| RAINFOREST_RESIN | ±50 |
| KELP | ±50 |
| SQUID_INK | ±50 |
| (other products) | Check the problem statement each round |

> **Note:** Limits may change between rounds and products. Always read the problem statement carefully!

### Calculating Remaining Capacity

Before placing an order, you need to know how much more you can buy or sell:

```python
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # Example: pos = 20

# You're holding 20 units, limit is 50
# Can still buy: 50 - 20 = 30 more units
max_buy = LIMIT - pos     # 50 - 20 = 30

# Can still sell: 50 + 20 = 70?? Well, actually yes!
# If pos = 20, you can sell 20 (back to 0) + sell short 50 = 70
# → Because the position limit is ±50, so:
max_sell = LIMIT + pos    # 50 + 20 = 70
# This is correct! You can move from +20 all the way down to -50 = 70 steps
```

**Detailed Explanation:**

```
Currently: pos = +20

  -50 ......... 0 ......... +20 ....... +50
                              ^-- You are here

  ← max_sell = 70 →          ← max_buy = 30 →
  (from +20 to -50 = 70)     (from +20 to +50 = 30)
```

Another example with pos = -15:

```
Currently: pos = -15

  -50 ... -15 ......... 0 ......... +50
              ^-- You are here

  ← max_sell = 35 →    ← max_buy = 65 →
  (from -15 to -50)    (from -15 to +50)
  LIMIT + pos           LIMIT - pos
  50 + (-15) = 35      50 - (-15) = 65
```

### The System Does NOT Give You an Error!

This is the dangerous part: if you place an order that would exceed the limit, IMC **silently rejects** your order. No error message, no warning. The order simply doesn't execute.

```python
# Example: pos = 45, LIMIT = 50
# You place a buy order for 10 units
Order("RAINFOREST_RESIN", 9999, 10)
# Only 5 units get bought (50 - 45 = 5)
# The other 5 are SILENTLY REJECTED
# You won't know why your order didn't fully fill!
```

### CRITICAL: Update Capacity After Each Order!

If you place multiple orders in the same tick, you must recalculate capacity after each one:

```python
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 30
orders = []

# Order 1: Buy 10 units at 9,998
buy_amount_1 = 10
max_buy = LIMIT - pos                             # 50 - 30 = 20, enough!
orders.append(Order("RAINFOREST_RESIN", 9998, buy_amount_1))
pos += buy_amount_1                                # UPDATE: pos = 40

# Order 2: Buy 15 units at 9,999
buy_amount_2 = 15
max_buy = LIMIT - pos                             # 50 - 40 = 10, not enough for 15!
buy_amount_2 = min(buy_amount_2, max_buy)          # → only buy 10
orders.append(Order("RAINFOREST_RESIN", 9999, buy_amount_2))
pos += buy_amount_2                                # UPDATE: pos = 50 (full!)

# Order 3: Buy more?
max_buy = LIMIT - pos                             # 50 - 50 = 0 → can't buy any more!
```

> **Real-world analogy:** Think of warehouse capacity. You place 3 separate delivery orders. After each delivery, you must check how much space is left. If you don't, the third delivery might not fit — and you waste the shipping cost!

> **What just happened?** Every product has a position limit (e.g., ±50). You must calculate how much more you can buy/sell. The system does NOT warn you when you exceed limits — orders are silently rejected. Always update capacity after each order.

---

## 10. The run() Function — Your Bot's Heart

### Required Structure

Your bot MUST have this structure:

```python
# ================================================
# REQUIRED IMPORTS
# ================================================
from datamodel import OrderDepth, TradingState, Order
from typing import List
import json  # If you use JSON for traderData

# ================================================
# CLASS TRADER — MUST BE NAMED "Trader"
# ================================================
class Trader:

    # ================================================
    # run() FUNCTION — THE SYSTEM CALLS THIS EVERY TICK
    # ================================================
    def run(self, state: TradingState):

        # 1. Create a dict to hold orders for each product
        result = {}
        # result will look like: {"RAINFOREST_RESIN": [Order(...), Order(...)]}

        # 2. Conversions — used in later rounds
        conversions = 1
        # Round 1: just set to 1
        # Round 2+: related to product conversions (see round-specific guides)

        # 3. traderData — your note for the next tick
        traderData = ""
        # You can write any string (max 50,000 characters)

        # ==========================================
        # YOUR TRADING LOGIC GOES HERE
        # ==========================================

        # Example: read the order book for RAINFOREST_RESIN
        if "RAINFOREST_RESIN" in state.order_depths:
            order_depth = state.order_depths["RAINFOREST_RESIN"]
            orders = []

            # ... your buy/sell decision logic ...

            result["RAINFOREST_RESIN"] = orders

        # ==========================================
        # RETURN THE RESULT — MUST BE EXACTLY 3 VALUES
        # ==========================================
        return result, conversions, traderData
```

### Explanation of Each Part

**`result` — Your Orders:**
```python
result = {}

# Add orders for RAINFOREST_RESIN
result["RAINFOREST_RESIN"] = [
    Order("RAINFOREST_RESIN", 9998, 5),    # Buy 5 units at 9,998
    Order("RAINFOREST_RESIN", 10002, -3),   # Sell 3 units at 10,002
]

# Add orders for KELP
result["KELP"] = [
    Order("KELP", 2048, 10),               # Buy 10 KELP at 2,048
]

# Products with no orders? Don't need to add them to result
```

**`conversions` — Conversions:**
```python
conversions = 1    # Round 1: set to 1, has no effect
                   # Round 2+: number of conversions (see round guides)
```

**`traderData` — Your Note:**
```python
# Any string is fine, as long as it's under 50,000 characters
traderData = "hello"                           # Simple text
traderData = str(10000.5)                      # Save a number
traderData = json.dumps({"price": 10000.5})    # Save multiple values
```

### Mandatory Rules

1. **Class must be named `Trader`** — not `MyBot`, not `Algorithm`
2. **Function must be named `run`** — not `trade`, not `execute`
3. **Must return EXACTLY 3 values:** `result, conversions, traderData`
   - Missing a value → ERROR
   - Extra value → ERROR
4. **result is a dict** — key is product name (string), value is list of Order objects
5. **Each Order must use the exact product name:** `Order("RAINFOREST_RESIN", price, qty)` — no typos

### Simplest Possible Bot

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}

        # This bot does one thing: buy RAINFOREST_RESIN at 9,995
        orders = []
        orders.append(Order("RAINFOREST_RESIN", 9995, 1))  # Buy 1 unit
        result["RAINFOREST_RESIN"] = orders

        return result, 1, ""
```

This bot is very naive — it only buys and never sells, so it will quickly hit the position limit. But it shows the basic structure!

> **What just happened?** The run() function is where you write your trading logic. The system calls it every tick. You MUST return 3 values: result (dict of orders), conversions (number), and traderData (string). The class must be named Trader, the function must be named run.

---

## 11. traderData — Memory Between Ticks

### The Problem: Your Bot Has Amnesia

As mentioned in the Tick section, your bot is **completely reset** after every tick. It's like losing your memory every 100 milliseconds. You don't remember the previous tick's price, what you traded, nothing.

But to trade intelligently, you NEED historical information! For example:
- Average price over the last 20 ticks (to calculate EMA)
- How many trades you've made today
- Whether the price trend is going up or down

### The Solution: traderData

`traderData` is a **string** that you send at the end of this tick, and receive back at the beginning of the next tick.

```
Tick 100:
  state.traderData = ""          ← First tick, empty string
  ... your logic ...
  return result, 1, "my_note"   ← Send "my_note" to next tick

Tick 200:
  state.traderData = "my_note"   ← Received "my_note" from tick 100!
  ... your logic ...
  return result, 1, "new_note"  ← Send "new_note" to tick 300

Tick 300:
  state.traderData = "new_note"  ← Received "new_note" from tick 200!
```

### Simple Example: Saving a Single Number

```python
class Trader:
    def run(self, state: TradingState):
        result = {}

        # Read the price from the previous tick
        if state.traderData:
            # We have data from the previous tick
            last_mid_price = float(state.traderData)
            print(f"Last tick's mid price: {last_mid_price}")
        else:
            # First tick — no data yet
            last_mid_price = None
            print("First tick, no previous data")

        # Calculate current mid price
        od = state.order_depths["RAINFOREST_RESIN"]
        best_ask = min(od.sell_orders.keys())
        best_bid = max(od.buy_orders.keys())
        current_mid = (best_ask + best_bid) / 2

        # Save mid price for the next tick to read
        traderData = str(current_mid)   # Example: "10000.5"

        return result, 1, traderData
```

### Advanced Example: Saving Multiple Values with JSON

When you need to save multiple pieces of information, use JSON:

```python
import json

class Trader:
    def run(self, state: TradingState):
        result = {}

        # =============================================
        # READ data from the previous tick
        # =============================================
        if state.traderData:
            data = json.loads(state.traderData)
            # data is now a Python dictionary
        else:
            # First tick — initialize empty data
            data = {
                "prices": [],         # Store price history
                "trade_count": 0,     # Count trades
                "last_action": None   # Last action taken
            }

        # =============================================
        # UPDATE data with this tick's information
        # =============================================
        od = state.order_depths["RAINFOREST_RESIN"]
        best_ask = min(od.sell_orders.keys())
        best_bid = max(od.buy_orders.keys())
        current_mid = (best_ask + best_bid) / 2

        # Add current price to the list
        data["prices"].append(current_mid)

        # Only keep the last 20 prices (save memory)
        if len(data["prices"]) > 20:
            data["prices"] = data["prices"][-20:]

        # Calculate EMA if we have enough data
        if len(data["prices"]) >= 5:
            ema = sum(data["prices"][-5:]) / 5  # Simple average of last 5 prices
            print(f"EMA(5): {ema}")

        # =============================================
        # SEND data to the next tick
        # =============================================
        traderData = json.dumps(data)
        # Example: '{"prices": [10000, 10001, 9999], "trade_count": 0, "last_action": null}'

        return result, 1, traderData
```

### Limit: 50,000 Characters

In Prosperity 4, traderData is **capped at 50,000 characters**. Sounds like a lot, but it can fill up fast if you store large amounts of data:

```python
# Example: each number takes about 7-10 characters
# 50,000 / 10 = about 5,000 numbers
# → Enough for 5,000 price history entries, or 250 prices x 20 products

# Tips to save space:
# 1. Only keep the last N prices (don't store everything)
# 2. Round numbers (10000.12345 → 10000.1)
# 3. Use short keys ("p" instead of "prices")
```

### How Frankfurt Hedgehogs Used traderData

They stored: EMA prices for each product, trader information (who bought what), ETF premiums, and many other strategic values — all as JSON.

> **Real-world analogy:** Imagine you lose your memory every day. Before going to sleep, you write a note on a piece of paper with important things: "Mango price today was $2.00, sold 50 units, customer named Olivia buys a lot." The next morning, you read the note and know what to do. traderData is that piece of paper.

> **What just happened?** traderData is the only way for your bot to "remember" information between ticks. It's a string you send at the end of this tick and receive at the start of the next. Use JSON to store multiple values. Maximum 50,000 characters in Prosperity 4.

---

# PART 4: LEARNING ROADMAP

---

## 12. Roadmap from Round 1 to Round 5

### Overview of All Rounds

```
Round 1: Market Making
├── RAINFOREST_RESIN  ← Fixed fair value = 10,000
│   └── Type: Stable price, low volatility
│   └── Strategy: Buy below 10,000, sell above 10,000
│
├── KELP              ← Slowly changing fair value (random walk)
│   └── Type: Price "wanders" up and down gently
│   └── Strategy: Calculate EMA to track the fair value
│
└── SQUID_INK         ← Highly volatile, has "informed trader" (Olivia)
    └── Type: Price jumps a lot, hard to predict
    └── Strategy: Track Olivia and other traders' behavior

Round 2: ETF Statistical Arbitrage
├── PICNIC_BASKET1 = 6 x Croissants + 3 x Jams + 1 x Djembes
├── PICNIC_BASKET2 = 4 x Croissants + 2 x Jams
└── Strategy: Basket price oscillates around the sum of components
    └── When basket is more expensive than components → sell basket, buy components
    └── When basket is cheaper than components → buy basket, sell components

Round 3: Options
├── VOLCANIC_ROCK (underlying asset)
├── VOLCANIC_ROCK_VOUCHER (call options, 5 strike prices)
└── Strategy: IV scalping + mean reversion
    └── Requires understanding Black-Scholes, implied volatility, delta

Round 4: Location Arbitrage
├── MAGNIFICENT_MACARONS
└── Strategy: Buy from external exchange → sell on the local exchange
    └── Uses conversions and observations

Round 5: Trader IDs
└── No new products — optimize all previous strategies
    └── Market trades now include information: who bought/sold
    └── Use this to identify "informed traders" like Olivia
```

### Step-by-Step Learning Path

Here is the recommended learning order — from easy to hard:

| Step | Concept to Learn | Needed For |
|------|-----------------|------------|
| 1 | Order book, taking, position limit | RAINFOREST_RESIN basics |
| 2 | Wall mid, making, overbidding | RAINFOREST_RESIN advanced |
| 3 | Dynamic fair value (EMA), traderData JSON | KELP |
| 4 | market_trades, pattern detection | SQUID_INK |
| 5 | Synthetic price, spread, mean reversion | Baskets (Round 2) |
| 6 | Black-Scholes, implied volatility, delta | Options (Round 3) |
| 7 | Conversion, external market, arbitrage | Macarons (Round 4) |

### Advice

1. **Start with RAINFOREST_RESIN** — the easiest product because of its fixed fair value
2. **Get one product working well before moving to the next** — don't try to do everything at once
3. **Read the problem statement carefully each round** — rules and products can change
4. **Test with the backtester** before submitting — don't submit untested code
5. **Review the logs** after each submission to understand what your bot did wrong

> **What just happened?** The competition has 5 rounds of increasing difficulty. Start with market making (buy low, sell high), then move to statistical arbitrage, options, location arbitrage, and finally optimization with trader IDs.

---

# PART 5: REFERENCE

---

## 13. Common Mistakes

### Mistake 1: Forgetting abs() for sell_orders Volumes

```python
# ======== WRONG ========
od = state.order_depths["RAINFOREST_RESIN"]
best_ask = min(od.sell_orders.keys())
volume = od.sell_orders[best_ask]       # → -10 (NEGATIVE!)
# If you use this volume to place a buy order:
Order("RAINFOREST_RESIN", best_ask, volume)  # → Buy -10 = SELL 10?! WRONG!

# ======== CORRECT ========
volume = abs(od.sell_orders[best_ask])  # → 10 (POSITIVE)
Order("RAINFOREST_RESIN", best_ask, volume)  # → Buy 10 units. CORRECT!
```

**Why it happens:** Sell orders in IMC have negative volumes by convention. Beginners almost always forget this.

### Mistake 2: Not Checking Position Limit Before Ordering

```python
# ======== WRONG ========
# No limit check, placing buy for 30 units
orders.append(Order("RAINFOREST_RESIN", 9998, 30))
# If pos is already 40 and LIMIT = 50 → only 10 can fill, 20 silently rejected!

# ======== CORRECT ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)
max_buy = LIMIT - pos
buy_amount = min(30, max_buy)  # Ensure we don't exceed limit
if buy_amount > 0:
    orders.append(Order("RAINFOREST_RESIN", 9998, buy_amount))
```

**Why it happens:** The system doesn't warn you, so you don't realize orders are being rejected.

### Mistake 3: Forgetting the Negative Sign for Sell Quantity

```python
# ======== WRONG ========
Order("RAINFOREST_RESIN", 10002, 5)    # Positive quantity = BUY, not SELL!

# ======== CORRECT ========
Order("RAINFOREST_RESIN", 10002, -5)   # Negative quantity = SELL. Correct!
```

**Why it happens:** Instinct is to write positive numbers. You must remember: negative = sell.

### Mistake 4: Not Using .get() for Position

```python
# ======== WRONG ========
pos = state.position["KELP"]           # KeyError if you haven't traded KELP!

# ======== CORRECT ========
pos = state.position.get("KELP", 0)    # Returns 0 if no position yet
```

**Why it happens:** On the first tick or if you haven't traded a product yet, the position dictionary won't have that key.

### Mistake 5: Returning Wrong Number of Values from run()

```python
# ======== WRONG — returning 2 values ========
return result, traderData
# TypeError: Must return 3 values!

# ======== WRONG — returning 4 values ========
return result, conversions, traderData, extra_data
# TypeError: Too many values!

# ======== CORRECT — returning exactly 3 values ========
return result, conversions, traderData
# result: dict, conversions: int, traderData: str
```

### Mistake 6: Not Updating Capacity After Each Order in the Same Tick

```python
# ======== WRONG ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 40
orders = []

# Order 1: Buy 8 units
orders.append(Order("RAINFOREST_RESIN", 9998, 8))
# pos is STILL 40 in our code — not updated!

# Order 2: Buy 8 more units
max_buy = LIMIT - pos  # 50 - 40 = 10, looks fine
orders.append(Order("RAINFOREST_RESIN", 9999, 8))
# TOTAL = 16 units! But we can only buy 10 (50 - 40)
# → 6 units silently rejected!

# ======== CORRECT ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 40
orders = []

# Order 1: Buy 8 units
buy1 = min(8, LIMIT - pos)  # min(8, 10) = 8
orders.append(Order("RAINFOREST_RESIN", 9998, buy1))
pos += buy1                  # UPDATE! pos = 48

# Order 2: Buy 8 more units
buy2 = min(8, LIMIT - pos)  # min(8, 2) = 2 — only 2 left!
if buy2 > 0:
    orders.append(Order("RAINFOREST_RESIN", 9999, buy2))
    pos += buy2              # UPDATE! pos = 50
```

---

## 14. Submission Checklist

Before submitting your Python file, verify all of the following:

### Basic Structure
- [ ] Class is named `Trader` (not anything else)
- [ ] Function is named `run` (not anything else)
- [ ] `run()` returns **exactly 3 values:** `result, conversions, traderData`
- [ ] All necessary imports are present (`from datamodel import ...`)

### Data Handling
- [ ] Using `abs()` when reading volumes from `sell_orders`
- [ ] Using `.get("PRODUCT", 0)` when reading `state.position`
- [ ] Handling empty `state.traderData` on the first tick

### Position Limits
- [ ] Checking position limit before placing orders
- [ ] Updating capacity after **each** order in the same tick
- [ ] Sell orders have **negative** quantity (`-5`, not `5`)

### traderData
- [ ] traderData is a **string** (use `json.dumps()` if needed)
- [ ] Does not exceed **50,000 characters**
- [ ] Handles empty `state.traderData` on the first tick

### Clean Code
- [ ] No `input()` (no keyboard input allowed)
- [ ] No `time.sleep()` (no sleeping allowed)
- [ ] No banned libraries (check the problem statement)
- [ ] Tested with the backtester
- [ ] Reviewed logs after testing — no errors

### Prosperity 4 Specific
- [ ] (Round 2+) Has `bid()` method if using conversions
- [ ] traderData under 50,000 characters

> **Tip:** Print this checklist and check items off every time you submit!

---

## 15. Glossary

| English | Definition |
|---------|-----------|
| **Order Book** | All pending buy/sell orders displayed together |
| **Bid** | The highest price a buyer is willing to pay |
| **Ask** | The lowest price a seller is willing to accept |
| **Spread** | The gap between the ask and bid prices |
| **Position** | The number of units you currently hold |
| **Long** | Position > 0 — you own units |
| **Short** | Position < 0 — you owe units |
| **Fill** | An order successfully executing (trading) |
| **Fair Value** | The estimated "true" price of a product |
| **Wall Mid** | The average of the bid wall and ask wall prices |
| **Market Making** | Placing both buy and sell orders around fair value to earn the spread |
| **Taking** | Crossing the spread to fill immediately (aggressive) |
| **Making** | Placing passive orders that wait to be filled |
| **Overbid** | A buy order priced above the current best bid |
| **Undercut** | A sell order priced below the current best ask |
| **PnL** | Profit and Loss |
| **EMA** | Exponential Moving Average — a weighted average that favors recent data |
| **Arbitrage** | Buying cheap in one place and selling expensive in another |
| **Mean Reversion** | The tendency of prices to return to their average over time |
| **Informed Trader** | A bot that has advance knowledge of price movements (e.g., Olivia) |
| **XIRECs** | Prosperity 4's in-game currency |
| **SeaShells** | Prosperity 3's in-game currency (outdated) |
| **Limit Order** | An order to buy/sell at a specific price or better |
| **Market Order** | An order at the best available price (NOT used in Prosperity) |
| **Price-Time Priority** | Best price gets matched first; same price means earliest order first |
| **Tick** | One time step in the simulation; timestamp increments by 100 |
| **Conversion** | Exchanging one product for another (used in Round 2+) |
| **Partial Fill** | Only part of an order gets executed |
| **FIFO** | First In, First Out — earlier orders get matched before later ones at the same price |

---

*Based on IMC Prosperity 4 official documentation + Frankfurt Hedgehogs (Top 2, Prosperity 3)*
