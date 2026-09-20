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