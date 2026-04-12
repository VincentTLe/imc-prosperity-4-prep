# Project Structure

This repo is organized around a few hard constraints and a few soft conventions.

## Files That Stay At The Root

- `datamodel.py`
- `backtester.py`
- `visualizer.py`
- `bone_visualizer.py`
- `project_paths.py`

These are root-level on purpose because the local tools import each other directly and some older scripts assume this layout.

## Active Development Areas

- `My_Bots/`: working bots
- `Lessons/`: teaching examples
- `Research/`: notebooks and exploration
- `Docs/`: instructions, notes, and competition research
- `scripts/`: repeatable command-line entrypoints

## Archived Or Local-Only Areas

- `My_Bots/archive/`: older bot snapshots
- `Jmerle-Backtester/`: large local mirror of the public backtester
- `Reference/`: large local mirror of public reference repos
- `data/[run-id]/`: local exported runs and scratch artifacts

These stay local unless there is a strong reason to publish them.

## Git Scope

The intended GitHub version of this repo should focus on:

- runnable code
- small tutorial data
- docs
- lessons
- active bots

It should avoid:

- large vendored reference repos
- generated logs
- downloaded zip archives
- one-off local helper scripts
