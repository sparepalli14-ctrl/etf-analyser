import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from etf_library import ETF_LIBRARY

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="European ETF Analyser",
    page_icon="📈",
    layout="wide"
)

st.title("📈 European ETF Analyser")
st.caption(
    f"Last run: {datetime.now().strftime('%d %b %Y  %H:%M')}  "
    f"|  For personal learning only — not financial advice."
)

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def pct_change(data, days):
    if len(data) < days:
        return 0.0
    start = data["Close"].iloc[-days]
    end   = data["Close"].iloc[-1]
    return round(((end - start) / start) * 100, 1)

def rsi_signal(rsi):
    if rsi >= 70:    return "🔴 Overbought"
    elif rsi >= 55:  return "🟡 Mild bullish"
    elif rsi >= 45:  return "⚪ Neutral"
    elif rsi >= 30:  return "🟡 Mild bearish"
    else:            return "🟢 Oversold"

def trend_label(price, sma50, sma200):
    if price > sma50 > sma200:    return "📈 Uptrend"
    elif price < sma50 < sma200:  return "📉 Downtrend"
    else:                         return "↔ Mixed"

# ═══════════════════════════════════════════════════════════════
#  FETCH + CACHE
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800)
def fetch_all():
    results = []
    for ticker, (name, exch, cat, degiro, isin) in ETF_LIBRARY.items():
        try:
            data = yf.Ticker(ticker).history(period="1y")
            if data.empty or len(data) < 20:
                continue

            data["RSI"]    = ta.rsi(data["Close"], length=14)
            data["SMA50"]  = ta.sma(data["Close"], length=50)
            data["SMA200"] = ta.sma(data["Close"], length=200)

            price  = data["Close"].iloc[-1]
            rsi    = data["RSI"].iloc[-1]
            sma50  = data["SMA50"].iloc[-1]
            sma200 = data["SMA200"].iloc[-1]

            results.append({
                "Ticker":   ticker,
                "Name":     name,
                "Exchange": exch,
                "Category": cat,
                "Price":    round(price, 2),
                "RSI":      round(rsi,   1),
                "1D%":      pct_change(data, 1),
                "1W%":      pct_change(data, 5),
                "1M%":      pct_change(data, 21),
                "3M%":      pct_change(data, 63),
                "6M%":      pct_change(data, 126),
                "1Y%":      pct_change(data, 252),
                "Signal":   rsi_signal(rsi),
                "Trend":    trend_label(price, sma50, sma200),
                "DEGIRO":   degiro,
                "ISIN":     isin,
                "_data":    data,
            })
        except Exception:
            continue
    return results

# ═══════════════════════════════════════════════════════════════
#  CHART
# ═══════════════════════════════════════════════════════════════

def draw_chart(r):
    data = r["_data"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

    ax1.plot(data.index, data["Close"],  color="steelblue", linewidth=1.5, label="Price")
    ax1.plot(data.index, data["SMA50"],  color="orange",    linewidth=1,   linestyle="--", label="SMA 50")
    ax1.plot(data.index, data["SMA200"], color="red",       linewidth=1,   linestyle="--", label="SMA 200")
    ax1.set_title(f"{r['Ticker']} — {r['Name']}  |  Price & RSI (1 year)", fontsize=13)
    ax1.set_ylabel("Price")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2.plot(data.index, data["RSI"], color="orange", linewidth=1.5, label="RSI (14)")
    ax2.axhline(70, color="red",   linestyle="--", linewidth=1, label="Overbought (70)")
    ax2.axhline(30, color="green", linestyle="--", linewidth=1, label="Oversold (30)")
    ax2.axhline(50, color="gray",  linestyle=":",  linewidth=0.8)
    ax2.fill_between(data.index, 70, 100, color="red",   alpha=0.07)
    ax2.fill_between(data.index, 0,  30,  color="green", alpha=0.07)
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════
#  TABLE + CHART SECTION
#  Tick the checkbox on any row to show its chart below
# ═══════════════════════════════════════════════════════════════

def show_section(results, key_prefix=""):
    if not results:
        st.info("No data available.")
        return

    # Build display df with a Select checkbox column first
    rows = [{k: v for k, v in r.items() if k != "_data"} for r in results]
    df   = pd.DataFrame(rows)
    df.insert(0, "Select", False)   # checkbox column at the front

    st.caption("✔ Tick a row to view its chart")

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn("📊", width="small"),
            "1D%":    st.column_config.NumberColumn(format="%.1f%%"),
            "1W%":    st.column_config.NumberColumn(format="%.1f%%"),
            "1M%":    st.column_config.NumberColumn(format="%.1f%%"),
            "3M%":    st.column_config.NumberColumn(format="%.1f%%"),
            "6M%":    st.column_config.NumberColumn(format="%.1f%%"),
            "1Y%":    st.column_config.NumberColumn(format="%.1f%%"),
            "RSI":    st.column_config.NumberColumn(format="%.1f"),
        },
        disabled=[c for c in df.columns if c != "Select"],
        key=f"{key_prefix}_table",
    )

    # Find which rows are ticked
    selected_tickers = edited[edited["Select"] == True]["Ticker"].tolist()

    for ticker in selected_tickers:
        match = next((r for r in results if r["Ticker"] == ticker), None)
        if match:
            st.markdown("---")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Ticker",  match["Ticker"])
            c2.metric("Price",   f"{match['Price']:.2f}")
            c3.metric("RSI",     f"{match['RSI']:.1f}")
            c4.metric("1M%",     f"{match['1M%']:+.1f}%")
            c5.metric("Signal",  match["Signal"])
            draw_chart(match)

# ═══════════════════════════════════════════════════════════════
#  LOAD ALL DATA
# ═══════════════════════════════════════════════════════════════

with st.spinner("Fetching live market data..."):
    all_results = fetch_all()

if not all_results:
    st.error("Could not fetch data — check your internet connection.")
    st.stop()

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR — navigation + context filters
# ═══════════════════════════════════════════════════════════════

st.sidebar.title("🔍 Navigate")

page = st.sidebar.radio("", [
    "🏆 Top & Bottom performers",
    "📋 Browse by category",
    "⚠ Signals & Alerts",
])

st.sidebar.markdown("---")

# Context-sensitive filters — different controls per page
if page == "🏆 Top & Bottom performers":
    sort_by  = st.sidebar.selectbox("Rank by", ["1M%", "1W%", "1D%", "3M%", "6M%", "1Y%"])
    n        = st.sidebar.slider("ETFs to show", 3, 10, 5)

elif page == "📋 Browse by category":
    categories   = ["All ETFs"] + sorted(set(r["Category"] for r in all_results))
    selected_cat = st.sidebar.selectbox("Category", categories)

elif page == "⚠ Signals & Alerts":
    rsi_ob = st.sidebar.slider("Overbought above", 65, 85, 70)
    rsi_os = st.sidebar.slider("Oversold below",   15, 35, 30)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(all_results)} ETFs loaded**")
st.sidebar.markdown("*Refreshes every 30 min*")

# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — TOP & BOTTOM PERFORMERS
# ═══════════════════════════════════════════════════════════════

if page == "🏆 Top & Bottom performers":

    st.subheader(f"🏆 Top & Bottom Performers — by {sort_by}")

    ranked = sorted(all_results, key=lambda r: r[sort_by], reverse=True)

    st.markdown(f"#### 📈 Top {n}")
    show_section(ranked[:n], key_prefix="top")

    st.markdown("---")

    st.markdown(f"#### 📉 Bottom {n}")
    show_section(ranked[-n:], key_prefix="bottom")

# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — BROWSE BY CATEGORY
# ═══════════════════════════════════════════════════════════════

elif page == "📋 Browse by category":

    filtered = all_results if selected_cat == "All ETFs" \
               else [r for r in all_results if r["Category"] == selected_cat]

    st.subheader(f"📋 {selected_cat}  —  {len(filtered)} ETF(s)")
    show_section(filtered, key_prefix="browse")

# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — SIGNALS & ALERTS
# ═══════════════════════════════════════════════════════════════

elif page == "⚠ Signals & Alerts":

    st.subheader("⚠ Signals & Alerts")

    overbought = [r for r in all_results if r["RSI"] >= rsi_ob]
    oversold   = [r for r in all_results if r["RSI"] <= rsi_os]
    uptrend    = [r for r in all_results if "Uptrend"   in r["Trend"]]
    downtrend  = [r for r in all_results if "Downtrend" in r["Trend"]]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Overbought", len(overbought), help=f"RSI ≥ {rsi_ob}")
    c2.metric("🟢 Oversold",   len(oversold),   help=f"RSI ≤ {rsi_os}")
    c3.metric("📈 Uptrend",    len(uptrend))
    c4.metric("📉 Downtrend",  len(downtrend))

    st.markdown("---")

    if overbought:
        st.markdown(f"#### 🔴 Overbought (RSI ≥ {rsi_ob})")
        show_section(overbought, key_prefix="ob")
        st.markdown("---")

    if oversold:
        st.markdown(f"#### 🟢 Oversold (RSI ≤ {rsi_os})")
        show_section(oversold, key_prefix="os")
        st.markdown("---")

    if not overbought and not oversold:
        st.success("✓ No extreme RSI signals right now.")
        st.markdown("---")

    if uptrend:
        st.markdown("#### 📈 Confirmed uptrend")
        show_section(uptrend, key_prefix="up")

    if downtrend:
        st.markdown("#### 📉 Confirmed downtrend")
        show_section(downtrend, key_prefix="dn")