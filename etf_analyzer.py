import yfinance as yf
import pandas_ta as ta
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
from etf_library import ETF_LIBRARY

# ═══════════════════════════════════════════════════════════════
#  EUROPEAN ETF LIBRARY — verified working tickers only
#  Format: "TICKER": ("Name", "Exchange", "Category")
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def rsi_signal(rsi):
    
    if rsi >= 70:    return "🔴 Overbought"
    elif rsi >= 55:  return "🟡 Mild bullish"
    elif rsi >= 45:  return "⚪ Neutral"
    elif rsi >= 30:  return "🟡 Mild bearish"
    else:            return "🟢 Oversold"

def trend_signal(price, sma50, sma200):
    if price > sma50 > sma200:    return "📈 Uptrend"
    elif price < sma50 < sma200:  return "📉 Downtrend"
    else:                         return "↔  Mixed"

def pct_change(data, days):
    if len(data) < days:
        return None
    start = data["Close"].iloc[-days]
    end   = data["Close"].iloc[-1]
    return ((end - start) / start) * 100

# ═══════════════════════════════════════════════════════════════
#  SAVE TO CSV — appends results to a history file
# ═══════════════════════════════════════════════════════════════

def save_to_csv(results, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename  = f"etf_scan_{timestamp}.csv"

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
             "Date", "Time", "Ticker", "Name", "Price", "RSI",
            "1D%", "1W%", "1M%", "3M%", "6M%", "1Y%",
            "Signal", "Trend", "DEGIRO Name", "ISIN"
        ])

        scan_date = datetime.now().strftime("%d %b %Y")
        scan_time = datetime.now().strftime("%H:%M")

        for r in results:
            # Get DEGIRO and ISIN from library
            info    = ETF_LIBRARY.get(r["ticker"], (r["ticker"], "Unknown", "Unknown", "n/a", "n/a"))
            degiro  = info[3] if len(info) > 3 else "n/a"
            isin    = info[4] if len(info) > 4 else "n/a"

            # Clean emoji from signal and trend
            signal = r.get("signal", rsi_signal(r.get("rsi", 0)))
            trend  = r.get("trend", "n/a")

            clean_signal = signal.replace("🔴","").replace("🟡","") \
                                 .replace("⚪","").replace("🟢","").strip()
            clean_trend  = trend.replace("📈","").replace("📉","") \
                                .replace("↔","").strip()

            writer.writerow([
                scan_date, scan_time,
                r["ticker"], r["name"],
                round(r["price"],       2),
                round(r["rsi"],         1),
                round(r.get("mom_1d",  0), 1),
                round(r.get("mom_1w",  0), 1),
                round(r.get("mom_1m",  0), 1),
                round(r.get("mom_3m",  0), 1),
                round(r.get("mom_6m",  0), 1),
                round(r.get("mom_1y",  0), 1),
                clean_signal, clean_trend,
                degiro, isin
            ])
            
    print(f"\n  ✓  Results saved to {filename}")
    print(f"     Open in Excel to see your scan history.\n")

    print(f"\n  {'Ticker':<12} {'Name':<32} {'Price':>8} {'RSI':>6}  "
      f"{'1D%':>6} {'1W%':>7} {'1M%':>7} {'3M%':>7} {'6M%':>7} {'1Y%':>7}  "
      f"{'Signal':<16} {'Trend'}")
    print("  " + "─" * 115)


# ═══════════════════════════════════════════════════════════════
#  FETCH + ANALYSE A LIST OF TICKERS
# ═══════════════════════════════════════════════════════════════

def analyse(tickers):
    print(f"\n  {'Ticker':<12} {'Name':<32} {'Price':>8} {'RSI':>6}  "
          f"{'1M%':>6}  {'Signal':<16} {'Trend'}")
    print("  " + "─" * 95)

    results = []

    for ticker in tickers:
        try:
            info = ETF_LIBRARY.get(ticker, (ticker, "Unknown", "Unknown", "n/a", "n/a"))
            name, exch, _, degiro, isin = info

            data = yf.Ticker(ticker).history(period="1y")

            if data.empty or len(data) < 20:
                print(f"  {ticker:<12} No data available")
                continue

            data["RSI"]    = ta.rsi(data["Close"], length=14)
            data["SMA50"]  = ta.sma(data["Close"], length=50)
            data["SMA200"] = ta.sma(data["Close"], length=200)

            price  = data["Close"].iloc[-1]
            rsi    = data["RSI"].iloc[-1]
            sma50  = data["SMA50"].iloc[-1]
            sma200 = data["SMA200"].iloc[-1]
            mom_1d  = pct_change(data, 1)
            mom_1w  = pct_change(data, 5)
            mom_1m  = pct_change(data, 21)
            mom_3m  = pct_change(data, 63)
            mom_6m  = pct_change(data, 126)
            mom_1y  = pct_change(data, 252)

            signal  = rsi_signal(rsi)
            trend   = trend_signal(price, sma50, sma200)

            def fmt(v): return f"{v:+.1f}%" if v is not None else "  n/a"

            print(f"  {ticker:<12} {name:<32} {price:>8.2f} {rsi:>6.1f}  "
                f"{fmt(mom_1d):>6} {fmt(mom_1w):>7} {fmt(mom_1m):>7} "
                f"{fmt(mom_3m):>7} {fmt(mom_6m):>7} {fmt(mom_1y):>7}  "
                f"{signal:<16} {trend}")

            results.append({
                "ticker": ticker,
                "name":   name,
                "data":   data,
                "price":  price,
                "rsi":    rsi,
                "mom_1d": mom_1d or 0,
                "mom_1w": mom_1w or 0,
                "mom_1m": mom_1m or 0,
                "mom_3m": mom_3m or 0,
                "mom_6m": mom_6m or 0,
                "mom_1y": mom_1y or 0,
                "signal": signal,
                "trend":  trend,
            })

        except Exception as e:
            print(f"  {ticker:<12} Skipped — {str(e)[:50]}")

    return results


# ═══════════════════════════════════════════════════════════════
#  TOP PERFORMERS — scan everything and rank by 1 month return
# ═══════════════════════════════════════════════════════════════

def top_performers():
    print("\n  Scanning all ETFs — takes about 30 seconds...\n")

    ranked = []

    for ticker, (name, exchange, category, degiro, isin) in ETF_LIBRARY.items():        
        try:
            data = yf.Ticker(ticker).history(period="6mo")

            if data.empty or len(data) < 25:
                continue

            data["RSI"] = ta.rsi(data["Close"], length=14)

            price  = data["Close"].iloc[-1]
            rsi    = data["RSI"].iloc[-1]
            mom_1d  = pct_change(data, 1)
            mom_1w  = pct_change(data, 5)
            mom_1m  = pct_change(data, 21)
            mom_3m  = pct_change(data, 63)
            mom_6m  = pct_change(data, 126)
            mom_1y  = pct_change(data, 252)

            if mom_1m is not None:
                ranked.append({
                    "ticker":   ticker,
                    "name":     name,
                    "category": category,
                    "price":    price,
                    "rsi":      rsi,
                    "mom_1d":   mom_1d or 0,
                    "mom_1w":   mom_1w or 0,
                    "mom_1m":   mom_1m,
                    "mom_3m":   mom_3m or 0,
                    "mom_6m":   mom_6m or 0,
                    "mom_1y":   mom_1y or 0,
                    "data":     data,
                })

        except Exception:
            continue

    ranked.sort(key=lambda x: x["mom_1m"], reverse=True)

    print(f"  {'Rank':<6} {'Ticker':<12} {'Name':<32} "
        f"{'1D%':>6} {'1W%':>7} {'1M%':>7} {'3M%':>7} {'6M%':>7} {'1Y%':>7} {'RSI':>6}  {'Category'}")
    print("  " + "─" * 100)

    print("  📈  TOP 5 — strongest momentum:")
    for i, r in enumerate(ranked[:5], 1):
        print(f"  {i:<6} {r['ticker']:<12} {r['name']:<32} "
            f"{r['mom_1d']:>+6.1f}% {r['mom_1w']:>+6.1f}% {r['mom_1m']:>+6.1f}% "
            f"{r['mom_3m']:>+6.1f}% {r['mom_6m']:>+6.1f}% {r['mom_1y']:>+6.1f}% "
            f"{r['rsi']:>6.1f}  {r['category']}")

    print("\n  📉  BOTTOM 5 — potential recovery candidates:")
    for i, r in enumerate(ranked[-5:], 1):
        print(f"  {i:<6} {r['ticker']:<12} {r['name']:<32} "
            f"{r['mom_1d']:>+6.1f}% {r['mom_1w']:>+6.1f}% {r['mom_1m']:>+6.1f}% "
            f"{r['mom_3m']:>+6.1f}% {r['mom_6m']:>+6.1f}% {r['mom_1y']:>+6.1f}% "
            f"{r['rsi']:>6.1f}  {r['category']}")

# ═══════════════════════════════════════════════════════════════
#  CHART — price with SMA lines + RSI panel
# ═══════════════════════════════════════════════════════════════

def draw_chart(ticker, name, data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)

    # ── Price panel ──
    ax1.plot(data.index, data["Close"],
             color="steelblue", linewidth=1.5, label="Price")
    if "SMA50" in data.columns:
        ax1.plot(data.index, data["SMA50"],
                 color="orange", linewidth=1, linestyle="--", label="SMA 50")
    if "SMA200" in data.columns:
        ax1.plot(data.index, data["SMA200"],
                 color="red", linewidth=1, linestyle="--", label="SMA 200")
    ax1.set_title(f"{ticker}  —  {name}  |  Price & RSI", fontsize=13)
    ax1.set_ylabel("Price")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(True, alpha=0.3)

    # ── RSI panel ──
    ax2.plot(data.index, data["RSI"],
             color="orange", linewidth=1.5, label="RSI (14)")
    ax2.axhline(70, color="red",   linestyle="--", linewidth=1, label="Overbought (70)")
    ax2.axhline(30, color="green", linestyle="--", linewidth=1, label="Oversold (30)")
    ax2.axhline(50, color="gray",  linestyle=":",  linewidth=0.8)
    ax2.fill_between(data.index, 70, 100, color="red",   alpha=0.07)
    ax2.fill_between(data.index, 0,  30,  color="green", alpha=0.07)
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# ═══════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════

def show_menu():
    categories = sorted(set(v[2] for v in ETF_LIBRARY.values()))
    n = len(categories)

    print("\n" + "═" * 60)
    print(f"  EUROPEAN ETF ANALYSER  |  {datetime.now().strftime('%d %b %Y  %H:%M')}")
    print("═" * 60)
    print("\n  Browse by category:\n")

    for i, cat in enumerate(categories, 1):
        count = sum(1 for v in ETF_LIBRARY.values() if v[2] == cat)
        print(f"  {i:>2}.  {cat:<30} ({count} ETF{'s' if count > 1 else ''})")

    print()
    print(f"  {n+1:>2}.  🏆 Top performers  (scan all {len(ETF_LIBRARY)} ETFs)")
    print(f"  {n+2:>2}.  📋 Show all ETFs")
    print(f"  {n+3:>2}.  ✏️  Type a ticker manually")
    print()

    choice = input("  Enter number: ").strip()

    try:
        choice_num = int(choice)
    except ValueError:
        print("  Invalid input — please enter a number.")
        return None, []

    if choice_num == n + 3:
        manual = input("  Enter ticker (e.g. IWDA.AS): ").strip().upper()
        return "list", [manual]

    elif choice_num == n + 2:
        return "list", list(ETF_LIBRARY.keys())

    elif choice_num == n + 1:
        return "top", []

    elif 1 <= choice_num <= n:
        selected = categories[choice_num - 1]
        tickers  = [t for t, v in ETF_LIBRARY.items() if v[2] == selected]
        return "list", tickers

    else:
        print("  Number out of range — please try again.")
        return None, []


# ═══════════════════════════════════════════════════════════════
#  CHART PROMPT — ask user which ticker to chart after results
# ═══════════════════════════════════════════════════════════════

def prompt_chart(results):
    if not results:
        return
    print("\n  Draw a chart for any of the above?  (press Enter to skip)")
    choice = input("  Ticker: ").strip().upper()
    if not choice:
        return
    match = [r for r in results if r["ticker"] == choice]
    if match:
        r = match[0]
        # Make sure SMA columns exist
        if "SMA50" not in r["data"].columns:
            r["data"]["SMA50"]  = ta.sma(r["data"]["Close"], length=50)
            r["data"]["SMA200"] = ta.sma(r["data"]["Close"], length=200)
        draw_chart(r["ticker"], r["name"], r["data"])
    else:
        print(f"  '{choice}' not in results — skipping chart.")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

print("\n  ⚠   For personal learning only — not financial advice.\n")

mode, tickers = show_menu()

if mode == "top":
    ranked = top_performers()
    # Convert ranked list to results format for saving
    save_to_csv(ranked)
    all_results = [
        {"ticker": r["ticker"], "name": r["name"], "data": r["data"]}
        for r in ranked
    ]
    prompt_chart(all_results)

elif mode == "list" and tickers:
    results = analyse(tickers)
    save_to_csv(results)       # ← saves category scans too
    prompt_chart(results)

print("\n  Done.\n")
