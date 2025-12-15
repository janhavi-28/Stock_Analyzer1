import yfinance as yf


def get_yahoo_19_indicators(symbol: str) -> dict:
    """
    Fetch 19 core fundamental indicators for a given stock symbol using yfinance.

    Works for Indian stocks like 'TATASTEEL.NS', 'RELIANCE.NS', etc.
    """

    symbol = symbol.upper()
    ticker = yf.Ticker(symbol)

    data: dict[str, float | int | str | None] = {
        "symbol": symbol
    }

    # ---------- BASIC INFO ----------
    info = ticker.info

    data["company_name"] = info.get("longName")
    data["current_market_price"] = info.get("currentPrice")
    data["market_cap"] = info.get("marketCap")

    # ---------- SHARE DATA ----------
    data["shares_outstanding"] = info.get("sharesOutstanding")
    data["eps_trailing"] = info.get("trailingEps")
    data["dividend_per_share"] = info.get("dividendRate")

    # Helpers for statement rows
    def safe_row(df, row_name: str):
        try:
            return float(df.loc[row_name].iloc[0])
        except Exception:
            return None

    # ---------- INCOME STATEMENT ----------
    try:
        inc = ticker.financials  # annual income statement (DataFrame: rows = items, cols = years)
    except Exception:
        inc = None

    if inc is not None and not inc.empty:
        data["revenue"] = safe_row(inc, "Total Revenue")
        data["cogs"] = safe_row(inc, "Cost Of Revenue")
        data["operating_expenses"] = safe_row(inc, "Operating Expense")
        data["ebit"] = safe_row(inc, "Operating Income")  # EBIT proxy
        data["ebitda"] = safe_row(inc, "EBITDA")
        data["net_profit"] = safe_row(inc, "Net Income")
        data["interest_expense"] = safe_row(inc, "Interest Expense")
        data["tax_expense"] = safe_row(inc, "Tax Provision")
    else:
        data["revenue"] = None
        data["cogs"] = None
        data["operating_expenses"] = None
        data["ebit"] = None
        data["ebitda"] = None
        data["net_profit"] = None
        data["interest_expense"] = None
        data["tax_expense"] = None

    # ---------- BALANCE SHEET ----------
    try:
        bs = ticker.balance_sheet
    except Exception:
        bs = None

    if bs is not None and not bs.empty:
        data["total_assets"] = safe_row(bs, "Total Assets")
        data["cash_and_cash_equivalents"] = safe_row(bs, "Cash And Cash Equivalents")
    else:
        data["total_assets"] = None
        data["cash_and_cash_equivalents"] = None

    # ---------- CASH FLOW ----------
    try:
        cf = ticker.cashflow
    except Exception:
        cf = None

    if cf is not None and not cf.empty:
        data["operating_cash_flow"] = safe_row(cf, "Operating Cash Flow")
        data["capital_expenditure"] = safe_row(cf, "Capital Expenditure")
    else:
        data["operating_cash_flow"] = None
        data["capital_expenditure"] = None

    return data


# Simple tester
if __name__ == "__main__":
    # Example: Tata Steel on NSE
    symbol = "TATASTEEL.NS"
    result = get_yahoo_19_indicators(symbol)

    print("\n===== YAHOO 19 INDICATORS =====\n")
    for k, v in result.items():
        print(f"{k:25} : {v}")
