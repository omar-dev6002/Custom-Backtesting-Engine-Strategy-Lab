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


