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
    for k, v in data.items():
        print(f"{k:25} | {v}")
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
# Fetch Yahoo Finance (CRORE, cached daily)
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
    data = {"symbol": symbol, "last_updated": today}

    try:
        fin = t.financials
        data["ebit"] = to_crore(fin.loc["Operating Income"].iloc[0])
        data["net_profit"] = to_crore(fin.loc["Net Income"].iloc[0])
        data["interest_expense"] = to_crore(fin.loc["Interest Expense"].iloc[0])
    except:
        pass

    try:
        bs = t.balance_sheet
        data["total_assets"] = to_crore(bs.loc["Total Assets"].iloc[0])
        data["current_liabilities"] = to_crore(bs.loc["Total Current Liabilities"].iloc[0])
        data["shareholders_equity"] = to_crore(bs.loc["Total Stockholder Equity"].iloc[0])
    except:
        pass

    try:
        cf = t.cashflow
        data["operating_cash_flow"] = to_crore(cf.loc["Operating Cash Flow"].iloc[0])
        data["capital_expenditure"] = to_crore(cf.loc["Capital Expenditure"].iloc[0])
    except:
        pass

    json.dump(data, open(cache, "w"), indent=2)
    print("✔ Live data fetched & saved.")
    return data


# ==========================================================
# Dummy Data (CRORE) – future scraper replacement
# ==========================================================
DUMMY = {
    "TATASTEEL.NS": {
        "total_debt": 95643,
        "shareholders_equity": 95932,
        "current_assets": 66620,
        "current_liabilities": 89760,
        "interest_expense": 7341
    }
}



def merge_dummy(symbol, data):
    dummy = DUMMY.get(symbol)
    if not dummy:
        return data
    for k, v in dummy.items():
        if data.get(k) is None:
            data[k] = v
    return data


# ==========================================================
# CATEGORY 3 SCORING
# ==========================================================
def score_category_3(d):

    # 3.1 Debt-to-Equity
    debt = d.get("total_debt")
    equity = d.get("shareholders_equity")

    de = debt / equity if debt and equity else None

    if de is None:
        de_score = 0
    elif de < 0.3:
        de_score = 8
    elif de < 0.5:
        de_score = 6
    elif de < 1.0:
        de_score = 4
    elif de < 2.0:
        de_score = 2
    else:
        de_score = 0

    # 3.2 Interest Coverage
    ebit = d.get("ebit")
    interest = d.get("interest_expense")

    coverage = ebit / interest if ebit and interest else None

    if coverage is None:
        ic_score = 0
    elif coverage >= 8:
        ic_score = 7
    elif coverage >= 5:
        ic_score = 5
    elif coverage >= 3:
        ic_score = 3
    elif coverage >= 2:
        ic_score = 1
    else:
        ic_score = 0

    # 3.3 Current Ratio
    ca = d.get("current_assets")
    cl = d.get("current_liabilities")

    cr = ca / cl if ca and cl else None

    if cr is None:
        cr_score = 0
    elif cr >= 2:
        cr_score = 5
    elif cr >= 1.5:
        cr_score = 4
    elif cr >= 1.2:
        cr_score = 3
    elif cr >= 1:
        cr_score = 1
    else:
        cr_score = 0

    # 3.4 Free Cash Flow
    ocf = d.get("operating_cash_flow")
    capex = d.get("capital_expenditure")
    profit = d.get("net_profit")

    fcf = ocf - abs(capex) if ocf is not None and capex is not None else None
    fcf_pct = (fcf / profit) * 100 if fcf and profit else None

    if fcf is None:
        fcf_score = 0
    elif fcf > 0 and fcf_pct and fcf_pct > 80:
        fcf_score = 5
    elif fcf > 0 and fcf_pct and fcf_pct >= 50:
        fcf_score = 3
    elif fcf > 0:
        fcf_score = 2
    elif fcf <= 0 and fcf > -100:
        fcf_score = 1
    else:
        fcf_score = 0

    total = de_score + ic_score + cr_score + fcf_score

    return {
        "Debt-to-Equity": round(de, 2) if de else None,
        "Debt Level Score": de_score,

        "Interest Coverage": round(coverage, 2) if coverage else None,
        "Interest Coverage Score": ic_score,

        "Current Ratio": round(cr, 2) if cr else None,
        "Current Ratio Score": cr_score,

        "Free Cash Flow": round(fcf, 2) if fcf else None,
        "FCF % of Profit": round(fcf_pct, 2) if fcf_pct else None,
        "FCF Score": fcf_score,

        "Total Category 3 Score": total
    }


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python score_C3.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    data = get_stock_data(symbol)
    data = merge_dummy(symbol, data)

    print("\n=== FINAL DATA (Yahoo + Dummy) ===")
    pretty(data)

    result = score_category_3(data)

    print("\n=== CATEGORY 3 SCORE ===")
    pretty(result)

    json.dump(result, open(f"{symbol}_CAT3_SCORED.json", "w"), indent=2)
    print(f"✔ Scoring saved to {symbol}_CAT3_SCORED.json")
