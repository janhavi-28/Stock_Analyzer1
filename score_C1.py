import yfinance as yf
import json
import sys
import os
import datetime

# ==========================================================
# Pretty Table
# ==========================================================
def pretty(data):
    print("\n" + "-" * 55)
    print(f"{'FIELD':25} | VALUE")
    print("-" * 55)
    for key, value in data.items():
        print(f"{key:25} | {value}")
    print("-" * 55 + "\n")


# ==========================================================
# Convert rupees → crore
# ==========================================================
def to_crore(x):
    try:
        return round(float(x) / 1e7, 3)
    except:
        return None


# ==========================================================
# Fetch Yahoo Finance + Convert ALL financial numbers to crore
# ==========================================================
def get_stock_data(symbol):
    symbol = symbol.upper()
    cache_file = f"{symbol}_YAHOO.json"
    today = str(datetime.date.today())

    # -----------------------------
    # Use cached data (today only)
    # -----------------------------
    if os.path.exists(cache_file):
        cached = json.load(open(cache_file))
        if cached.get("last_updated") == today:
            print("✔ Using today's cached Yahoo data.")
            return cached

    # -----------------------------
    # Fetch Live Yahoo Data
    # -----------------------------
    print("Fetching live Yahoo Finance data...")
    t = yf.Ticker(symbol)
    info = t.info

    data = {
        "symbol": symbol,
        "company_name": info.get("longName"),
        "current_price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "eps_trailing": info.get("trailingEps"),
        "last_updated": today
    }

    # -----------------------------
    # TTM Revenue (converted to crore)
    # -----------------------------
    try:
        qfin = t.quarterly_financials
        rev_quarters = qfin.loc["Total Revenue"].tolist()
        ttm_revenue_rupees = sum(rev_quarters[:4])
        data["revenue"] = to_crore(ttm_revenue_rupees)
    except:
        data["revenue"] = None

    # -----------------------------
    # Annual EBIT & Net Profit (converted to crore)
    # -----------------------------
    try:
        fin = t.financials
        data["ebit"] = to_crore(fin.loc["Operating Income"].iloc[0])
        data["net_profit"] = to_crore(fin.loc["Net Income"].iloc[0])
    except:
        pass

    # -----------------------------
    # Balance Sheet (converted to crore)
    # -----------------------------
    try:
        bs = t.balance_sheet
        data["total_assets"] = to_crore(bs.loc["Total Assets"].iloc[0])
        data["current_liabilities"] = to_crore(bs.loc["Total Current Liabilities"].iloc[0])
        data["cash_and_cash_equivalents"] = to_crore(bs.loc["Cash And Cash Equivalents"].iloc[0])
    except:
        pass

    # -----------------------------
    # Cash Flow (converted to crore)
    # -----------------------------
    try:
        cf = t.cashflow
        data["operating_cash_flow"] = to_crore(cf.loc["Operating Cash Flow"].iloc[0])
        data["capital_expenditure"] = to_crore(cf.loc["Capital Expenditure"].iloc[0])
    except:
        pass

    # Save new cache
    json.dump(data, open(cache_file, "w"), indent=2)
    print("✔ Live data fetched & saved.")

    return data


# ==========================================================
# Dummy Data (Crore)
# ==========================================================
DUMMY = {
    "TATASTEEL.NS": {
        "revenue_5yr": [218543, 229171, 243353, 243959, 156294],
        "net_profit_5yr": [3174, -4910, 8075, 41749, 1174],
        "eps_5yr": [2.74, -3.55, 7.17, 32.88, 6.26],

        # Manual numbers in CRORE
        "ebit_manual": 25298,
        "net_profit_manual": 3174,
        "revenue_manual": 218543
    }
}


# Merge dummy where Yahoo fails
def merge_dummy(symbol, data):
    dummy = DUMMY.get(symbol)
    if not dummy:
        return data

    for key, value in dummy.items():
        if data.get(key) is None:
            data[key] = value
    return data


# ==========================================================
# CATEGORY 1 Scoring Engine
# ==========================================================
def score_category_1(d):

    rev = d.get("revenue_5yr")
    eps = d.get("eps_5yr")

    if not rev or not eps:
        return {"error": "Missing 5-year revenue/EPS data"}

    # -----------------------------
    # Revenue CAGR
    # -----------------------------
    cagr = ((rev[0] / rev[-1]) ** 0.25 - 1) * 100
    cagr_score = (
        8 if cagr >= 20 else
        6 if cagr >= 15 else
        4 if cagr >= 10 else
        2 if cagr >= 5 else
        0
    )

    # -----------------------------
    # Consistency
    # -----------------------------
    pos_years = sum(rev[i] > rev[i + 1] for i in range(4))

    # -----------------------------
    # Margins using CRORE values
    # -----------------------------
    revenue = d.get("revenue") or d.get("revenue_manual")
    ebit = d.get("ebit") or d.get("ebit_manual")
    npf = d.get("net_profit") or d.get("net_profit_manual")

    opm = (ebit / revenue) * 100
    npm = (npf / revenue) * 100

    opm_score = (
        4 if opm >= 20 else
        3 if opm >= 15 else
        2 if opm >= 10 else
        1 if opm >= 5 else
        0
    )

    npm_score = (
        4 if npm >= 15 else
        3 if npm >= 10 else
        2 if npm >= 5 else
        1 if npm >= 2 else
        0
    )

    # -----------------------------
    # EPS CAGR
    # -----------------------------
    eps_cagr = ((eps[0] / eps[-1]) ** 0.25 - 1) * 100
    eps_score = (
        5 if eps_cagr >= 25 else
        4 if eps_cagr >= 20 else
        3 if eps_cagr >= 15 else
        2 if eps_cagr >= 10 else
        1 if eps_cagr >= 5 else
        0
    )

    total = cagr_score + pos_years + opm_score + npm_score + eps_score

    return {
        "Revenue CAGR %": round(cagr, 2),
        "Revenue CAGR Score": cagr_score,

        "Positive Revenue Years": pos_years,

        "OPM %": round(opm, 2),
        "OPM Score": opm_score,

        "NPM %": round(npm, 2),
        "NPM Score": npm_score,

        "EPS CAGR %": round(eps_cagr, 2),
        "EPS Score": eps_score,

        "Total Category 1 Score": total
    }


# ==========================================================
# MAIN PROGRAM
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python score_C1.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    data = get_stock_data(symbol)
    data = merge_dummy(symbol, data)

    print("\n=== FINAL DATA (Yahoo + Dummy) ===")
    pretty(data)

    score_output = score_category_1(data)

    print("\n=== CATEGORY 1 SCORE ===")
    pretty(score_output)

    json.dump(score_output, open(f"{symbol}_CAT1_SCORED.json", "w"), indent=2)
    print(f"✔ Scoring saved to {symbol}_CAT1_SCORED.json")