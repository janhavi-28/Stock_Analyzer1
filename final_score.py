import json
import sys
import os

# ==========================================================
# Pretty Final Score Sheet
# ==========================================================
def print_final_score(sheet):
    print("\n==== FINAL SCORE SHEET ====\n")

    print(f"Category 1: Business Quality & Growth     {sheet['cat1']:>5} / 25")
    print(f"Category 2: Profitability & Returns       {sheet['cat2']:>5} / 25")
    print(f"Category 3: Financial Health & Safety     {sheet['cat3']:>5} / 25")
    print(f"Category 4: Management Quality            {sheet['cat4']:>5} / 15")
    print(f"Category 5: Valuation                     {sheet['cat5']:>5} / 10")

    print("\n==========================================")
    print(f"TOTAL SCORE: {sheet['total']:>5} / 100\n")


# ==========================================================
# Safe JSON Loader
# ==========================================================
def load_score(file, key):
    if not os.path.exists(file):
        print(f"⚠ Missing file: {file}")
        return 0

    try:
        data = json.load(open(file))
        return data.get(key, 0)
    except Exception as e:
        print(f"⚠ Error reading {file}: {e}")
        return 0


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python final_score.py SYMBOL")
        sys.exit()

    symbol = sys.argv[1].upper()

    # --------------------------------------------------
    # Load category scores
    # --------------------------------------------------
    cat1_score = load_score(f"{symbol}_CAT1_SCORED.json", "Total Category 1 Score")
    cat2_score = load_score(f"{symbol}_CAT2_SCORED.json", "Total Category 2 Score")
    cat3_score = load_score(f"{symbol}_CAT3_SCORED.json", "Total Category 3 Score")
    cat4_score = load_score(f"{symbol}_CAT4_SCORED.json", "Total Category 4 Score")
    cat5_score = load_score(f"{symbol}_CAT5_SCORED.json", "Total Category 5 Score")

    total_score = (
        cat1_score +
        cat2_score +
        cat3_score +
        cat4_score +
        cat5_score
    )

    final_sheet = {
        "symbol": symbol,
        "cat1": cat1_score,
        "cat2": cat2_score,
        "cat3": cat3_score,
        "cat4": cat4_score,
        "cat5": cat5_score,
        "total": total_score
    }

    print_final_score(final_sheet)

    json.dump(
        final_sheet,
        open(f"{symbol}_FINAL_SCORE.json", "w"),
        indent=2
    )

    print(f"✔ Final score saved to {symbol}_FINAL_SCORE.json")
