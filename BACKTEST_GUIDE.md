# Backtesting Guide

## Install

```powershell
python -m pip install -r requirements.txt
```

## Fastest Way To Run

Use the stable wrapper script:

```powershell
python scripts/run_backtest.py --bot My_Bots/temp_bot.py --round 0 --day -1 --data-root data
```

That script:

- resolves the repo-relative bot path
- auto-detects a usable data root
- runs one round/day through `backtester.py`

## Direct Backtester Usage

You can still call the engine directly:

```powershell
python backtester.py My_Bots/temp_bot.py 0 -1 --data-root data
```

If auto-detection is not enough, point it at a specific dataset:

```powershell
python backtester.py My_Bots/temp_bot.py 1 0 --data-root data
```

## Visual Review

After a run, inspect `backtest_results.json` with the Streamlit dashboard:

```powershell
streamlit run visualizer.py
```

The visualizer now discovers the project root and data root automatically instead of depending on an old absolute path.

## Expected Outputs

- `backtest_results.json`: structured result for the dashboard
- console summary from `backtester.py`
- optional bot `print()` output inside the visualizer log panel

## Recommended Workflow

1. Edit `My_Bots/temp_bot.py`
2. Run `python scripts/run_backtest.py --bot My_Bots/temp_bot.py --round 1 --day 0`
3. Open `streamlit run visualizer.py`
4. Compare fills, PnL, and position usage
5. Promote stable ideas into `My_Bots/my_first_bot.py` or a cleaner named bot
