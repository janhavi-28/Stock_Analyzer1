import streamlit as st
import json
import subprocess
import os

st.set_page_config(page_title="InvestSmart – Stock Analyzer", layout="wide")

# ------------------------------
# CSS (HTML-like styling)
# ------------------------------
st.markdown("""
<style>
body {
    background-color: #f7fafc;
}
.hero {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 50px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}
.hero-score {
    font-size: 90px;
    font-weight: 700;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.05);
}
.verdict {
    background: linear-gradient(135deg, #48bb78, #38a169);
    padding: 40px;
    border-radius: 20px;
    color: white;
    text-align: center;
}
.metric {
    font-size: 40px;
    font-weight: 700;
    color: #667eea;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Helpers
# ------------------------------
def run(script, symbol):
    subprocess.run(["python", script, symbol], check=True)

def load_json(file):
    if not os.path.exists(file):
        return {}
    return json.load(open(file))

# ------------------------------
# Navbar
# ------------------------------
st.markdown("## 📊 InvestSmart – Stock Analyzer")

symbol = st.text_input("Enter stock symbol (Yahoo format)", "TATASTEEL.NS")

if st.button("Analyze"):

    with st.spinner("Running full analysis…"):
        run("score_C1.py", symbol)
        run("score_C2.py", symbol)
        run("score_C3.py", symbol)
        run("score_C4.py", symbol)
        run("score_C5.py", symbol)
        run("final_score.py", symbol)

    final = load_json(f"{symbol}_FINAL_SCORE.json")

    # ------------------------------
    # HERO SCORE
    # ------------------------------
    st.markdown(f"""
    <div class="hero">
        <div style="opacity:0.9; letter-spacing:1px;">{symbol}</div>
        <div class="hero-score">{final['total']} / 100</div>
        <div style="font-size:20px;">
            Business • Financials • Management • Valuation
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------
    # CATEGORY CARDS
    # ------------------------------
    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        ("🏢 Business", final["cat1"], 25),
        ("💰 Profitability", final["cat2"], 25),
        ("🏥 Financial", final["cat3"], 25),
        ("👔 Management", final["cat4"], 15),
        ("📊 Valuation", final["cat5"], 10),
    ]

    for col, (name, score, maxv) in zip([c1,c2,c3,c4,c5], cards):
        with col:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.markdown(f"<div class='metric'>{score}/{maxv}</div>", unsafe_allow_html=True)
            st.progress(score / maxv)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # ------------------------------
    # DETAILS (Expandable)
    # ------------------------------
    with st.expander("🏢 Business Quality – Details"):
        st.write(load_json(f"{symbol}_CAT1_SCORED.json"))

    with st.expander("💰 Profitability – Details"):
        st.write(load_json(f"{symbol}_CAT2_SCORED.json"))

    with st.expander("🏥 Financial Health – Details"):
        st.write(load_json(f"{symbol}_CAT3_SCORED.json"))

    with st.expander("👔 Management – Details"):
        st.write(load_json(f"{symbol}_CAT4_SCORED.json"))

    with st.expander("📊 Valuation – Details"):
        st.write(load_json(f"{symbol}_CAT5_SCORED.json"))

    # ------------------------------
    # VERDICT
    # ------------------------------
    score = final["total"]

    if score >= 80:
        verdict = "✅ Strong Buy"
    elif score >= 60:
        verdict = "🟡 Good Quality – Watch Valuation"
    elif score >= 40:
        verdict = "🟠 Cyclical Opportunity"
    else:
        verdict = "🔴 High Risk / Deep Cyclical"

    st.markdown(f"""
    <div class="verdict">
        <div style="letter-spacing:1px;">INVESTMENT VERDICT</div>
        <h1>{verdict}</h1>
        <p>This decision is derived from a multi-factor 100-point quantitative model.</p>
    </div>
    """, unsafe_allow_html=True)
