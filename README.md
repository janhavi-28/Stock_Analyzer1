# 📊 Stock Analyzer – 100‑Point Scoring Engine

A **Python-based stock analysis system** that evaluates listed stocks using a **100‑point quantitative framework**. The engine scores a company across business quality, profitability, financial health, management quality, and valuation, then aggregates everything into a single, explainable score.

This project is **logic‑first**, modular, and debuggable. Each category runs independently and produces JSON outputs that are easy to inspect.

---

## 🧠 What This Project Does

* Scores any stock (Yahoo Finance symbol) on **5 categories**
* Uses **real Yahoo Finance data** (via `yfinance`)
* Produces **category‑wise JSON score files**
* Aggregates scores into a **final 0–100 score**
* Provides a **Streamlit dashboard** for visualization

---

## 📂 Project Structure (Important Files)

```
Stock_Analyzer/
│
├── app.py                # Streamlit UI (frontend)
├── final_score.py        # Aggregates CAT1–CAT5 into final score (IMPORTANT)
│
├── score_C1.py           # Category 1: Business Quality & Growth
├── score_C2.py           # Category 2: Profitability & Returns
├── score_C3.py           # Category 3: Financial Health & Safety
├── score_C4.py           # Category 4: Management Quality
├── score_C5.py           # Category 5: Valuation (P/E, PEG, DCF)
│
├── yahoo19json.py        # Yahoo Finance data fetch helper
├── .gitignore
└── README.md
```

### ⭐ Most Important Files

| File                          | Why it matters                                      |
| ----------------------------- | --------------------------------------------------- |
| `score_C1.py` – `score_C5.py` | Core scoring logic (heart of the project)           |
| `final_score.py`              | Combines all category scores into a final 100 score |
| `app.py`                      | Streamlit dashboard (visual layer only)             |
| `yahoo19json.py`              | Fetches & structures Yahoo Finance data             |

---

## 📊 Scoring Framework

| Category                  | Max Points |
| ------------------------- | ---------- |
| Business Quality & Growth | 25         |
| Profitability & Returns   | 25         |
| Financial Health & Safety | 25         |
| Management Quality        | 15         |
| Valuation                 | 10         |
| **TOTAL**                 | **100**    |

---

## ⚙️ Requirements

### Python

```
Python 3.9+
```

### Python Libraries

Install dependencies with:

```bash
pip install yfinance streamlit pandas numpy
```

> Note: `json`, `os`, `sys`, `datetime` are part of the Python standard library.

---

## ▶ How to Run (Command Line – Recommended First)

### 1️⃣ Run Individual Category Scoring

Example:

```bash
python score_C3.py TATASTEEL.NS
```

This creates:

```
TATASTEEL.NS_CAT3_SCORED.json
```

Run all categories:

```bash
python score_C1.py TATASTEEL.NS
python score_C2.py TATASTEEL.NS
python score_C3.py TATASTEEL.NS
python score_C4.py TATASTEEL.NS
python score_C5.py TATASTEEL.NS
```

---

### 2️⃣ Generate Final Score

```bash
python final_score.py TATASTEEL.NS
```

Example output:

```
==== FINAL SCORE SHEET ====
Category 1:  4 / 25
Category 2:  0 / 25
Category 3:  9 / 25
Category 4: 15 / 15
Category 5:  4 / 10
TOTAL SCORE: 32 / 100
```

Also generates:

```
TATASTEEL.NS_FINAL_SCORE.json
```

---

## 🌐 Run Streamlit UI (Dashboard)

### 1️⃣ Install Streamlit

```bash
python -m pip install streamlit
```

### 2️⃣ Launch the App

```bash
python -m streamlit run app.py
```

Your browser will open automatically with the dashboard.

---









