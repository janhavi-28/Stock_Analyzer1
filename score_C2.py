# ==========================================================
# CATEGORY 2 : Profitability & Returns (25 Points)
# Final Corrected Version (Working with Crore Data)
# ==========================================================

import json
import sys
import os

# Import functions from Category 1 engine
from score_C1 import (
    get_stock_data,
    merge_dummy,
    pretty
)

# ----------------------------------------------------------
# Dummy Data for Category 2 (all values in CRORE)
# ----------------------------------------------------------
DUMMY_CATEGORY2 = {
    "TATASTEEL.NS": {
        "shareholders_equity_manual": 95932,    # crore

        "shareholders_equity_5yr": [
            95932,    # FY25
            101200,   # FY24
            133467,   # FY23
            151208,   # FY22
            87860     # FY21
        ],

        "total_assets": 2800000,                # crore (2.8 trillion)
        "current_liabilities": 89760            # crore
    }
}


# ----------------------------------------------------------
# Merge Dummy Values for Category 2
# ----------------------------------------------------------
def merge_dummy_c2(symbol, data):
    dummy = DUMMY_CATEGORY2.get(symbol)
    if not dummy:
        return data

    for key, value in dummy.items():
        if data.get(key) is None:
            data[key] = value

    return data


# ----------------------------------------------------------
# Safe Float Conversion
# ----------------------------------------------------------
def safe(x):
    try:
        return float(x)
    except:
        return 0


# ----------------------------------------------------------
# CATEGORY 2 SCORING ENGINE (Final Corrected Version)
# ----------------------------------------------------------
def score_category_2(d):

    # -------------------------------
    # 2.1 ROE (Latest Year)
    # ROE = Net Profit / Equity * 100
    # -------------------------------
    npf = safe(d.get("net_profit") or d.get("net_profit_manual"))
    equity = safe(d.get("shareholders_equity") or d.get("shareholders_equity_manual"))

    roe = (npf / equity * 100) if equity else 0

    roe_score = (
        10 if roe >= 25 else
        8 if roe >= 20 else
        6 if roe >= 15 else
        4 if roe >= 10 else
        2 if roe >= 5 else
        0
    )

    # -------------------------------
    # 2.2 ROCE
    # ROCE = EBIT / Capital Employed * 100
    # Capital Employed = Total Assets - Current Liabilities
    # -------------------------------
    ebit = safe(d.get("ebit") or d.get("ebit_manual"))
    assets = safe(d.get("total_assets"))
    liab = safe(d.get("current_liabilities"))

    capital_employed = assets - liab if assets and liab else 0
    roce = (ebit / capital_employed * 100) if capital_employed else 0

    roce_score = (
        8 if roce >= 25 else
        6 if roce >= 20 else
        4 if roce >= 15 else
        2 if roce >= 10 else
        0
    )

    # -------------------------------
    # 2.3 ROE Consistency (5-Year)
    # Count years with ROE > 15%
    # -------------------------------
    np5 = d.get("net_profit_5yr") or []
    eq5 = d.get("shareholders_equity_5yr") or []

    roe_years = []
    for np_i, eq_i in zip(np5, eq5):
        eq_i = safe(eq_i)
        np_i = safe(np_i)
        roe_years.append((np_i / eq_i * 100) if eq_i else 0)

    good_years = sum(r > 15 for r in roe_years)

    roe_consistency_score = (
        7 if good_years == 5 else
        5 if good_years == 4 else
        3 if good_years == 3 else
        1 if good_years == 2 else
        0
    )

    # -------------------------------
    # Total Category 2 Score
    # -------------------------------
    total = roe_score + roce_score + roe_consistency_score

    return {
        "ROE % (Latest)": round(roe, 2),
        "ROE Score": roe_score,

        "ROCE % (Latest)": round(roce, 2),
        "ROCE Score": roce_score,

        "ROE > 15% Years (5yr)": good_years,
        "ROE Consistency Score": roe_consistency_score,

        "Total Category 2 Score": total
    }


# ==========================================================
# MAIN (Run: python score_C2.py SYMBOL)
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python score_C2.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    # Step 1 — Yahoo data in CRORE
    data = get_stock_data(symbol)

    # Step 2 — Merge Category 1 dummy (revenue, NP, EPS, EBIT)
    data = merge_dummy(symbol, data)

    # Step 3 — Merge Category 2 dummy (equity, assets, liabilities)
    data = merge_dummy_c2(symbol, data)

    # Step 4 — Score Category 2
    score2 = score_category_2(data)

    # Step 5 — Display Output
    print("\n=== CATEGORY 2 SCORE ===")
    pretty(score2)

    # Step 6 — Save JSON output
    outfile = f"{symbol}_CAT2_SCORED.json"
    json.dump(score2, open(outfile, "w"), indent=2)
    print(f"✔ Saved: {outfile}")
