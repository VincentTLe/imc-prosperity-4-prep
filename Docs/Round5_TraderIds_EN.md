# Round 5 - TRADER IDS: Learn to Read Who Is Trading

> **Prerequisite:** Read `General_EN.md` first, and understand the Round 1 and Round 4 guides.
> This round is about using trade history and counterparty identity to infer direction.

---

# PART 1: WHAT IS A TRADER ID STRATEGY?

---

## 1. Why Trader IDs Matter

Sometimes the most important signal is not the price.
It is **who** is trading.

If a specific trader tends to buy before prices rise, their buy activity can be a useful signal.
If a specific trader tends to sell before prices fall, their sells can also be useful.

In the Frankfurt Hedgehogs material, the classic example was **Olivia**.
They noticed that Olivia's trades could be used as a direction signal.

Beginner version:

- if Olivia buys, the market may be bullish
- if Olivia sells, the market may be bearish

This is not magic.
It is pattern recognition on trade logs.

---

## 2. What You Are Looking At

The exchange gives you recent trades in `state.market_trades`.

Each trade usually tells you:

- timestamp
- price
- quantity
- buyer name or ID
- seller name or ID

Your job is to watch for a trader with a repeatable pattern.

If the pattern is strong enough, you can follow it.

---

## 3. The Core Idea

The simplest strategy is:

1. Detect a target trader's latest buy or sell.
2. Store that signal in `traderData`.
3. Use the signal to take a position in the same direction.
4. Refresh the signal every tick.

That is the entire structure.

---

# PART 2: BUILDING A SIMPLE SIGNAL

---

## 4. Why Persistence Is Needed

Trade history does not always tell the whole story forever.
Sometimes the relevant trade scrolls out of the most recent window.

That is why Frankfurt persisted timestamps in `traderData`.

Beginner version:

- `traderData` is your memory
- use it to remember the last meaningful buy and sell time

Without that, your bot forgets the signal too quickly.

---

## 5. A Simple Direction Rule

Use the latest timestamp to infer direction:

- if the target trader's last buy is newer than the last sell, they are bullish
- if the target trader's last sell is newer than the last buy, they are bearish
- if you have no signal yet, stay neutral

That is much easier to reason about than trying to predict the market directly.

---

# PART 3: A BEGINNER-FRIENDLY COPY TRADER

---

## 6. Example Code

```python
from datamodel import Order, TradingState
import json


class Trader:
    def run(self, state: TradingState):
        product = "SQUID_INK"
        target_id = "Olivia"
        limit = 50
        orders = []

        last_buy_ts = None
        last_sell_ts = None

        if state.traderData:
            try:
                saved = json.loads(state.traderData)
                last_buy_ts = saved.get("last_buy_ts")
                last_sell_ts = saved.get("last_sell_ts")
            except Exception:
                pass

        for trade in state.market_trades.get(product, []):
            if trade.buyer == target_id:
                if last_buy_ts is None or trade.timestamp > last_buy_ts:
                    last_buy_ts = trade.timestamp
            if trade.seller == target_id:
                if last_sell_ts is None or trade.timestamp > last_sell_ts:
                    last_sell_ts = trade.timestamp

        signal = "NEUTRAL"
        if last_buy_ts is not None and last_sell_ts is None:
            signal = "BULLISH"
        elif last_sell_ts is not None and last_buy_ts is None:
            signal = "BEARISH"
        elif last_buy_ts is not None and last_sell_ts is not None:
            signal = "BULLISH" if last_buy_ts > last_sell_ts else "BEARISH"

        position = state.position.get(product, 0)

        if signal == "BULLISH":
            qty = limit - position
            if qty > 0:
                orders.append(Order(product, 10**9, qty))
        elif signal == "BEARISH":
            qty = limit + position
            if qty > 0:
                orders.append(Order(product, -10**9, -qty))

        next_state = json.dumps({
            "last_buy_ts": last_buy_ts,
            "last_sell_ts": last_sell_ts,
        })

        return {product: orders}, 0, next_state
```

### What this code is doing

- watches `state.market_trades`
- checks whether Olivia is buyer or seller
- saves the newest timestamps in `traderData`
- turns that into a bullish or bearish signal
- trades in that direction

The big idea is not the exact prices in this toy example.
The big idea is the signal logic.

---

## 7. Why This Is Useful

If a trader is consistently informed, copying their direction can be profitable.

This is especially useful when:

- the trader is early
- the market is slow to react
- the signal is cleaner than the order book

Frankfurt Hedgehogs used this idea on `SQUID_INK` by persisting the relevant trade timestamps and acting on the direction of Olivia's activity.

---

# PART 4: HOW TO TURN SIGNAL INTO A TRADE

---

## 8. Do Not Overcomplicate the Entry

Once you know the direction, the simplest response is:

- if bullish, move long
- if bearish, move short

If you want to be more careful, scale in gradually.
But for a beginner, a clear direction response is easier to debug.

The most important thing is:

- make sure the signal is real
- make sure the trader ID is correct
- make sure you are not reacting to stale data

---

## 9. Position Limit Still Matters

Copy trading is not exempt from risk limits.

If you are already long and the signal says bullish again, check capacity before buying more.
If you are already short and the signal says bearish again, check capacity before selling more.

The same `max_buy` and `max_sell` discipline from Round 1 still applies.

---

## 10. A Better Beginner Pattern

If you want a safer first version, do this:

1. Detect the signal.
2. Save it.
3. Compare it to your current position.
4. Trade only when the signal is fresh.

That keeps you from overreacting to one noisy print.

---

# PART 5: WALK THROUGH AN EXAMPLE

---

## 11. Example Tick

Suppose:

- Olivia buys `SQUID_INK` at timestamp 1200
- later, no new Olivia sell appears
- your bot sees her latest action as bullish

Then your logic should say:

- the informed trader is buying
- I should also lean long

If Olivia later sells at timestamp 1250:

- the signal flips bearish
- your bot should stop behaving bullish

That is why timestamps matter more than just a single recent trade.

---

## 12. What to Store in traderData

Keep only the minimum necessary memory.

Good things to store:

- last buy timestamp
- last sell timestamp
- a small signal flag
- a compact rolling count

Bad things to store:

- full raw trade history
- huge logs
- anything that grows without limit

`traderData` is limited, so keep it lean.

---

# PART 6: COMMON MISTAKES

---

## 13. Mistakes Beginners Make

1. Forgetting to persist the signal across ticks.
2. Confusing buyer ID and seller ID.
3. Reacting to stale trades as if they were new.
4. Overfitting to one trader without checking consistency.
5. Ignoring position limits when copying a strong signal.

The most common bug is simple:

- the trader trades
- you see the trade
- but you fail to save the timestamp
- so next tick you forget it

That turns a signal strategy into random behavior.

---

## 14. Beginner Roadmap

Start here:

1. Inspect `state.market_trades`.
2. Find one target trader ID.
3. Record last buy and sell timestamps.
4. Store them in `traderData`.
5. Convert the timestamps into bullish or bearish direction.
6. Trade with the signal, while respecting limits.

That is enough to get a working first version.

---

*Based on the Round 5 training material and Frankfurt Hedgehogs' copy-trading approach: track a target trader, persist timestamps, infer direction, and trade with the signal.*
