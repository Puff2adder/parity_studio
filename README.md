# Parity and Black Scholes learning studio version 1

This is the chapter's working studio, with an orientation and five modules. Public practice uses identical textbook inputs; the assessed homework questions and solutions are not included. All examples are hypothetical.

## Start locally

Double-click `start_studio.cmd`, or from this folder run:

```powershell
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8512 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8512. The pinned versions in requirements.txt match the tested installed environment. No installation was needed here. Keep the terminal running while using the studio; Ctrl+C stops it.

Module links use `?page=parity`, `?page=dividends`, `?page=forwards`, `?page=pricing`, or `?page=practice`. Add `&example=pbs-bs-fx` to the pricing route to open the currency preset. Example IDs and page IDs are stable and independent of chapter numbers. The manifest at ../../../examples/studio_links.json records unpublished public URLs as null.

## Teaching design

Allow five minutes for orientation, then 15 for replication, 20 for dividends, 15 for forwards, 25 for pricing and hedge decisions, and 10 for the mixed review. Additional application experiments and the put-maturity counterexample are optional. Students can directly navigate, request hints, reveal solutions, retry questions, and reset without correctness or writing gates.

Module 4 has an application dropdown: volatility/maturity, price versus intrinsic value and bounds, and the textbook euro-purchase comparison. Module 5 has 30 questions, six per objective group; mixed review draws two per group. Every choice has an explanation, with hints and retries. No grades or identities are collected, and no homework instructor files are read.

## Sources and maintenance

Question prose and distractors: question_bank.py. Financial engines and bounded arithmetic calculator: finance.py. Interface: app.py. Textbook presets: chapter_parity_black_scholes/examples/textbook_examples_v1.json. Shared layout: shared/studio_theme/parity_theme_v1.py. Calculations use full precision; the interface reports six decimals. Premiums are per unit except explicitly labeled total hedge costs.

The formula calculator supports arithmetic expressions in named inputs; it does not solve equations or execute Python. Supported functions are exp, sqrt, ln/log, N, abs, min, and max. It clears stale output after input changes. The forward strike is solved directly from parity.

Cash-dividend parity is an exact cash-flow relation under the assumptions. The cash-dividend Black–Scholes shortcut is qualified as an approximation under fixed dividend jumps. Yield and currency pricing use the standard constant-yield model. Continuous reinvestment, unrestricted shorting, and consistent riskless funding are assumptions, not promises about executable market trades.

The download contains the active experiment inputs and main-module calculated results. Application comparison tables are visible for manual recording; they are not appended to this download. Add your own interpretation. Session state is temporary.

## Publication

This studio has not been publicly deployed or promoted to final. Only files explicitly listed in public_files.json may enter a future deployment package. The allowlist also maps shared theme and textbook examples into that package. Do not publish the workspace, instructor manuals, originals, or validation files. Public hosting and classroom concurrency have not been tested.


## Revision 1.1 — stock-price comparison module

Module 5 compares three maturities or three volatilities, calls first then puts, with exact parity lower bounds and optional upper bounds. No dividends, a dated cash dividend, or continuous yield may be selected. The default horizontal axis is stock price at a future valuation date, with T interpreted as remaining maturity; current valuation is also selectable. A separate expiration payoff panel uses S_T. Cash-dividend model values are qualified as approximations. The core pricing allocation is now 15 minutes plus 10 minutes for comparisons; Module 6 retains the final multiple-choice practice.
