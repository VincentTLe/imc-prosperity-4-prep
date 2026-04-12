# -*- coding: utf-8 -*-
"""
=============================================================================
PROSPERITY 4 — LEARNING VISUALIZER
=============================================================================
Run:  streamlit run visualizer.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import re
import sys
import time
import subprocess

from project_paths import PROJECT_ROOT, default_bot_path, find_data_root

# =============================================================================
# PAGE CONFIG & CUSTOM STYLING
# =============================================================================
st.set_page_config(page_title="Prosperity 4 Visualizer", layout="wide", page_icon="📈")

st.markdown("""
<style>
    /* Premium Dark Mode Glassmorphism Theme */
    .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 95%; }
    
    /* Modern Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 229, 255, 0.15);
        border: 1px solid rgba(0, 229, 255, 0.3);
    }
    [data-testid="stMetricLabel"] { font-size: 0.9rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    [data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 700; color: #f8fafc; padding-top: 4px; }
    
    /* Typography */
    h1, h2, h3 { color: #f1f5f9; font-weight: 600; }
    h3 { margin-top: 1.5rem !important; margin-bottom: 1rem !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #06090f; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    
    /* Table styling */
    .dataframe { border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS
# =============================================================================
DATA_ROOT_PATH = find_data_root()
PROJECT_ROOT_STR = str(PROJECT_ROOT)
DATA_ROOT = str(DATA_ROOT_PATH) if DATA_ROOT_PATH is not None else ""
BACKTESTER = str(PROJECT_ROOT / "backtester.py")
RESULTS_FILE = str(PROJECT_ROOT / "backtest_results.json")
DEFAULT_BOT = os.path.relpath(default_bot_path(), PROJECT_ROOT_STR)

# Color palette — Premium Cyber/Neon Theme
C_BID       = "#00E5FF"   # Neon Cyan (Bid)
C_ASK       = "#FF0055"   # Neon Pink (Ask)
C_MID       = "#E2E8F0"   # Light Grey (Mid)
C_BUY_MKR   = "#00E5FF"   # Neon Cyan markers
C_SELL_MKR  = "#FF0055"   # Neon Pink markers
C_PNL       = "#A78BFA"   # Pastel Purple (PnL)
C_POS       = "#FBBF24"   # Amber/Gold (Position)
C_SPREAD    = "#34D399"   # Mint Green (Spread)
C_BAND      = "rgba(0, 229, 255, 0.05)"  # subtle cyan glow
C_BID_L2    = "rgba(0, 229, 255, 0.3)"
C_BID_L3    = "rgba(0, 229, 255, 0.15)"
C_ASK_L2    = "rgba(255, 0, 85, 0.3)"
C_ASK_L3    = "rgba(255, 0, 85, 0.15)"

# =============================================================================
# SESSION STATE
# =============================================================================
for key, default in [
    ("last_bot_mtime", 0.0),
    ("auto_refresh_on", True),
    ("last_run_status", "No backtest run yet."),
    ("last_run_ok", True),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# =============================================================================
# HELPERS
# =============================================================================
def discover_data_files(data_root):
    rounds = {}
    if not os.path.isdir(data_root):
        return rounds
    for fp, _, filenames in os.walk(data_root):
        for fname in filenames:
            m = re.match(r"prices_round_(\d+)_day_(-?\d+)\.csv", fname)
            if m:
                r, d = int(m.group(1)), int(m.group(2))
                rounds.setdefault(r, []).append(d)
    for r in rounds:
        rounds[r] = sorted(set(rounds[r]))
    return dict(sorted(rounds.items()))


def run_backtest(bot_file, round_num, day_num):
    bot_path = os.path.join(PROJECT_ROOT_STR, bot_file) if not os.path.isabs(bot_file) else bot_file
    return subprocess.run(
        [sys.executable, BACKTESTER, bot_path, str(round_num), str(day_num), "--data-root", DATA_ROOT],
        capture_output=True, text=True, timeout=120,
    )


def load_results():
    if not os.path.exists(RESULTS_FILE):
        return None
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # Race condition: backtester is writing while we're reading.
        # Wait briefly and retry once.
        time.sleep(0.5)
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return None


def extract_depth_levels(depth_list, side="bid"):
    """Extract 3 price levels from depth snapshots into separate arrays.

    bid side: sorted descending (best=highest), ask side: sorted ascending (best=lowest)
    Returns (level1_prices, level2_prices, level3_prices)
    """
    l1, l2, l3 = [], [], []
    reverse = (side == "bid")
    for snap in depth_list:
        prices = sorted(snap.keys(), key=lambda x: int(x), reverse=reverse)
        l1.append(int(prices[0]) if len(prices) > 0 else None)
        l2.append(int(prices[1]) if len(prices) > 1 else None)
        l3.append(int(prices[2]) if len(prices) > 2 else None)
    return l1, l2, l3


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.header("⚙️ Settings")
    bot_file = st.text_input("Bot file", value=DEFAULT_BOT)
    bot_abs_path = os.path.join(PROJECT_ROOT_STR, bot_file)

    available = discover_data_files(DATA_ROOT)
    if DATA_ROOT:
        st.caption(f"Data root: `{DATA_ROOT}`")
    if available:
        selected_round = st.selectbox("Round", list(available.keys()))
        day_opts = available[selected_round]
        selected_day = st.selectbox("Day", day_opts,
                                    index=day_opts.index(0) if 0 in day_opts else 0)
    else:
        st.warning("No data files found.")
        selected_round, selected_day = 1, 0

    st.divider()
    st.session_state.auto_refresh_on = st.toggle("Auto-refresh on save",
                                                  value=st.session_state.auto_refresh_on)
    poll_interval = st.slider("Poll interval (sec)", 1, 10, 2)

    st.divider()
    if st.button("▶ Run Backtest Now", use_container_width=True):
        with st.spinner("Running backtest..."):
            r = run_backtest(bot_file, selected_round, selected_day)
        st.session_state.last_run_ok = r.returncode == 0
        st.session_state.last_run_status = (
            f"OK at {time.strftime('%H:%M:%S')}" if r.returncode == 0
            else (r.stderr[-500:] if r.stderr else "Unknown error")
        )
        st.rerun()

    if st.session_state.last_run_ok:
        st.success(st.session_state.last_run_status)
    else:
        st.error(st.session_state.last_run_status)

    st.divider()
    with st.expander("📄 Bot Code"):
        if os.path.exists(bot_abs_path):
            with open(bot_abs_path, "r", encoding="utf-8") as f:
                st.code(f.read(), language="python", line_numbers=True)

# =============================================================================
# AUTO-REFRESH
# =============================================================================
if st.session_state.auto_refresh_on and os.path.exists(bot_abs_path):
    mtime = os.path.getmtime(bot_abs_path)
    if mtime != st.session_state.last_bot_mtime:
        st.session_state.last_bot_mtime = mtime
        with st.spinner("📡 File changed — running backtest..."):
            r = run_backtest(bot_file, selected_round, selected_day)
        st.session_state.last_run_ok = r.returncode == 0
        st.session_state.last_run_status = (
            f"Auto-run OK at {time.strftime('%H:%M:%S')}" if r.returncode == 0
            else (r.stderr[-500:] if r.stderr else "Error")
        )
        st.rerun()

# =============================================================================
# LOAD DATA
# =============================================================================
data = load_results()

st.title("📈 Prosperity 4 — Learning Visualizer")

if data is None:
    st.warning("No backtest results. Click **Run Backtest Now** in the sidebar.")
    if st.session_state.auto_refresh_on:
        time.sleep(poll_interval)
        st.rerun()
    st.stop()

# =============================================================================
# DATA PREPARATION
# =============================================================================
metadata   = data.get("metadata", {})
timestamps = data["timestamps"]
products   = list(data["products"].keys())

# Product selector + metrics
col_sel, col_m1, col_m2, col_m3, col_m4 = st.columns([1.5, 1, 1, 1, 1])
with col_sel:
    selected_product = st.selectbox("Product", products, label_visibility="collapsed")

prod      = data["products"][selected_product]
pos_limit = metadata.get("position_limits", {}).get(selected_product, 50)
final_pnl = prod["pnl"][-1] if prod["pnl"] else 0
final_pos = prod["position"][-1] if prod["position"] else 0
n_trades  = len(prod.get("trades", []))

col_m1.metric("💰 PnL", f"{final_pnl:+,.0f}")
col_m2.metric("📦 Position", f"{final_pos:+d}")
col_m3.metric("🔄 Trades", f"{n_trades}")
col_m4.metric("📏 Limit", f"±{pos_limit}")

# Build main DataFrame
df = pd.DataFrame({
    "ts": timestamps,
    "mid": prod["mid_price"],
    "pnl": prod["pnl"],
    "pos": prod["position"],
})

# Best bid/ask
bb = prod.get("best_bid", [])
ba = prod.get("best_ask", [])
if bb and ba:
    df["bb"] = bb
    df["ba"] = ba
    df["spread"] = [a - b if a and b else None for a, b in zip(ba, bb)]

# Extract depth levels (3 bid + 3 ask)
bid_depth = prod.get("bid_depth", [])
ask_depth = prod.get("ask_depth", [])
if bid_depth:
    bl1, bl2, bl3 = extract_depth_levels(bid_depth, "bid")
    al1, al2, al3 = extract_depth_levels(ask_depth, "ask")
    df["bl1"], df["bl2"], df["bl3"] = bl1, bl2, bl3
    df["al1"], df["al2"], df["al3"] = al1, al2, al3

trades_df = pd.DataFrame(prod.get("trades", []))

# =============================================================================
# MAIN CHART — Price + PnL + Position (shared x-axis, with range slider)
# =============================================================================
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.55, 0.225, 0.225],
    subplot_titles=["Price & Order Book", "Profit & Loss", "Position"],
)

# ── Row 1: PRICE CHART ──────────────────────────────────────────────────────

# Depth level 3 (faintest)
if "bl3" in df.columns:
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["bl3"], mode="lines", name="Bid L3",
        line=dict(width=0), showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["al3"], mode="lines", name="Ask L3",
        line=dict(width=0), fill="tonexty", fillcolor="rgba(148,163,184,0.06)",
        showlegend=False,
    ), row=1, col=1)

# Depth level 2
if "bl2" in df.columns:
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["bl2"], mode="lines", name="Bid L2",
        line=dict(width=0.5, color=C_BID_L2, dash="dot"), showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["al2"], mode="lines", name="Ask L2",
        line=dict(width=0.5, color=C_ASK_L2, dash="dot"), showlegend=False,
    ), row=1, col=1)

# Best bid / ask (level 1) — solid thin lines with band fill
if "ba" in df.columns:
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["ba"], mode="lines", name="Best Ask",
        line=dict(width=1, color=C_ASK),
    ), row=1, col=1)
    fig.add_trace(go.Scattergl(
        x=df["ts"], y=df["bb"], mode="lines", name="Best Bid",
        line=dict(width=1, color=C_BID),
        fill="tonexty", fillcolor=C_BAND,
    ), row=1, col=1)

# Mid price — main reference
fig.add_trace(go.Scattergl(
    x=df["ts"], y=df["mid"], mode="lines", name="Mid Price",
    line=dict(width=2, color=C_MID),
), row=1, col=1)

# Fair value line (for Resin-type products)
if "RESIN" in selected_product.upper():
    fig.add_hline(y=10000, line_dash="dot", line_color="#f59e0b", line_width=1,
                  annotation_text="Fair Value 10,000",
                  annotation_position="top right",
                  annotation_font_size=10, annotation_font_color="#92400e",
                  row=1, col=1)

# Trade markers — large & prominent on top
if not trades_df.empty:
    buys = trades_df[trades_df["type"] == "BUY"]
    sells = trades_df[trades_df["type"] == "SELL"]
    if not buys.empty:
        fig.add_trace(go.Scattergl(
            x=buys["timestamp"], y=buys["price"], mode="markers", name="Buy",
            marker=dict(color=C_BUY_MKR, symbol="triangle-up", size=12,
                        line=dict(color="rgba(255,255,255,0.9)", width=1)),
            hovertemplate="BUY %{y} × %{customdata}<extra></extra>",
            customdata=buys["quantity"],
        ), row=1, col=1)
    if not sells.empty:
        fig.add_trace(go.Scattergl(
            x=sells["timestamp"], y=sells["price"], mode="markers", name="Sell",
            marker=dict(color=C_SELL_MKR, symbol="triangle-down", size=12,
                        line=dict(color="rgba(255,255,255,0.9)", width=1)),
            hovertemplate="SELL %{y} × %{customdata}<extra></extra>",
            customdata=sells["quantity"],
        ), row=1, col=1)

# ── Row 2: PNL ──────────────────────────────────────────────────────────────
fig.add_trace(go.Scattergl(
    x=df["ts"], y=df["pnl"], mode="lines", name="PnL",
    line=dict(width=2, color=C_PNL),
    fill="tozeroy", fillcolor="rgba(167, 139, 250, 0.1)",
), row=2, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1, row=2, col=1)

# ── Row 3: POSITION ─────────────────────────────────────────────────────────
fig.add_trace(go.Scattergl(
    x=df["ts"], y=df["pos"], mode="lines", name="Position",
    line=dict(width=2, color=C_POS),
    fill="tozeroy", fillcolor="rgba(251, 191, 36, 0.1)",
), row=3, col=1)
fig.add_hline(y=pos_limit,  line_dash="dot", line_color="rgba(255,0,85,0.5)", line_width=1, row=3, col=1)
fig.add_hline(y=-pos_limit, line_dash="dot", line_color="rgba(255,0,85,0.5)", line_width=1, row=3, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1, row=3, col=1)

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    height=800,
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(15, 23, 42, 0.95)", font_size=12, font_family="monospace", bordercolor="rgba(255,255,255,0.1)"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        font=dict(size=11, color="#cbd5e1"), bgcolor="rgba(0,0,0,0)",
    ),
    margin=dict(t=40, b=15, l=60, r=20),
)
# Update grid lines to be subtle
for axis in [fig.layout.xaxis, fig.layout.xaxis2, fig.layout.xaxis3]:
    axis.gridcolor = "rgba(255,255,255,0.05)"
for axis in [fig.layout.yaxis, fig.layout.yaxis2, fig.layout.yaxis3]:
    axis.gridcolor = "rgba(255,255,255,0.05)"

# Range slider on the bottom x-axis — this is how you zoom & navigate
fig.update_xaxes(
    rangeslider=dict(visible=True, thickness=0.04),
    row=3, col=1,
)
# Clean axis labels
fig.update_yaxes(title_text="Price", title_font_size=10, row=1, col=1)
fig.update_yaxes(title_text="PnL",   title_font_size=10, row=2, col=1)
fig.update_yaxes(title_text="Pos",   title_font_size=10, row=3, col=1)

st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SPREAD CHART (small, optional)
# =============================================================================
if "spread" in df.columns:
    with st.expander("📐 Bid-Ask Spread over time"):
        spread_fig = go.Figure()
        spread_fig.add_trace(go.Scattergl(
            x=df["ts"], y=df["spread"], mode="lines",
            line=dict(width=1.5, color=C_SPREAD),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
            hovertemplate="Spread: %{y}<extra></extra>",
        ))
        spread_fig.update_layout(
            height=200, template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=30, l=60, r=20),
            xaxis=dict(rangeslider=dict(visible=True, thickness=0.06), gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Spread", title_font_size=10, gridcolor="rgba(255,255,255,0.05)"),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="rgba(15, 23, 42, 0.95)", font_size=12, bordercolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(spread_fig, use_container_width=True)

# =============================================================================
# TRADE HISTORY — clean table with colored type column
# =============================================================================
st.markdown("### 📋 Trades")
if not trades_df.empty:
    display_df = trades_df.sort_values("timestamp", ascending=False).reset_index(drop=True)

    # Reorder columns for readability
    col_order = ["timestamp", "type", "price", "quantity", "buyer", "seller"]
    display_df = display_df[[c for c in col_order if c in display_df.columns]]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=300,
        column_config={
            "timestamp": st.column_config.NumberColumn("Time", format="%d"),
            "type":      st.column_config.TextColumn("Side", width="small"),
            "price":     st.column_config.NumberColumn("Price", format="%d"),
            "quantity":  st.column_config.NumberColumn("Qty", format="%d"),
            "buyer":     st.column_config.TextColumn("Buyer", width="small"),
            "seller":    st.column_config.TextColumn("Seller", width="small"),
        },
    )
else:
    st.info("No trades — try adjusting the threshold in your bot!")

# =============================================================================
# SANDBOX LOGS — searchable
# =============================================================================
sandbox_logs = data.get("sandbox_logs", {})
if sandbox_logs:
    with st.expander("🖥️ Bot Logs (print output)"):
        search = st.text_input("🔍 Filter", "", placeholder="Type to search...",
                               key="log_search")
        matches = []
        for ts_key in sorted(sandbox_logs, key=lambda x: int(x)):
            text = sandbox_logs[ts_key]
            if not text:
                continue
            if search and search.lower() not in text.lower():
                continue
            matches.append(f"[t={ts_key}] {text}")

        if matches:
            # Show in a scrollable container
            st.code("\n".join(matches[:300]), language="text")
            if len(matches) > 300:
                st.caption(f"Showing first 300 of {len(matches)} entries.")
        else:
            st.caption("No matching logs." if search else "No logs with output.")

# =============================================================================
# EDUCATIONAL
# =============================================================================
with st.expander("📚 How to read this dashboard"):
    st.markdown("""
**Price chart** _(top, largest)_
- **Dark line** = mid price (average of best bid & ask)
- **Green line** = best bid (highest buy offer). **Red line** = best ask (lowest sell offer)
- **Shaded band** between bid & ask = the spread. Narrower = more liquid market
- **Faint dotted lines** = deeper order book levels (level 2 & 3)
- **▲ Green triangles** = your bot bought here. **▼ Red triangles** = your bot sold here
- **Orange dotted line** = fair value (for Resin: always 10,000)

**PnL chart** _(middle)_
- Your cumulative profit. Rising = making money.

**Position chart** _(bottom)_
- How many units you hold. Red dotted lines = position limits (±{pos_limit}).

**How to zoom**: Drag the **range slider** at the very bottom of the chart to zoom into any time window. All 3 charts zoom together.

**Experiment ideas:**
1. Change `< 10000` → `< 9999` in your bot → fewer buys, more selective
2. Change `> 10000` → `> 10001` → fewer sells, more selective
3. Save the file → charts update automatically!
    """)

# =============================================================================
# POLLING LOOP
# =============================================================================
if st.session_state.auto_refresh_on:
    time.sleep(poll_interval)
    st.rerun()
