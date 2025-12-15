import yfinance as yf
import json
import sys
import os
import datetime

# ==========================================================
# Pretty Table
# ==========================================================
def pretty(data):
    print("\n" + "-" * 65)
    print(f"{'FIELD':35} | VALUE")
    print("-" * 65)
    for k, v in data.items():
        print(f"{k:35} | {v}")
    print("-" * 65 + "\n")


# ==========================================================
# Fetch Yahoo Finance (cached daily)
# ==========================================================
def get_stock_data(symbol):
    symbol = symbol.upper()
    cache = f"{symbol}_YAHOO.json"
    today = str(datetime.date.today())

    if os.path.exists(cache):
        cached = json.load(open(cache))
        if cached.get("last_updated") == today:
            print("✔ Using today's cached Yahoo data.")
            return cached

    print("Fetching live Yahoo Finance data...")
    t = yf.Ticker(symbol)
    info = t.info

    data = {
        "symbol": symbol,
        "last_updated": today,
        "current_price": info.get("currentPrice"),
        "eps_trailing": info.get("trailingEps"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "market_cap": info.get("marketCap"),
        "total_debt": info.get("totalDebt"),
        "cash": info.get("totalCash")
    }

    json.dump(data, open(cache, "w"), indent=2)
    print("✔ Yahoo data fetched & cached.")
    return data


# ==========================================================
# Dummy Valuation Data
# ==========================================================
DUMMY_VALUATION = {
    "TATASTEEL.NS": {
        "industry_pe": 9.5,
        "eps_cagr": 12.0,           # %
        "wacc": 0.10,
        "terminal_growth": 0.04,
        "fcf_forecast": [22000, 24000, 26000, 28000, 30000]  # crore
    }
}


def merge_dummy(symbol, data):
    dummy = DUMMY_VALUATION.get(symbol)
    if not dummy:
        return data

    for k, v in dummy.items():
        if data.get(k) is None:
            data[k] = v

    return data


# ==========================================================
# CATEGORY 5 : VALUATION (10 POINTS)
# ==========================================================
def score_category_5(d):

    # -----------------------------
    # 5.1 P/E vs Industry
    # -----------------------------
    price = d.get("current_price")
    eps = d.get("eps_trailing")
    industry_pe = d.get("industry_pe")

    pe = price / eps if price and eps else None
    diff_pct = ((pe - industry_pe) / industry_pe * 100) if pe and industry_pe else None

    if diff_pct is None:
        pe_score = 0
    elif diff_pct <= -20:
        pe_score = 3
    elif diff_pct <= -10:
        pe_score = 2
    elif abs(diff_pct) <= 10:
        pe_score = 1
    elif diff_pct <= 30:
        pe_score = 0.5
    else:
        pe_score = 0

    # -----------------------------
    # 5.2 PEG Ratio
    # -----------------------------
    eps_cagr = d.get("eps_cagr")
    peg = pe / eps_cagr if pe and eps_cagr else None

    if peg is None:
        peg_score = 0
    elif peg < 0.7:
        peg_score = 3
    elif peg < 1.0:
        peg_score = 2
    elif peg < 1.3:
        peg_score = 1
    elif peg < 2.0:
        peg_score = 0.5
    else:
        peg_score = 0

    # -----------------------------
    # 5.3 DCF Intrinsic Value
    # -----------------------------
    fcf_list = d.get("fcf_forecast")
    wacc = d.get("wacc")
    g = d.get("terminal_growth")
    shares = d.get("shares_outstanding")
    cash = d.get("cash") or 0
    debt = d.get("total_debt") or 0
    cmp = price

    iv = None
    iv_per_share = None
    mos = None

    if fcf_list and wacc and g and shares:
        discounted = 0
        for t, fcf in enumerate(fcf_list, start=1):
            discounted += fcf / ((1 + wacc) ** t)

        terminal = (fcf_list[-1] * (1 + g)) / (wacc - g)
        terminal /= ((1 + wacc) ** len(fcf_list))

        iv = discounted + terminal  # in crore

        iv_rupees = iv * 1e7
        cash_rupees = cash * 1e7
        debt_rupees = debt * 1e7

        iv_per_share = (iv_rupees + cash_rupees - debt_rupees) / shares
        mos = ((iv_per_share - cmp) / iv_per_share) * 100

    if mos is None:
        dcf_score = 0
    elif mos >= 30:
        dcf_score = 4
    elif mos >= 10:
        dcf_score = 3
    elif mos >= -10:
        dcf_score = 2
    elif mos >= -30:
        dcf_score = 1
    else:
        dcf_score = 0

    total = pe_score + peg_score + dcf_score

    return {
        "P/E": round(pe, 2) if pe else None,
        "Industry P/E": industry_pe,
        "P/E Difference %": round(diff_pct, 2) if diff_pct else None,
        "P/E Score": pe_score,

        "PEG": round(peg, 2) if peg else None,
        "PEG Score": peg_score,

        "Intrinsic Value / Share": round(iv_per_share, 2) if iv_per_share else None,
        "Margin of Safety %": round(mos, 2) if mos else None,
        "DCF Score": dcf_score,

        "Total Category 5 Score": total
    }


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python score_C5.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    data = get_stock_data(symbol)
    data = merge_dummy(symbol, data)

    print("\n=== FINAL DATA (Yahoo + Dummy Valuation) ===")
    pretty(data)

    result = score_category_5(data)

    print("\n=== CATEGORY 5 SCORE ===")
    pretty(result)

    json.dump(result, open(f"{symbol}_CAT5_SCORED.json", "w"), indent=2)
    print(f"✔ Scoring saved to {symbol}_CAT5_SCORED.json")
