import yfinance as yf
import json
import sys
import os
import datetime

# ==========================================================
# Pretty Table
# ==========================================================
def pretty(data):
    print("\n" + "-" * 60)
    print(f"{'FIELD':30} | VALUE")
    print("-" * 60)
    for k, v in data.items():
        print(f"{k:30} | {v}")
    print("-" * 60 + "\n")


# ==========================================================
# Fetch Yahoo Finance (cached daily)
# NOTE: Yahoo does NOT give promoter / pledge / dividend years
# We keep this for consistency with Category 3 pipeline
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

    data = {
        "symbol": symbol,
        "last_updated": today
    }

    # Minimal Yahoo fields (kept for pipeline consistency)
    try:
        info = t.info
        data["company_name"] = info.get("longName")
    except:
        pass

    json.dump(data, open(cache, "w"), indent=2)
    print("✔ Yahoo data fetched & cached.")
    return data


# ==========================================================
# Dummy Management Data (to be replaced by Screener scrape)
# ==========================================================
DUMMY_MGMT = {
    "TATASTEEL.NS": {
        "promoter_holding_pct": 52.4,   # %
        "pledged_shares_pct": 0.0,      # %
        "dividend_paid_years": 5        # out of last 5
    }
}


def merge_dummy(symbol, data):
    dummy = DUMMY_MGMT.get(symbol)
    if not dummy:
        return data

    for k, v in dummy.items():
        if data.get(k) is None:
            data[k] = v

    return data


# ==========================================================
# CATEGORY 4 : MANAGEMENT QUALITY (15 POINTS)
# ==========================================================
def score_category_4(d):

    # --------------------------------------------------
    # 4.1 Promoter Holding (7 pts)
    # --------------------------------------------------
    ph = d.get("promoter_holding_pct")

    if ph is None:
        ph_score = 0
    elif 40 <= ph <= 65:
        ph_score = 7
    elif 30 <= ph < 40 or 65 < ph <= 75:
        ph_score = 5
    elif 25 <= ph < 30:
        ph_score = 3
    else:
        ph_score = 1

    # --------------------------------------------------
    # 4.2 Pledged Shares (5 pts)
    # --------------------------------------------------
    pledged = d.get("pledged_shares_pct")

    if pledged is None:
        pledged_score = 0
    elif pledged == 0:
        pledged_score = 5
    elif pledged < 10:
        pledged_score = 4
    elif pledged < 25:
        pledged_score = 2
    elif pledged < 50:
        pledged_score = 1
    else:
        pledged_score = 0

    # --------------------------------------------------
    # 4.3 Dividend Consistency (3 pts)
    # --------------------------------------------------
    div_years = d.get("dividend_paid_years")

    if div_years is None:
        div_score = 0
    elif div_years == 5:
        div_score = 3
    elif div_years == 4:
        div_score = 2
    elif div_years == 3:
        div_score = 1
    else:
        div_score = 0

    total = ph_score + pledged_score + div_score

    return {
        "Promoter Holding %": ph,
        "Promoter Holding Score": ph_score,

        "Pledged Shares %": pledged,
        "Pledged Shares Score": pledged_score,

        "Dividend Paid (Last 5 Years)": div_years,
        "Dividend Consistency Score": div_score,

        "Total Category 4 Score": total
    }


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python score_C4.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    data = get_stock_data(symbol)
    data = merge_dummy(symbol, data)

    print("\n=== FINAL DATA (Yahoo + Dummy Management) ===")
    pretty(data)

    result = score_category_4(data)

    print("\n=== CATEGORY 4 SCORE ===")
    pretty(result)

    json.dump(result, open(f"{symbol}_CAT4_SCORED.json", "w"), indent=2)
    print(f"✔ Scoring saved to {symbol}_CAT4_SCORED.json")
