from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def _looks_like_data_root(path: Path) -> bool:
    return _price_file_count(path) > 0


def _price_file_count(path: Path) -> int:
    if not path.is_dir():
        return 0

    return sum(1 for candidate in path.rglob("prices_round_*_day_*.csv") if candidate.is_file())


def data_root_candidates() -> list[Path]:
    return [
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "Jmerle-Backtester" / "prosperity3bt" / "resources",
        PROJECT_ROOT / "Reference" / "CarterT27" / "data",
    ]


def find_data_root() -> Path | None:
    ranked_candidates = [
        (candidate, _price_file_count(candidate))
        for candidate in data_root_candidates()
    ]
    ranked_candidates = [item for item in ranked_candidates if item[1] > 0]
    if not ranked_candidates:
        return None
    ranked_candidates.sort(key=lambda item: item[1], reverse=True)
    return ranked_candidates[0][0]


def default_bot_path() -> Path:
    active_bot = PROJECT_ROOT / "My_Bots" / "temp_bot.py"
    if active_bot.is_file():
        return active_bot
    return PROJECT_ROOT / "My_Bots" / "my_first_bot.py"
