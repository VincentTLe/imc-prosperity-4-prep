# Round 2 - PICNIC BASKETS: Trading the ETF Spread

> **Prerequisite:** You should already know the basics from `General_EN.md` and the Round 1 Resin guide.
> In particular, you need to understand order books, `wall_mid`, positions, and why `buy` means positive volume while `sell` means negative volume.

---

# PART 1: WHAT IS THE ETF BASKET?

---

## 1. What Are PICNIC_BASKET1 and PICNIC_BASKET2?

In Round 2, the market introduces two new basket products:

| Product | What it contains |
|---------|-------------------|
| **PICNIC_BASKET1** | 6 x CROISSANTS + 3 x JAMS + 1 x DJEMBES |
| **PICNIC_BASKET2** | 4 x CROISSANTS + 2 x JAMS |

Think of a basket like a pre-made shopping pack.
Instead of buying the ingredients one by one, the market also sells you a bundle.

The important point is:

- The basket is not magic.
- Its value should be close to the sum of its ingredients.
- If the basket gets too expensive compared with the ingredients, it is probably overvalued.
- If the basket gets too cheap compared with the ingredients, it is probably undervalued.

That is the whole Round 2 idea.

---

## 2. Why Is This an ETF Problem?

An ETF is just a basket of assets that should roughly track its underlying parts.
If the parts move up together, the ETF should usually move up too.
If the ETF drifts too far away from the value of its parts, you can trade that difference.

In this round, the key question is:

> **Is the basket price higher or lower than the synthetic value of the ingredients?**

If yes, the basket is mispriced.
If no, do nothing.

This is much more useful than trying to guess where the basket will go in isolation.
The basket is not traded because it is "interesting".
It is traded because it can be compared to something else.

---

## 3. The Practical Fair Value

The Frankfurt Hedgehogs logic uses the order book to estimate a fair price for each product.
For each ingredient, the best estimate is the **wall_mid**:

```text
wall_mid = (bid_wall + ask_wall) / 2
```

Then the basket's synthetic value is:

```text
synthetic value = sum(ingredient wall_mid x basket factor)
```

For example:

- Basket 1 synthetic value = `6 * CROISSANTS + 3 * JAMS + 1 * DJEMBES`
- Basket 2 synthetic value = `4 * CROISSANTS + 2 * JAMS`

The trading signal is then:

```text
spread = basket wall_mid - synthetic value - running premium
```

If the spread is positive and large, the basket is expensive.
If the spread is negative and large, the basket is cheap.

The "running premium" is just a slowly updated offset.
It exists because the basket may have a small persistent bias relative to the raw synthetic value.

---

# PART 2: BASIC STRATEGY

---

## 4. Core Idea: Sell Rich, Buy Cheap

This is the simplest version of the strategy:

- Basket is above fair value -> **sell basket**
- Basket is below fair value -> **buy basket**

You do not need to predict the future price path.
You only need to compare the basket against its ingredients.

### Simple example

Imagine the order book says:

- CROISSANTS wall_mid = 100
- JAMS wall_mid = 50
- DJEMBES wall_mid = 80

Then Basket 1 synthetic value is:

```text
6 * 100 + 3 * 50 + 1 * 80 = 830
```

If PICNIC_BASKET1 is trading around 900, then the basket is rich.
If it is trading around 780, then the basket is cheap.

That is the whole decision rule.

---

## 5. The Two Baskets Are Not the Same

The two baskets look similar, but they are different tools:

| Basket | Main use |
|--------|----------|
| **PICNIC_BASKET1** | Stronger link to all three ingredients |
| **PICNIC_BASKET2** | Simpler basket, only uses CROISSANTS and JAMS |

Basket 1 is more "complete" because it includes DJEMBES.
Basket 2 is cleaner because it ignores DJEMBES completely.

That matters because:

- Basket 1 reacts to all three ingredients.
- Basket 2 reacts only to CROISSANTS and JAMS.

So when you compare the baskets, you should never treat them as the same product.

---

## 6. Position Limits

The Frankfurt Hedgehogs bot uses separate limits for the baskets:

- PICNIC_BASKET1: `60`
- PICNIC_BASKET2: `100`

These limits are smaller than the constituent limits because the baskets are traded as higher-impact instruments.

You should always check your current position before submitting orders.
If you forget this, you will either:

- hit the exchange limit and lose trades, or
- overtrade and take risk you did not intend to take.

---

# PART 3: STEP-BY-STEP TRADING LOGIC

---

## 7. What the Bot Does Each Tick

The logic is:

1. Read the basket order book.
2. Read the constituent order books.
3. Compute synthetic value from the constituent wall mids.
4. Subtract the running premium.
5. Compare basket wall_mid with synthetic value.
6. If the basket is too rich, sell it.
7. If the basket is too cheap, buy it.
8. If you already have inventory, close it when the spread returns to normal.

### Pseudocode

```python
synthetic = 6 * croissants_mid + 3 * jams_mid + 1 * djembes_mid   # basket 1
spread = basket_mid - synthetic - premium

if spread > threshold:
    sell basket
elif spread < -threshold:
    buy basket
elif spread is near 0 and position != 0:
    reduce or close position
```

That is the simplest useful version of the strategy.

---

## 8. Why the Running Premium Matters

In practice, the basket is often not centered exactly on raw synthetic value.
It may trade with a small average offset.

If you ignore that offset, you can end up doing this:

- Buying a basket that is not actually cheap enough
- Selling a basket that is not actually rich enough

The running premium fixes that problem.
It makes your comparison more stable over time.

Frankfurt starts with a guessed premium and then updates it as new prices arrive.
That is a practical compromise:

- simple enough to maintain,
- flexible enough to follow the market,
- and much safer than hardcoding one constant forever.

---

## 9. A Concrete Tick Example

Suppose:

- PICNIC_BASKET1 wall_mid = 915
- CROISSANTS wall_mid = 100
- JAMS wall_mid = 50
- DJEMBES wall_mid = 80
- running premium = 20

Then:

```text
synthetic = 6*100 + 3*50 + 1*80 = 830
spread = 915 - 830 - 20 = 65
```

If the threshold is 80, this is not enough yet.
If the threshold is 50, this is a sell signal.

So the exact threshold matters, but the decision rule stays the same.

---

## 10. Why This Works

This strategy works because the basket and its ingredients are linked.
They are not independent assets.

If the basket becomes expensive enough relative to the components, other traders will eventually push it back toward fair value.
Your job is to step in before that correction finishes.

In other words:

- you are not betting on direction,
- you are betting on convergence.

That is the essence of statistical arbitrage in this round.

---

# PART 4: SUMMARY

---

## 11. What You Should Remember

| Idea | Meaning |
|------|---------|
| Basket 1 | `6 CROISSANTS + 3 JAMS + 1 DJEMBES` |
| Basket 2 | `4 CROISSANTS + 2 JAMS` |
| Fair value | Sum of constituent wall mids with basket factors |
| Signal | Basket wall_mid minus synthetic value |
| Trade rich basket | Sell it |
| Trade cheap basket | Buy it |
| Practical fix | Subtract running premium |

If you understand that table, you understand the round.

---

## 12. Next Step

Read the Round 2 constituents guide next.
That guide explains why the individual ingredients matter on their own, and how they are used both as pricing inputs and as hedges for the basket trades.

---

*Based on the Round 1 Resin teaching style and the Frankfurt Hedgehogs Round 2 basket logic.*
