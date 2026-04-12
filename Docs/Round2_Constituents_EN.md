# Round 2 - THE THREE INGREDIENTS: CROISSANTS, JAMS, AND DJEMBES

> **Prerequisite:** You should already understand the basket guide.
> This guide explains the three ingredients on their own, and how they connect back to the two Picnic Baskets.

---

# PART 1: WHAT ARE THE CONSTITUENTS?

---

## 1. The Three Products

Round 2 adds three individual products:

| Product | Role |
|---------|------|
| **CROISSANTS** | Ingredient in both baskets |
| **JAMS** | Ingredient in both baskets |
| **DJEMBES** | Ingredient in Basket 1 only |

These are the building blocks of the baskets.
The baskets are just weighted combinations of these products.

The key formulas are:

```text
PICNIC_BASKET1 = 6 x CROISSANTS + 3 x JAMS + 1 x DJEMBES
PICNIC_BASKET2 = 4 x CROISSANTS + 2 x JAMS
```

So if you understand the ingredients, you understand the basket.

---

## 2. Why These Products Matter

The ingredients matter for two reasons:

1. They let you compute the basket's synthetic value.
2. They let you hedge basket inventory after you trade the basket.

That means the constituents are not just "extra products".
They are part of the pricing model.

If Basket 1 is cheap, you do not only want to know that Basket 1 is cheap.
You also want to know what the underlying ingredients are doing, because they tell you:

- whether the basket is actually mispriced,
- and how much offsetting exposure you need.

---

## 3. Wall Mid Is the Fair Price Estimate

For each constituent, the Frankfurt Hedgehogs bot uses the same idea as in Round 1:

```text
wall_mid = (bid_wall + ask_wall) / 2
```

That gives a practical estimate of the current fair value.

Why use wall_mid instead of the raw mid?

- The top-of-book can be noisy.
- The wall levels usually show where the real liquidity sits.
- Averaging the walls gives a more stable price to compare against the basket.

So the constituents are not just traded on their own.
They are also used to build a cleaner synthetic basket price.

---

# PART 2: HOW THEY RELATE TO THE BASKETS

---

## 4. Croissants

Croissants is the most important ingredient in the round.

Why?

- It appears in both baskets.
- It has the largest weight in both basket formulas.
- It is also the product where the Frankfurt Hedgehogs bot looks for an "informed trader" signal.

That makes CROISSANTS special:

- it is an input to basket pricing,
- and it is also its own standalone trading opportunity.

If Croissants moves, both baskets are affected.
If Basket 1 or Basket 2 moves, Croissants may also need to be hedged.

---

## 5. Jams

Jams is the shared middle ingredient.

It appears in both baskets, but with different weights:

- Basket 1 uses 3 x JAMS
- Basket 2 uses 2 x JAMS

That means Jams has a broad effect on the basket spread.
If Jams is expensive, both baskets become more expensive synthetically.
If Jams is cheap, both baskets become cheaper synthetically.

Jams is therefore a useful hedge ingredient when you have basket exposure.

---

## 6. Djembes

Djembes only appears in Basket 1.

That makes it the cleanest way to separate Basket 1 from Basket 2.

If Djembes moves:

- Basket 1 synthetic value changes,
- Basket 2 synthetic value does not.

This is useful because it gives Basket 1 its own extra source of movement.
In practice, that also means Basket 1 is slightly more complex than Basket 2.

Djembes is also why Basket 1 cannot be treated as "just another CROISSANTS + JAMS product".

---

## 7. A Simple Mental Model

You can think about the products like this:

```text
Croissants -> shared base ingredient
Jams       -> shared support ingredient
Djembes    -> Basket 1 only ingredient
```

Or even more simply:

- CROISSANTS moves both baskets.
- JAMS moves both baskets.
- DJEMBES moves only Basket 1.

That is the practical relationship you need to remember.

---

# PART 3: HOW THE BOT USES THE CONSTITUENTS

---

## 8. Constituents as Pricing Inputs

The first job of the constituent books is to estimate synthetic basket value.

Example for Basket 1:

```text
synthetic_1 = 6 * croissants_mid + 3 * jams_mid + 1 * djembes_mid
```

Example for Basket 2:

```text
synthetic_2 = 4 * croissants_mid + 2 * jams_mid
```

Once you have these numbers, you can compare them to the basket wall mid.
That is what creates the basket trading signal.

So even though you may not always trade the constituents aggressively, you still need them for valuation.

---

## 9. Constituents as Hedge Instruments

When the bot takes a basket position, it does not want to carry all that exposure blindly.
It uses the ingredients to reduce risk.

The Frankfurt Hedgehogs code does this with a partial hedge:

```text
expected hedge position = - basket exposure x basket factor x hedge factor
```

The hedge factor is `0.5`, which means the bot only offsets about half of the basket exposure.

Why only half?

- It reduces risk.
- It still leaves some room to profit if the spread keeps moving in the right direction.
- It avoids over-hedging into a flat or unstable book.

This is a practical compromise, not a theoretical law.

---

## 10. What the Hedge Means in Practice

Suppose you buy Basket 1.
Then you are implicitly long:

- CROISSANTS
- JAMS
- DJEMBES

because Basket 1 is made from those ingredients.

To avoid carrying too much unwanted exposure, you sell some of those ingredients separately.
That is the hedge.

If you short Basket 1, the hedge goes the other way:

- you buy some ingredients back.

This keeps the basket trade focused on the spread instead of on the direction of the underlying ingredients.

---

## 11. Why Croissants Gets Special Treatment

In the Frankfurt Hedgehogs strategy, CROISSANTS is not only a basket ingredient.
It is also watched for informed-trader behavior.

That matters because if someone with better information is buying or selling Croissants, the baskets can be indirectly affected.

So Croissants plays two roles:

1. It helps determine basket fair value.
2. It helps infer whether the basket signal should be adjusted.

That is why the bot treats CROISSANTS as more than just one more line in the formula.

---

## 12. Position Limits

The constituent limits are larger than the basket limits:

- CROISSANTS: `250`
- JAMS: `350`
- DJEMBES: `60`

That makes sense because you often need more constituent volume to hedge basket exposure.

If you ignore those limits, the hedge can fail even when the basket trade is correct.

So the safe order of thought is:

1. Decide the basket trade.
2. Estimate the hedge.
3. Check the constituent limits.
4. Submit only the volume you can actually carry.

---

# PART 4: STEP-BY-STEP EXAMPLE

---

## 13. Basket 1 Example

Suppose the order books imply:

- CROISSANTS wall_mid = 100
- JAMS wall_mid = 50
- DJEMBES wall_mid = 80

Then Basket 1 synthetic value is:

```text
6*100 + 3*50 + 1*80 = 830
```

If PICNIC_BASKET1 is trading at 900, then the basket is rich relative to its parts.
If your threshold says the spread is large enough, you sell the basket.

Then you hedge part of that basket exposure with the constituents.
That is the link between the basket guide and this guide.

---

## 14. Basket 2 Example

Suppose:

- CROISSANTS wall_mid = 100
- JAMS wall_mid = 50

Then Basket 2 synthetic value is:

```text
4*100 + 2*50 = 500
```

If PICNIC_BASKET2 is trading at 540, the basket is rich.
If it is trading at 460, the basket is cheap.

Notice that DJEMBES does not appear at all.
That is why Basket 2 is cleaner and easier to isolate.

---

# PART 5: SUMMARY

---

## 15. What You Should Remember

| Product | Main role |
|---------|-----------|
| CROISSANTS | Shared ingredient, plus its own signal source |
| JAMS | Shared ingredient for both baskets |
| DJEMBES | Basket 1 only ingredient |

And the key relationship is:

```text
Basket price = basket factor x constituent fair values + premium
```

If you know the constituent prices, you can estimate the basket.
If you know the basket position, you can choose the right hedge.

That is the full practical value of the three ingredients.

---

## 16. Next Step

If you can explain why Basket 1 includes DJEMBES and Basket 2 does not, you understand the product structure well enough to start coding.
If you can also explain why CROISSANTS is special, you understand the trading logic behind the Frankfurt Hedgehogs approach.

---

*Based on the Round 1 Resin teaching style and the Frankfurt Hedgehogs basket and hedge logic.*
