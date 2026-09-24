# Derivations & Notes

Handwritten notes from working through this project, day by day. Photos of the original page are paired with a typed version below each one.

---

## Day 1 — Finance basics

![Day 1 notes](notes/day1_finance_basics.png)

Some terms commonly used in this project:

1. **Stock / ticker** — Small ownership in a company → stock. A "ticker" is the short code for a company (e.g. AAPL = Apple, JPM = JPMorgan, etc.)
2. **Buying** — We pay a cash amount to acquire shares, betting the price goes up later.
3. **Selling** — We convert shares back into cash. Sell above what you paid → profit. Selling below what you paid → loss.
4. **Cash vs. Position** — Cash is uninvested money sitting in your account. A position is how many shares of a specific stock you currently hold.
5. **Commission** — Fee the broker charges per trade.
6. **OHLCV** — Open / High / Low / Close / Volume — the day's price summary.
7. **Equity curve** — Cash + value of everything held, plotted over time. This is the main chart used to judge whether a strategy actually worked or not.
8. **Backtesting** — Simulating how a strategy would have performed on past data, before risking real money on it.

---

## Day 2 — Portfolio buy/sell calculation

![Day 2 notes](notes/day2_portfolio_calc.png)

Worked through the exact numbers used to test the `Portfolio` class, starting from $100,000 cash:

**Buying** 10 AAPL shares @ $125.07, with $1 commission:

$100,000 − (10 × $125.07 + $1) = $98,748.30

**Selling** those same 10 AAPL shares later @ $180, with $1 commission:

$98,748.30 + (10 × $180 − $1) = $100,547.30

This matched the `Portfolio.update_on_fill()` output exactly when tested in `main.py`, confirming the cash/position math is correct.


## Day 4 — The event loop

![Day 4 notes](notes/day_4_event_loop.jpg)

For each day in price data:

1. Look at the day's price.
2. Ask the strategy: "Given what you know so far, do you want to buy, sell, or do nothing?"
3. If it wants to trade, create an order and hand it to the broker.
4. Broker checks feasibility and updates the portfolio if the trade goes through.
5. Record the portfolio's total value for that day — this running list of daily values will be our equity curve.

This is the design that became `engine/backtester.py` — implemented directly from this outline, one step per line above mapping to one part of the loop.

## Day 6 — SMA crossover strategy

![Day 6 notes part 1](notes/day6_1_sma_concept.jpg)

**Moving average (SMA):** instead of looking at a single day's closing price, average the last N days. A 20-day SMA on any given day = average of that day's close and the previous 19. Smooths out daily noise and shows the underlying trend.

**Crossover idea:** track 2 moving averages of different lengths — a fast one (e.g. 20-day) and a slow one (e.g. 50-day).
- Fast average crosses above slow average → recent prices rising faster than the longer-term trend → buy signal.
- Fast average crosses below slow average → recent momentum weakening relative to the trend → sell signal.

Called a "golden cross" (bullish) / "death cross" (bearish) when using 50-day and 200-day averages specifically.

**Why it's not guaranteed to work:** moving averages are lagging indicators — they only tell us about a trend after it's already partway underway. In a choppy, sideways market, this strategy can generate a lot of false signals (buy, then immediately get a sell signal a few days later, losing a bit to commission each time).

![Day 6 notes part 2](notes/day6_2_sma_calc.jpg)

Worked a small example with 3-day and 5-day windows (instead of 20/50) to compute by hand:

| Day | Price |
|---|---|
| 1 | 100 |
| 2 | 102 |
| 3 | 101 |
| 4 | 105 |
| 5 | 108 |
| 6 | 110 |
| 7 | 107 |
| 8 | 104 |

3-day SMA starts from Day 3 (Days 1–2 have no value yet): 101.0, 102.7, 104.7, 107.7, 108.3, 107.0

5-day SMA starts from Day 5: 103.2, 105.2, 106.2, 106.8

![Day 6 notes part 3](notes/day6_3_crossover_code.jpg)

Comparing the two each day:
- Day 5: 3-day (104.7) > 5-day (103.2) — fast already above slow
- Day 6: 3-day (107.7) > 5-day (105.2) — still above
- Day 7: 3-day (108.3) > 5-day (106.2) — still above
- Day 8: 3-day (107.0) > 5-day (106.8) — still above, but gap shrinking

If this continued and the 3-day dropped below the 5-day on a later day, that exact crossing point is what triggers a sell signal.

**Code design notes:**
1. The event loop originally only handled today's single price, but computing an SMA needs price history.
2. Fix: compute indicators upfront, not inside the loop — use pandas `.rolling(window).mean()` to compute the moving average for the entire column at once.
3. Updated 3 files: `backtester.py` (to precompute indicators and pass the full row), `buy_and_hold.py` (to match the new signature), and the new `sma_crossover.py`.
4. `df["Close"].rolling(3).mean()` computes the SMA for each row — for Day 1–2 it gives `NaN` since there isn't enough history yet, for Day 3 onward it gives a real value.



## Day 7 — RSI mean-reversion

![Day 7 notes part 1](notes/day7_1_rsi_concept.jpg)

**Concept:** RSI (Relative Strength Index) measures whether a stock is moving up or down too fast recently, on a 0–100 scale. Unlike SMA (which follows trends), RSI is a mean-reversion strategy — betting that after a big move, price tends to snap back toward its average rather than keep going.

**Calculation, conceptually:** over the last N days (say 14), look at the days that closed up vs. down. Average the size of the up-moves and the down-moves separately. RSI compares these two averages and converts the result into a 0–100 score.

**RSI indicators:**
- RSI near 100: price has been rising almost every day recently, very little pullback — considered "overbought," might be due for a pullback.
- RSI near 0: price has been falling almost every day recently — considered "oversold," might be due to bounce.
- RSI near 50: roughly balanced up/down days.

Rule used: RSI below 30 → buy signal (oversold, expect a bounce). RSI above 70 → sell signal (overbought, expect a pullback).

![Day 7 notes part 2](notes/day7_2_rsi_vs_sma_table.jpg)

**Why this is different from SMA crossover:** SMA crossover assumes "the trend will continue" (momentum). RSI assumes "this move has gone too far, too fast, and will reverse" (mean reversion).

Worked a 5-day window example:

| Day | Price | Daily Change |
|---|---|---|
| 1 | 100 | — |
| 2 | 102 | +2 |
| 3 | 101 | −1 |
| 4 | 104 | +3 |
| 5 | 103 | −1 |
| 6 | 107 | +4 |

Split changes into gain and loss (losses recorded as positive magnitudes, separately from gains):

| Day | Gain | Loss |
|---|---|---|
| 2 | 2 | 0 |
| 3 | 0 | 1 |
| 4 | 3 | 0 |
| 5 | 0 | 1 |
| 6 | 4 | 0 |

![Day 7 notes part 3](notes/day7_3_rsi_calc.jpg)

**Average gain and average loss over the period:**

Avg gain = (2+0+3+0+4)/5 = 1.8 = AG
Avg loss = (0+1+0+1+0)/5 = 0.4 = AL

**RS (Relative Strength)** = AG / AL = 1.8 / 0.4 = 4.5 — "on average, up-days are bigger by 4.5x than the down-days."

**RSI** = 100 − 100/(1 + RS) = 100 − 100/5.5 ≈ **81.82**

RSI ≈ 81.82 is above the 70 "overbought" threshold → there were more gains (4 of 5 days), and gains were bigger than losses.

**Edge case:** if there were zero losses at all, RS = AG/0 → ∞, and RSI = 100 − 100/(1+∞) = 100. This represents a pure uptrend with no down-days at all — the formula naturally bounds itself between 0 and 100 regardless of the actual size of price changes, which is what makes it comparable across different stocks and time periods.

This maps directly to `strategies/rsi_strategy.py`: `avg_gain`/`avg_loss` are the AG/AL from this table, computed with `.rolling(period).mean()` instead of by hand, and `Buy_Signal`/`Sell_Signal` implement the 30/70 threshold rule above.



## Day 8 — Momentum breakout

![Day 8 notes part 1](notes/day8_1_momentum_concept.jpg)

**Core idea:**
1. Looks for stocks pushing to new extremes and bets that breaking out of a recent range signals the start of a genuinely new move.
2. Track the highest closing price (Close) over the last N days (a "rolling high"). If today's close breaks above that rolling high, it means price just did something it hasn't done in the last N days — that's the breakout signal to buy.
3. Symmetrically, if price breaks below the rolling N-day low, that's a breakdown signal to exit.
4. This strategy is sharper and more immediate than SMA crossover. This makes it react faster, but also prone to false breakouts (price changes for a day or two only).

**Example:**

| Day | Price |
|---|---|
| 1 | 100 |
| 2 | 102 |
| 3 | 99 |
| 4 | 103 |
| 5 | 101 |
| 6 | 104 |
| 7 | 102 |
| 8 | 105 |
| 9 | 110 |

![Day 8 notes part 2](notes/day8_2_shift_fix.jpg)

The 5-day rolling high as of Day 8 looks at Days 4–8: (103, 101, 104, 102, 105) → highest = 105.

Day 9's close is 110, which is above 105 → breakout signal: buy.

We didn't use Days (5–9), only Days (4–8). If we included Day 9 for the "5-day high as of Day 9," it would already include 110 — meaning it would just equal 110, and price could technically never be "above" a high that includes itself.

Then, using `.rolling(5).max()` will fail, as by default it includes the current row in its own window, so comparing today's price to today's own rolling max would (at best) always be a tie, never a genuine breakout.

**Fix:** we need to compare today's price against the rolling high of the previous N days only — shifting the rolling calculation back by one day. Same as `.shift(1)` in SMA crossover, just applied to rolling min/max instead of rolling mean.

This maps directly to `strategies/momentum_breakout.py`: `df["Close"].shift(1).rolling(window).max()` implements exactly this fix.



## Day 9 — Transaction costs (slippage)

![Day 9 notes part 1](notes/day9_1_slippage_concept.jpg)

We already have commission (a flat $1 fee per trade). We are missing slippage.

**What is slippage?** In trading, the price we always see isn't the price we always get. Between deciding to trade and the order actually executing, the price can move — especially because our own order competes with other buyers/sellers. If we want to buy, we are usually buying more (slightly) than the last quoted price (other buyers are ahead of us, or the price ticks up as our order gets filled). If we are selling, we usually get slightly less. This gap is called slippage.

**Simple example:** 0.1% slippage means: on a BUY, our actual fill price is 0.1% higher than the day's close; on a SELL, 0.1% lower. It is not perfectly realistic (real slippage depends on order size, liquidity, volatility), but easier for simplification.

**Numbers:** buying 10 shares of a $200 stock, with 0.1% slippage.
- Without slippage, total buying cost: $200 × 10 = $2,000.00
- With 0.1% slippage, total cost: [$200 × (1 + 0.001)] × 10 = $2,002.00
- We paid $2 more than the quoted price due to slippage.

![Day 9 notes part 2](notes/day9_2_slippage_calc.jpg)

Later, on selling the stocks (10 shares) at $210:
- Without slippage: $2,100.00
- With slippage: [$210 × (1 − 0.001)] × 10 = $2,097.90
- We got $2.10 less than the quoted price.

**Total slippage cost on this round trip:** $(2 + 2.10) = $4.10 — on top of whatever commissions are charged.

This maps directly to `engine/broker.py`: `_apply_slippage()` implements exactly this — multiplying the quoted price by `(1 + slippage_pct)` on a BUY and `(1 - slippage_pct)` on a SELL.