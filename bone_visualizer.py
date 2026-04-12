import argparse
import subprocess
import os
import json
import re
import sys

def run_backtester(bot_file, round_num, day_num=None):
    """Runs jmerle's backtester and returns the path to the output log."""
    # We will use the jmerle backtester installed, or via the local Jmerle-Backtester folder
    # For now, let's assume `prosperity3bt` is installed or we can run it via module.
    # The backtester outputs a .log file which we will capture.
    
    log_file = "latest_run.log"
    print(f"[*] Running backtester on {bot_file} (Round {round_num})...")
    
    # Check if prosperity3bt is installed globally, otherwise use local uv run
    # Let's try running the command line tool
    cmd = ["python", "-m", "prosperity3bt", bot_file, str(round_num)]
    if day_num is not None:
        cmd.append(str(day_num))
    cmd.extend(["--out", log_file])
    
    try:
        # Try global first
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Fallback to local uv run in Jmerle-Backtester
            print("[*] Global prosperity3bt failed, trying local uv run...")
            cmd = ["uv", "run", "prosperity3bt", os.path.abspath(bot_file), str(round_num)]
            if day_num is not None:
                cmd.append(str(day_num))
            cmd.extend(["--out", os.path.abspath(log_file)])
            
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.abspath(".")
            result = subprocess.run(cmd, cwd="Jmerle-Backtester", capture_output=True, text=True, env=env)
            if result.returncode != 0:
                print("[-] Backtester failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                sys.exit(1)
    except FileNotFoundError:
        print("[-] python or backtester module not found!")
        sys.exit(1)
        
    print("[+] Backtest complete!")
    return log_file

def parse_log(log_file):
    """Parses the jmerle log file to extract Activities log and Trade History."""
    print(f"[*] Parsing {log_file}...")
    
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Activities log (CSV format embedded in log)
    activities_match = re.search(r"Activities log:\n(.+?)(?=\n\n|\Z)", content, re.DOTALL)
    activities_csv = activities_match.group(1) if activities_match else ""
    
    # Extract Trade History
    trades_match = re.search(r"Trade History:\n(.+?)(?=\n\n|\Z)", content, re.DOTALL)
    trades_json_str = trades_match.group(1) if trades_match else "[]"
    
    try:
        trades = json.loads(trades_json_str)
    except json.JSONDecodeError:
        trades = []

    return activities_csv, trades

def plot_data(activities_csv, trades):
    """Plots the data using plotly and opens it in a browser."""
    print("[*] Generating interactive plot...")
    try:
        import pandas as pd
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        from io import StringIO
    except ImportError:
        print("[-] Missing dependencies! Please run: pip install pandas plotly")
        sys.exit(1)

    if not activities_csv.strip():
        print("[-] No activities log found. Did the algorithm run successfully?")
        return

    # Load activities into a pandas DataFrame
    df = pd.read_csv(StringIO(activities_csv), sep=";")
    
    if trades:
        trades_df = pd.DataFrame(trades)
    else:
        trades_df = pd.DataFrame(columns=["timestamp", "buyer", "seller", "symbol", "currency", "price", "quantity"])

    # We will create a subplot for each product
    products = df['product'].unique()
    
    # Create HTML file
    print(f"[+] Found {len(products)} products: {', '.join(products)}")
    
    for product in products:
        prod_df = df[df['product'] == product]
        prod_trades = trades_df[trades_df['symbol'] == product] if not trades_df.empty else trades_df
        
        # Create figure with secondary y-axis for PnL
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add mid_price
        fig.add_trace(
            go.Scatter(x=prod_df['timestamp'], y=prod_df['mid_price'], name="Mid Price", line=dict(color='gray')),
            secondary_y=False,
        )
        
        # Add PnL
        fig.add_trace(
            go.Scatter(x=prod_df['timestamp'], y=prod_df['profit_and_loss'], name="PnL", line=dict(color='blue', dash='dash')),
            secondary_y=True,
        )
        
        # Add Buy/Sell trade markers
        if not prod_trades.empty:
            # You are the buyer when buyer is not empty (wait, actually backtester uses specific names or just 'SUBMISSION')
            # In standard logs, if buyer == "SUBMISSION" or similar
            # For simplicity, if your trade exists, we can show it
            buys = prod_trades[prod_trades['buyer'] == "SUBMISSION"]
            sells = prod_trades[prod_trades['seller'] == "SUBMISSION"]
            
            if not buys.empty:
                fig.add_trace(
                    go.Scatter(
                        x=buys['timestamp'], y=buys['price'], 
                        mode='markers', name='Buy',
                        marker=dict(color='green', symbol='triangle-up', size=10)
                    ),
                    secondary_y=False,
                )
            if not sells.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sells['timestamp'], y=sells['price'], 
                        mode='markers', name='Sell',
                        marker=dict(color='red', symbol='triangle-down', size=10)
                    ),
                    secondary_y=False,
                )
                
        fig.update_layout(
            title_text=f"Product: {product} - Mid Price and PnL",
            height=600
        )
        
        fig.update_xaxes(title_text="Timestamp")
        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="PnL", secondary_y=True)
        
        # Save and show
        html_file = f"{product}_visualizer.html"
        fig.write_html(html_file)
        print(f"[+] Generated {html_file}")
        
        # Open in browser
        import webbrowser
        webbrowser.open('file://' + os.path.realpath(html_file))

def main():
    parser = argparse.ArgumentParser(description="Prosperity 4 Simple Bone Visualizer")
    parser.add_argument("bot_file", help="Path to your bot python file")
    parser.add_argument("round", type=int, help="Round number (0-6)")
    parser.add_argument("day", type=int, nargs="?", default=None, help="Day number (optional)")
    
    args = parser.parse_args()
    
    # 1. Run the backtester
    log_file = run_backtester(args.bot_file, args.round, args.day)
    
    # 2. Parse the log
    activities_csv, trades = parse_log(log_file)
    
    # 3. Plot the data
    plot_data(activities_csv, trades)

if __name__ == "__main__":
    main()
