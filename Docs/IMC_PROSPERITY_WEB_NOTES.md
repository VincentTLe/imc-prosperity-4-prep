# IMC Prosperity Web Notes

Research date: April 12, 2026

This note captures the useful external context gathered during web search before reorganizing the repo.

## Official Signals

- Official site: <https://prosperity.imc.com/>
- Search results on April 12, 2026 referenced `IMC Prosperity 04` and `Coming Soon`.
- Search results for the signup page described the event as an annual 15-day algorithmic trading challenge.

## Public Open References

- Prosperity community wiki:
  <https://imc-prosperity.notion.site/Prosperity-3-Wiki-19ee8453a09380529731c4e6fb697ea4>
- Frankfurt Hedgehogs Prosperity 3 writeup:
  <https://github.com/TimoDiehm/imc-prosperity-3>
- Alpha Animals / CarterT27 Prosperity 3 writeup:
  <https://github.com/cartert27/imc-prosperity-3>

## Practical Takeaways For This Repo

- Round 1 public references consistently start with three products:
  `RAINFOREST_RESIN`, `KELP`, and `SQUID_INK`.
- The best public writeups combine three things:
  local backtesting, custom visualization, and notebook-style research.
- Public winner writeups emphasize that early-round edge often comes from:
  fair-value estimation, inventory control, and careful reading of the matching environment.
- Reference repos are useful to study, but vendoring full datasets locally makes the repo much heavier than it needs to be for GitHub.

## How This Affects The Repo Layout

- Keep the runnable local workflow in git.
- Keep large mirrored references local and gitignored.
- Keep links to the official site, wiki, and public writeups in docs so the repo is still easy to navigate later.
