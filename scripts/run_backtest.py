from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backtester import ProsperityBacktester, discover_data_files
from project_paths import PROJECT_ROOT, default_bot_path, find_data_root


def resolve_bot_path(bot_arg: str | None) -> Path:
    if not bot_arg:
        return default_bot_path()

    bot_path = Path(bot_arg)
    if bot_path.is_absolute():
        return bot_path

    return PROJECT_ROOT / bot_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one Prosperity backtest from a stable project entrypoint.")
    parser.add_argument("--bot", default=None, help="Bot path relative to repo root. Defaults to My_Bots/temp_bot.py.")
    parser.add_argument("--round", type=int, default=1, dest="round_num", help="Round number to run.")
    parser.add_argument("--day", type=int, default=0, help="Day number to run.")
    parser.add_argument("--data-root", default=None, help="Optional data root relative to repo root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    bot_path = resolve_bot_path(args.bot)
    if not bot_path.is_file():
        print(f"ERROR: Bot file not found: {bot_path}")
        return 1

    if args.data_root:
        raw_data_root = Path(args.data_root)
        data_root = raw_data_root if raw_data_root.is_absolute() else PROJECT_ROOT / raw_data_root
    else:
        data_root = find_data_root()
    if data_root is None:
        print("ERROR: Could not find a usable data root.")
        return 1

    available = discover_data_files(str(data_root))
    key = (args.round_num, args.day)
    if key not in available:
        available_keys = ", ".join(f"r{round_num}d{day_num}" for round_num, day_num in sorted(available))
        print(f"ERROR: No data for round {args.round_num} day {args.day}.")
        print(f"Available: {available_keys}")
        return 1

    files = available[key]
    backtester = ProsperityBacktester(
        bot_file_path=str(bot_path),
        prices_path=files["prices"],
        trades_path=files["trades"],
        round_num=args.round_num,
        day_num=args.day,
    )
    backtester.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
