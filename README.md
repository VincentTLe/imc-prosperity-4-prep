# IMC Prosperity Workspace

This repository is organized as a practical local workspace for IMC Prosperity bot development, backtesting, visualization, and notes.

It keeps the engine files at the repository root because the local tooling imports them directly. Everything else is grouped around a simple workflow: edit a bot, run a backtest, inspect the result, and keep research close to the code.

## Quick Start

1. Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run a backtest with the current active bot:

```powershell
python scripts/run_backtest.py --bot My_Bots/temp_bot.py --round 0 --day -1 --data-root data
```

3. Open the Streamlit visualizer:

```powershell
streamlit run visualizer.py
```

## Layout

```text
Prosperity/
|-- backtester.py              # Local simulation runner
|-- datamodel.py               # IMC datamodel types
|-- visualizer.py              # Streamlit dashboard
|-- bone_visualizer.py         # Simpler HTML visualizer
|-- project_paths.py           # Shared path discovery helpers
|-- requirements.txt
|-- BACKTEST_GUIDE.md
|-- Docs/                      # Guides, structure notes, web research notes
|-- Lessons/                   # Tutorial-style lesson bots
|-- My_Bots/                   # Active bots and archived snapshots
|-- Research/                  # Notebooks and exploratory analysis
|-- Visualizations/            # Static HTML visualizers
|-- data/                      # Small local data and tutorial csvs
`-- scripts/                   # Stable entrypoints for common tasks
```

## Working Areas

- `My_Bots/temp_bot.py`: current scratch bot.
- `My_Bots/my_first_bot.py`: cleaner starting point.
- `My_Bots/archive/`: older snapshots moved out of the way but still kept locally.
- `Lessons/README.md`: catalog of all lesson bots added by round.
- `Lessons/Round1/Lesson1_Resin.py`: original commented teaching example.
- `Research/Tutorial_Analysis.ipynb`: notebook exploration.

## Local-Only Assets

Large third-party mirrors and heavy reference datasets are intentionally gitignored:

- `Jmerle-Backtester/`
- `Reference/`
- downloaded zip files and numeric run dumps under `data/`
- generated logs and `backtest_results.json`

That keeps the GitHub version lightweight while still letting you keep large local study material beside the repo.

## Docs

- `BACKTEST_GUIDE.md`: install and run commands.
- `Docs/PROJECT_STRUCTURE.md`: what belongs where.
- `Docs/IMC_PROSPERITY_WEB_NOTES.md`: notes gathered from web research on April 12, 2026.
- `Docs/LESSON_CATALOG.md`: index of the round-by-round learning guides.
- `Docs/General_EN.md` / `Docs/General_VI.md`: longer learning notes.
- `Docs/Round1_Resin_EN.md` / `Docs/Round1_Resin_VI.md`: round 1 Resin material.
- `Docs/Round1_Kelp_EN.md` / `Docs/Round1_SquidInk_EN.md`: extra Round 1 product guides.
- `Docs/Round2_ETF_EN.md` / `Docs/Round2_Constituents_EN.md`: ETF and constituent guides.
- `Docs/Round3_Options_EN.md`: options round guide.
- `Docs/Round4_Macarons_EN.md`: conversions / location arbitrage guide.
- `Docs/Round5_TraderIds_EN.md`: trader-ID / Olivia guide.

## Notes From Web Research

As of April 12, 2026, the official landing page for the competition is `https://prosperity.imc.com/`, and public search results referenced `IMC Prosperity 04` / `Coming Soon`. Public Prosperity 3 writeups and the community wiki remain the most detailed open sources for mechanics, round structure, and strategy ideas. The reference note is collected in `Docs/IMC_PROSPERITY_WEB_NOTES.md`.
