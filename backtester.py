# -*- coding: utf-8 -*-
"""
=============================================================================
PROSPERITY 4 — BACKTESTER ENGINE
=============================================================================
Simulates the IMC Prosperity trading environment locally.
Features:
  - Two-phase order matching (order book depth + market trades)
  - Engine-enforced position limits (same as real platform)
  - Stdout capture (sandbox logs)
  - traderData persistence between timesteps
  - own_trades / market_trades population
  - Expanded JSON output for the Streamlit visualizer
=============================================================================
"""

import csv
import sys
import os
import re
import json
import argparse
import importlib.util
from io import StringIO
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from datamodel import (
    TradingState, OrderDepth, Order, Trade, Listing, Observation,
)
from project_paths import default_bot_path, find_data_root

# =============================================================================
# POSITION LIMITS — same as the real IMC platform
# =============================================================================
POSITION_LIMITS: Dict[str, int] = {
    "RAINFOREST_RESIN": 50,
    "KELP": 50,
    "SQUID_INK": 50,
    "CROISSANTS": 250,
    "JAMS": 350,
    "DJEMBES": 60,
    "PICNIC_BASKET1": 60,
    "PICNIC_BASKET2": 100,
    "VOLCANIC_ROCK": 400,
    "VOLCANIC_ROCK_VOUCHER_9500": 200,
    "VOLCANIC_ROCK_VOUCHER_9750": 200,
    "VOLCANIC_ROCK_VOUCHER_10000": 200,
    "VOLCANIC_ROCK_VOUCHER_10250": 200,
    "VOLCANIC_ROCK_VOUCHER_10500": 200,
    "MAGNIFICENT_MACARONS": 75,
}

DEFAULT_LIMIT = 50  # fallback for unknown products


# =============================================================================
# DATA STRUCTURES
# =============================================================================
@dataclass
class PriceRow:
    day: int
    timestamp: int
    product: str
    bid_prices: List[int]
    bid_volumes: List[int]
    ask_prices: List[int]
    ask_volumes: List[int]
    mid_price: float


@dataclass
class MarketTrade:
    """Wraps a Trade with remaining fill quantities for matching."""
    trade: Trade
    buy_quantity: int
    sell_quantity: int


# =============================================================================
# DATA LOADING
# =============================================================================
def discover_data_files(data_root: str) -> Dict[tuple, dict]:
    """Scan data_root for available round/day CSV files.

    Returns {(round_num, day_num): {"prices": path, "trades": path_or_None}}
    """
    result = {}
    if not os.path.isdir(data_root):
        return result

    for folder_path, _, filenames in os.walk(data_root):
        for fname in filenames:
            m = re.match(r"prices_round_(\d+)_day_(-?\d+)\.csv", fname)
            if not m:
                continue
            round_num = int(m.group(1))
            day_num = int(m.group(2))
            key = (round_num, day_num)

            if key not in result:
                result[key] = {"prices": None, "trades": None}
            result[key]["prices"] = os.path.join(folder_path, fname)

            trades_fname = f"trades_round_{round_num}_day_{day_num}.csv"
            trades_path = os.path.join(folder_path, trades_fname)
            if os.path.isfile(trades_path):
                result[key]["trades"] = trades_path

    return result


def _parse_int_levels(row: dict, prefix: str, max_levels: int = 3):
    """Extract up to max_levels of price/volume pairs from a CSV row."""
    prices, volumes = [], []
    for i in range(1, max_levels + 1):
        p = row.get(f"{prefix}_price_{i}", "")
        v = row.get(f"{prefix}_volume_{i}", "")
        if p == "" or v == "":
            break
        prices.append(int(p))
        volumes.append(int(v))
    return prices, volumes


def load_prices(prices_path: str) -> tuple:
    """Parse prices CSV.

    Returns (timestamps_sorted, prices_dict, products_set)
      prices_dict = {timestamp: {product: PriceRow}}
    """
    prices: Dict[int, Dict[str, PriceRow]] = {}
    products = set()

    with open(prices_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            ts = int(row["timestamp"])
            product = row["product"]
            products.add(product)

            bid_prices, bid_volumes = _parse_int_levels(row, "bid")
            ask_prices, ask_volumes = _parse_int_levels(row, "ask")

            mid_str = row.get("mid_price", "")
            if mid_str and mid_str != "":
                mid_price = float(mid_str)
            elif bid_prices and ask_prices:
                mid_price = (bid_prices[0] + ask_prices[0]) / 2.0
            else:
                mid_price = 0.0

            if ts not in prices:
                prices[ts] = {}

            prices[ts][product] = PriceRow(
                day=int(row.get("day", 0)),
                timestamp=ts,
                product=product,
                bid_prices=bid_prices,
                bid_volumes=bid_volumes,
                ask_prices=ask_prices,
                ask_volumes=ask_volumes,
                mid_price=mid_price,
            )

    timestamps = sorted(prices.keys())
    return timestamps, prices, sorted(products)


def load_trades(trades_path: str) -> Dict[int, Dict[str, List[Trade]]]:
    """Parse trades CSV.

    Returns {timestamp: {product: [Trade(...)]}}
    """
    trades: Dict[int, Dict[str, List[Trade]]] = {}

    with open(trades_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            ts = int(row["timestamp"])
            symbol = row["symbol"]
            price = int(float(row["price"]))
            quantity = int(row["quantity"])
            buyer = row.get("buyer", "")
            seller = row.get("seller", "")

            if ts not in trades:
                trades[ts] = {}
            if symbol not in trades[ts]:
                trades[ts][symbol] = []

            trades[ts][symbol].append(
                Trade(symbol, price, quantity, buyer, seller, ts)
            )

    return trades


# =============================================================================
# ENGINE LOGIC
# =============================================================================
def prepare_state(state: TradingState, prices_at_ts: Dict[str, PriceRow],
                  products: List[str]) -> None:
    """Build order_depths and listings from price data for this timestep."""
    state.order_depths = {}
    state.listings = {}

    for product in products:
        row = prices_at_ts.get(product)
        if row is None:
            continue

        depth = OrderDepth()
        for p, v in zip(row.bid_prices, row.bid_volumes):
            depth.buy_orders[p] = v
        for p, v in zip(row.ask_prices, row.ask_volumes):
            depth.sell_orders[p] = -v  # sell volumes are negative

        state.order_depths[product] = depth
        state.listings[product] = Listing(product, product, 1)


def enforce_limits(
    products: List[str],
    orders: Dict[str, List[Order]],
    positions: Dict[str, int],
) -> List[str]:
    """Check position limits BEFORE matching. Cancel all orders for a product
    if the proposed orders would violate its limit. Returns warning messages."""
    warnings = []
    for product in products:
        product_orders = orders.get(product, [])
        if not product_orders:
            continue

        pos = positions.get(product, 0)
        limit = POSITION_LIMITS.get(product, DEFAULT_LIMIT)

        total_long = sum(o.quantity for o in product_orders if o.quantity > 0)
        total_short = sum(abs(o.quantity) for o in product_orders if o.quantity < 0)

        if pos + total_long > limit or pos - total_short < -limit:
            msg = f"Orders for {product} exceeded limit of {limit} — all cancelled"
            warnings.append(msg)
            orders.pop(product, None)

    return warnings


def type_check_orders(orders: dict) -> None:
    """Validate order types — same checks as the real platform."""
    for key, value in orders.items():
        if not isinstance(key, str):
            raise ValueError(f"Orders key '{key}' is {type(key)}, expected str")
        for order in value:
            if not isinstance(order.price, int):
                raise ValueError(f"Order price {order.price} is {type(order.price)}, expected int")
            if not isinstance(order.quantity, int):
                raise ValueError(f"Order quantity {order.quantity} is {type(order.quantity)}, expected int")


# -----------------------------------------------------------------------------
# TWO-PHASE ORDER MATCHING  (ported from Jmerle's runner.py)
# -----------------------------------------------------------------------------
def match_buy_order(
    state: TradingState,
    order: Order,
    market_trades: List[MarketTrade],
    profit_loss: Dict[str, float],
) -> List[Trade]:
    """Phase 1: match buy order against order book sell levels (ascending price).
    Phase 2: match remaining against historical market trades."""
    trades = []
    depth = state.order_depths[order.symbol]

    # Phase 1 — order book
    price_matches = sorted(p for p in depth.sell_orders if p <= order.price)
    for price in price_matches:
        volume = min(order.quantity, abs(depth.sell_orders[price]))

        trades.append(Trade(order.symbol, price, volume, "SUBMISSION", "", state.timestamp))
        state.position[order.symbol] = state.position.get(order.symbol, 0) + volume
        profit_loss[order.symbol] = profit_loss.get(order.symbol, 0.0) - price * volume

        depth.sell_orders[price] += volume
        if depth.sell_orders[price] == 0:
            del depth.sell_orders[price]

        order.quantity -= volume
        if order.quantity == 0:
            return trades

    # Phase 2 — market trades
    for mt in market_trades:
        if mt.sell_quantity == 0 or mt.trade.price > order.price:
            continue

        volume = min(order.quantity, mt.sell_quantity)
        trades.append(Trade(order.symbol, order.price, volume, "SUBMISSION", mt.trade.seller, state.timestamp))

        state.position[order.symbol] = state.position.get(order.symbol, 0) + volume
        profit_loss[order.symbol] = profit_loss.get(order.symbol, 0.0) - order.price * volume
        mt.sell_quantity -= volume

        order.quantity -= volume
        if order.quantity == 0:
            return trades

    return trades


def match_sell_order(
    state: TradingState,
    order: Order,
    market_trades: List[MarketTrade],
    profit_loss: Dict[str, float],
) -> List[Trade]:
    """Phase 1: match sell order against order book buy levels (descending price).
    Phase 2: match remaining against historical market trades."""
    trades = []
    depth = state.order_depths[order.symbol]

    # Phase 1 — order book
    price_matches = sorted((p for p in depth.buy_orders if p >= order.price), reverse=True)
    for price in price_matches:
        volume = min(abs(order.quantity), depth.buy_orders[price])

        trades.append(Trade(order.symbol, price, volume, "", "SUBMISSION", state.timestamp))
        state.position[order.symbol] = state.position.get(order.symbol, 0) - volume
        profit_loss[order.symbol] = profit_loss.get(order.symbol, 0.0) + price * volume

        depth.buy_orders[price] -= volume
        if depth.buy_orders[price] == 0:
            del depth.buy_orders[price]

        order.quantity += volume  # quantity is negative, so += moves towards 0
        if order.quantity == 0:
            return trades

    # Phase 2 — market trades
    for mt in market_trades:
        if mt.buy_quantity == 0 or mt.trade.price < order.price:
            continue

        volume = min(abs(order.quantity), mt.buy_quantity)
        trades.append(Trade(order.symbol, order.price, volume, mt.trade.buyer, "SUBMISSION", state.timestamp))

        state.position[order.symbol] = state.position.get(order.symbol, 0) - volume
        profit_loss[order.symbol] = profit_loss.get(order.symbol, 0.0) + order.price * volume
        mt.buy_quantity -= volume

        order.quantity += volume
        if order.quantity == 0:
            return trades

    return trades


def match_orders(
    state: TradingState,
    products: List[str],
    orders: Dict[str, List[Order]],
    trades_at_ts: Dict[str, List[Trade]],
    profit_loss: Dict[str, float],
) -> Dict[str, List[Trade]]:
    """Match all orders for all products. Returns dict of own_trades per product."""
    # Wrap historical market trades
    market_trades_map: Dict[str, List[MarketTrade]] = {}
    for product, trade_list in trades_at_ts.items():
        market_trades_map[product] = [
            MarketTrade(trade=t, buy_quantity=t.quantity, sell_quantity=t.quantity)
            for t in trade_list
        ]

    all_own_trades: Dict[str, List[Trade]] = {}

    for product in products:
        new_trades = []
        for order in orders.get(product, []):
            if order.quantity > 0:
                new_trades.extend(match_buy_order(
                    state, order, market_trades_map.get(product, []), profit_loss
                ))
            elif order.quantity < 0:
                new_trades.extend(match_sell_order(
                    state, order, market_trades_map.get(product, []), profit_loss
                ))

        if new_trades:
            state.own_trades[product] = new_trades
            all_own_trades[product] = new_trades

    # Populate state.market_trades with remaining (unmatched) market trades
    for product, mt_list in market_trades_map.items():
        for mt in mt_list:
            mt.trade.quantity = min(mt.buy_quantity, mt.sell_quantity)
        remaining = [mt.trade for mt in mt_list if mt.trade.quantity > 0]
        if remaining:
            state.market_trades[product] = remaining

    return all_own_trades


# =============================================================================
# BACKTESTER CLASS
# =============================================================================
class ProsperityBacktester:
    def __init__(self, bot_file_path: str, prices_path: str,
                 trades_path: Optional[str] = None,
                 round_num: int = 1, day_num: int = 0):
        self.bot_file_path = bot_file_path
        self.round_num = round_num
        self.day_num = day_num

        # Load data
        self.timestamps, self.prices, self.products = load_prices(prices_path)
        self.trades_data = load_trades(trades_path) if trades_path else {}

        # State tracking
        self.positions: Dict[str, int] = {}
        self.profit_loss: Dict[str, float] = {}
        for p in self.products:
            self.positions[p] = 0
            self.profit_loss[p] = 0.0

        # History for JSON export
        self.history = {
            "metadata": {
                "bot_file": bot_file_path,
                "round": round_num,
                "day": day_num,
                "position_limits": {
                    p: POSITION_LIMITS.get(p, DEFAULT_LIMIT)
                    for p in self.products
                },
            },
            "timestamps": [],
            "products": {
                p: {
                    "mid_price": [],
                    "pnl": [],
                    "position": [],
                    "best_bid": [],
                    "best_ask": [],
                    "bid_depth": [],
                    "ask_depth": [],
                    "trades": [],
                }
                for p in self.products
            },
            "sandbox_logs": {},
        }

        # Dynamic import of bot
        spec = importlib.util.spec_from_file_location("bot", self.bot_file_path)
        self.bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.bot_module)
        self.trader = self.bot_module.Trader()

    def run(self):
        print(f"Backtesting: {self.bot_file_path}")
        print(f"Data: round {self.round_num}, day {self.day_num}")
        print(f"Products: {', '.join(self.products)}")
        print(f"Timesteps: {len(self.timestamps)}")
        print("-" * 60)

        trader_data = ""
        state = TradingState(
            traderData=trader_data,
            timestamp=0,
            listings={},
            order_depths={},
            own_trades={},
            market_trades={},
            position=self.positions,
            observations=Observation({}, {}),
        )

        for ts in self.timestamps:
            self.history["timestamps"].append(ts)

            # Prepare state
            state.timestamp = ts
            state.traderData = trader_data
            state.position = self.positions.copy()

            prices_at_ts = self.prices[ts]
            prepare_state(state, prices_at_ts, self.products)

            # Capture stdout from trader.run()
            stdout_capture = StringIO()
            with redirect_stdout(stdout_capture):
                orders_dict, conversions, trader_data = self.trader.run(state)
            lambda_log = stdout_capture.getvalue().rstrip()

            # Store sandbox log
            self.history["sandbox_logs"][str(ts)] = lambda_log

            # Type-check orders
            try:
                type_check_orders(orders_dict)
            except ValueError as e:
                self.history["sandbox_logs"][str(ts)] += f"\nORDER ERROR: {e}"
                orders_dict = {}

            # Enforce position limits
            warnings = enforce_limits(self.products, orders_dict, state.position)
            if warnings:
                self.history["sandbox_logs"][str(ts)] += "\n" + "\n".join(warnings)

            # Match orders (two-phase)
            trades_at_ts = self.trades_data.get(ts, {})
            own_trades = match_orders(
                state, self.products, orders_dict, trades_at_ts, self.profit_loss
            )

            # Update positions from state
            self.positions = dict(state.position)

            # Record history per product
            for product in self.products:
                row = prices_at_ts.get(product)
                if row is None:
                    continue

                ph = self.history["products"][product]

                # Mid price
                ph["mid_price"].append(row.mid_price)

                # Best bid / ask
                depth = state.order_depths.get(product, OrderDepth())
                best_bid = max(depth.buy_orders.keys()) if depth.buy_orders else 0
                best_ask = min(depth.sell_orders.keys()) if depth.sell_orders else 0
                ph["best_bid"].append(best_bid)
                ph["best_ask"].append(best_ask)

                # Full depth snapshot
                bid_snap = {str(p): v for p, v in sorted(depth.buy_orders.items(), reverse=True)}
                ask_snap = {str(p): abs(v) for p, v in sorted(depth.sell_orders.items())}
                ph["bid_depth"].append(bid_snap)
                ph["ask_depth"].append(ask_snap)

                # Position
                pos = self.positions.get(product, 0)
                ph["position"].append(pos)

                # PnL = realized cash + unrealized (position × mid_price)
                pnl = self.profit_loss.get(product, 0.0) + pos * row.mid_price
                ph["pnl"].append(pnl)

                # Own trades at this timestep
                for t in own_trades.get(product, []):
                    trade_type = "BUY" if t.buyer == "SUBMISSION" else "SELL"
                    ph["trades"].append({
                        "timestamp": ts,
                        "type": trade_type,
                        "price": t.price,
                        "quantity": t.quantity,
                        "buyer": t.buyer or "",
                        "seller": t.seller or "",
                    })

        # Print summary
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        total_pnl = 0.0
        for product in self.products:
            pos = self.positions.get(product, 0)
            pnl_list = self.history["products"][product]["pnl"]
            final_pnl = pnl_list[-1] if pnl_list else 0.0
            total_pnl += final_pnl
            print(f"  {product:30s} | Position: {pos:+5d} | PnL: {final_pnl:+12,.1f}")
        print("-" * 60)
        print(f"  {'TOTAL':30s} |                | PnL: {total_pnl:+12,.1f}")
        print("=" * 60)

        # Export to JSON
        with open("backtest_results.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f)
        print("\n[+] Exported backtest_results.json")

        return self.history


# =============================================================================
# CLI INTERFACE
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Prosperity 4 Backtester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python backtester.py My_Bots/temp_bot.py 1 0\n"
               "  python backtester.py my_bot.py 1 0 --data-root path/to/data\n"
               "  python backtester.py my_bot.py 1 --print\n",
    )
    parser.add_argument("bot_file", help="Path to the bot Python file")
    parser.add_argument("round", type=int, help="Round number to run")
    parser.add_argument("day", type=int, nargs="?", default=None,
                        help="Day number (default: 0). Use negative for training days.")
    parser.add_argument("--data-root", default=None,
                        help="Path to data directory (auto-detected if omitted)")
    parser.add_argument("--print", dest="print_output", action="store_true",
                        help="Also print trader stdout to console")

    args = parser.parse_args()

    # Find data root
    resolved_data_root = args.data_root or find_data_root()
    data_root = str(resolved_data_root) if resolved_data_root is not None else None
    if data_root is None:
        print("ERROR: Could not find data directory. Use --data-root to specify.")
        sys.exit(1)

    # Discover available files
    available = discover_data_files(data_root)
    if not available:
        print(f"ERROR: No data files found in {data_root}")
        sys.exit(1)

    # Determine which days to run
    if args.day is not None:
        days_to_run = [(args.round, args.day)]
    else:
        days_to_run = sorted(k for k in available if k[0] == args.round)

    if not days_to_run:
        print(f"ERROR: No data for round {args.round}")
        avail_str = ", ".join(f"r{r}d{d}" for r, d in sorted(available))
        print(f"Available: {avail_str}")
        sys.exit(1)

    for round_num, day_num in days_to_run:
        key = (round_num, day_num)
        if key not in available:
            print(f"ERROR: No data for round {round_num} day {day_num}")
            continue

        files = available[key]
        bt = ProsperityBacktester(
            bot_file_path=args.bot_file,
            prices_path=files["prices"],
            trades_path=files["trades"],
            round_num=round_num,
            day_num=day_num,
        )

        if args.print_output:
            bt.run()
        else:
            bt.run()


if __name__ == "__main__":
    # If no CLI args provided, use defaults for easy testing
    if len(sys.argv) == 1:
        resolved_data_root = find_data_root()
        data_root = str(resolved_data_root) if resolved_data_root is not None else None
        if data_root is None:
            print("ERROR: No data directory found. Pass arguments or set --data-root.")
            sys.exit(1)
        available = discover_data_files(data_root)
        key = (1, 0)
        if key not in available:
            key = sorted(available.keys())[0] if available else None
        if key is None:
            print("ERROR: No data files found.")
            sys.exit(1)
        files = available[key]
        bt = ProsperityBacktester(
            bot_file_path=str(default_bot_path()),
            prices_path=files["prices"],
            trades_path=files["trades"],
            round_num=key[0],
            day_num=key[1],
        )
        bt.run()
    else:
        main()
