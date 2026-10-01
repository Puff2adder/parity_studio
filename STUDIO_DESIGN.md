# Five module learning studio

Audience: Executive MBA, also accessible to MBA students and undergraduate seniors. Prerequisites are European option payoffs and present value. One studio contains orientation plus five stable modules. Core route: orientation 5 minutes; replication 15; dividends 20; forwards 15; pricing 25; review 10. Classroom timing is a planning estimate.

| Module | Observable outcome | Guided textbook examples | Applications |
|---|---|---|---|
| Parity | Construct a synthetic put, verify equivalent terminal packages, diagnose a quote | S₀ 61, K 65, call 4.12, three months, r 2.6% | Spot at-the-money premium gap; reverse the quote discrepancy |
| Dividends | Account for dated dividends and reinvesting units in arbitrage | S₀ 55 with $2 dividend in one month; index 100 with 5% yield | Vary amounts and dates; compare policies; use two cash dividends |
| Forwards | Select K so c₀ − p₀ = 0 and explain the resulting commitment | S₀ 100, r 5%, T 1; no dividend, $4 dividend at six months, or 4% yield | Strike/net-premium graph; terminal payoff and financed-profit comparison |
| Pricing | Apply the appropriate model, check bounds, and select a hedge | Stock 160; cash-dividend example; index 300; FX 1.10; put-maturity extension | Volatility/maturity table and plot; intrinsic versus bounds plot; euro purchase hedge |
| Practice | Explain the identities, assumptions, and business consequences | 30 public practice items with misconception-based distractors | Topic practice, balanced mixed review, full explanations, hints, retry |

Modules 1–4 present objectives, matching textbook problem facts, an optional attempt, two hints, full walkthrough on request, application experiments, and a synthesis with limitations. Module 1 additionally provides an editable payoff table. Full navigation remains available. Inputs change calculations immediately and invalidate old feedback. Resets restore the complete selected textbook example.

The portfolio selector in Module 4 provides three decision-focused investigations. The currency comparison deliberately uses the textbook's public 100,000-euro case, not the assessed 150,000-euro homework case. The question bank contains no assessed answers. Six questions cover each of replication, dividends, forwards, pricing, and bounds/decisions; mixed review samples two from each group.

Stable IDs and benchmark inputs live in the chapter examples JSON. Financial functions are independent of the interface; layout is in the shared theme. The arithmetic calculator evaluates a bounded expression tree using named inputs, without eval or arbitrary Python execution. It does not solve arbitrary symbolic equations. A specific forward-strike button solves the parity condition.

This is a local working revision. No public deployment, classroom concurrency test, or promotion to final has occurred. A seven-file allowlist defines the future deployment boundary. No identity collection, grade transmission, or hidden assessed answers are implemented.


## Revision 1.1 — stock-price comparison module

Module 5 compares three maturities or three volatilities, calls first then puts, with exact parity lower bounds and optional upper bounds. No dividends, a dated cash dividend, or continuous yield may be selected. The default horizontal axis is stock price at a future valuation date, with T interpreted as remaining maturity; current valuation is also selectable. A separate expiration payoff panel uses S_T. Cash-dividend model values are qualified as approximations. The core pricing allocation is now 15 minutes plus 10 minutes for comparisons; Module 6 retains the final multiple-choice practice.
