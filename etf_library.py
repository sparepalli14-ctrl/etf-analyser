# ═══════════════════════════════════════════════════════════════
#  ETF LIBRARY — single source of truth
#  Format: "TICKER": ("Name", "Exchange", "Category", "DEGIRO Name", "ISIN")
#
#  To add a new ETF, just add a new line here.
#  etf_analyzer.py picks it up automatically.
# ═══════════════════════════════════════════════════════════════

ETF_LIBRARY = {

    # ── Netherlands — AEX (Euronext Amsterdam) ──────────────────
    "IAEX.AS":  ("iShares AEX — Dutch top 25",       "Amsterdam",  "Netherlands",         "IAEX",  "IE00B02KXL92"),

    # ── Global broad (Amsterdam-listed, EUR denominated) ────────
    "IWDA.AS":  ("iShares MSCI World",                "Amsterdam",  "Global broad",        "IWDA",  "IE00B4L5Y983"),
    "VWRL.AS":  ("Vanguard FTSE All-World",           "Amsterdam",  "Global broad",        "VWCE",  "IE00BK5BQT80"),
    "CSPX.AS":  ("iShares Core S&P 500",              "Amsterdam",  "Global broad",        "CSPX",  "IE00B5BMR087"),
    "VHYL.AS":  ("Vanguard FTSE All-World High Div",  "Amsterdam",  "Europe broad",        "VHYL",  "IE00B8GKDB10"),

    # ── Europe broad ────────────────────────────────────────────
    "EXSA.DE":  ("iShares STOXX Europe 600",          "XETRA",      "Europe broad",        "EXSA",  "DE0002635307"),
    "VEUR.L":   ("Vanguard FTSE Developed Europe",    "London",     "Europe broad",        "VEUR",  "IE00B945VV12"),
    "IMEU.L":   ("iShares MSCI Europe",               "London",     "Europe broad",        "IMEU",  "IE00B4K48X80"),

    # ── Germany ─────────────────────────────────────────────────
    "EXS1.DE":  ("iShares Core DAX",                  "XETRA",      "Germany",             "EXS1",  "DE0005933931"),
    "DBXD.DE":  ("Xtrackers DAX",                     "XETRA",      "Germany",             "DBXD",  "LU0274211480"),

    # ── France ──────────────────────────────────────────────────
    "C40.PA":   ("Amundi CAC 40",                     "Paris",      "France",              "C40",   "FR0010468983"),
    "CW8.PA":   ("Amundi MSCI World",                 "Paris",      "France",              "CW8",   "LU1681043599"),

    # ── UK ──────────────────────────────────────────────────────
    "ISF.L":    ("iShares FTSE 100",                  "London",     "UK broad",            "ISF",   "IE0005042456"),
    "VMID.L":   ("Vanguard FTSE 250",                 "London",     "UK broad",            "VMID",  "IE00BKX55S42"),
    "IUKD.L":   ("iShares UK Dividend",               "London",     "UK dividend",         "IUKD",  "IE00B0M63060"),

    # ── Sectors ─────────────────────────────────────────────────
    "EXH1.DE":  ("STOXX 600 Healthcare",              "XETRA",      "Sector — healthcare", "EXH1",  "DE000A0Q4R36"),
    "EXV1.DE":  ("STOXX 600 Technology",              "XETRA",      "Sector — tech",       "EXV1",  "DE000A0H08E0"),
    "EXV6.DE":  ("STOXX 600 Banks",                   "XETRA",      "Sector — banks",      "EXV6",  "DE000A0H08P6"),
    "EXV8.DE":  ("STOXX 600 Energy",                  "XETRA",      "Sector — energy",     "EXV8",  "DE000A0H08R2"),
    "INRG.L":   ("iShares Global Clean Energy",       "London",     "Sector — energy",     "INRG",  "IE00B1XNHC34"),

    # ── Emerging markets ────────────────────────────────────────
    "EMIM.AS":  ("iShares Core MSCI Emerging Mkts",   "Amsterdam",  "Emerging markets",    "EMIM",  "IE00BKM4GZ66"),
    "XMME.DE":  ("Xtrackers MSCI Emerging Markets",   "XETRA",      "Emerging markets",    "XMME",  "IE00BTJRMP35"),
    "AEEM.PA":  ("Amundi MSCI Emerging Markets",       "Paris",      "Emerging markets",    "AEEM",  "LU1681045370"),

    # ── US tech ─────────────────────────────────────────────────
    "PANX.PA":  ("Amundi NASDAQ 100",                  "Paris",      "US tech",             "PANX",  "LU1681038243"),

    # ── Small cap ───────────────────────────────────────────────
    "WSML.L":   ("iShares MSCI World Small Cap",       "London",     "Small cap",           "WSML",  "IE00BF4RFH31"),

    # ── Bonds ───────────────────────────────────────────────────
    "EUNA.AS":  ("iShares Euro Govt Bond",             "Amsterdam",  "Bonds",               "EUNA",  "IE00B4WXJJ64"),
    "IEAG.L":   ("iShares Euro Aggregate Bond",        "London",     "Bonds",               "IEAG",  "IE00B3DKXQ41"),

    # ── Commodities ─────────────────────────────────────────────
    "SGLD.L":   ("iShares Physical Gold",              "London",     "Commodities",         "SGLD",  "IE00B4ND3602"),
}