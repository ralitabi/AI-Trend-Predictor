# 🔮 AI Trend Predictor — Quick Start

Get up and running in under 5 minutes.

---

## Prerequisites

- Python 3.10 or higher (`python --version`)
- `pip` (`python -m pip --version`)
- Internet connection

---

## Step 1 — Clone or Download

```bash
git clone https://github.com/your-username/ai-investment-terminal.git
cd ai-investment-terminal
```

Or download the ZIP from GitHub and extract it.

---

## Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, yfinance, statsmodels, Prophet, scikit-learn, Plotly, OpenAI, and everything else needed.

> **Python 3.14 users**: TensorFlow is not yet available for 3.14. That is fine — LSTM is optional and disabled by default.

---

## Step 3 — Configure (Optional)

```bash
cp .env.example .env
```

Open `.env` and set your OpenAI key if you want AI-generated reports:

```
OPENAI_API_KEY=sk-proj-your-key-here
```

The app works fully **without** any API key — it uses professional template reports instead.

---

## Step 4 — Start the Server

```bash
python -m uvicorn frontend.server:app --host 0.0.0.0 --port 8000
```

---

## Step 5 — Open the Dashboard

Open your browser and go to:

```
http://localhost:8000
```

The first load takes 10–30 seconds while market data is downloaded and models are fitted. Subsequent tab switches are instant.

---

## What You Will See

```
Navbar  -> Select asset (Gold / S&P 500 / Bitcoin)
        -> Select currency (USD, PKR, SAR, EUR, GBP, ...)
        -> Select unit (Troy Oz, Tola, Mithqal, BTC, ...)
        -> Set risk tolerance
        -> Set forecast period

Ticker  -> Live scrolling prices for all 3 assets

Hero    -> Current price in your chosen currency & unit
        -> 52-week range progress bar

Tabs:
  Overview    -> Price chart + Bollinger Bands + RSI + MACD
  Forecast    -> AI ensemble prediction + 90% confidence band
  Risk Check  -> Sharpe, VaR, CVaR, drawdown, ATR
  What To Do  -> Buy/Hold/Sell + ATR-based price targets
  AI Analysis -> GPT-4o written market report
  Compare All -> Gold vs S&P 500 vs Bitcoin side by side
```

---

## Currency + Unit Examples

| If you are in... | Set Currency | Set Unit | What you see |
|---|---|---|---|
| Pakistan | PKR | Tola (11.66g) | Gold price per tola in rupees |
| Saudi Arabia | SAR | Mithqal (4.25g) | Gold price per mithqal in riyals |
| United Kingdom | GBP | Troy Ounce | Gold price per oz in pounds |
| Hong Kong | CNY | Tael HK (37.43g) | Gold price per tael in yuan |
| USA | USD | BTC | Bitcoin price in dollars |

---

## Adding Your OpenAI Key in the UI

You can also enter your key directly in the dashboard without editing any file:

1. Find the **OpenAI Key** field in the top-right navbar
2. Paste your `sk-proj-...` key
3. Click **Generate Report** in the AI Analysis tab

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Port 8000 already in use | Add `--port 8001` to the uvicorn command |
| Slow first load | Normal — models are fitting, wait 30 seconds |
| "No data" error | Check internet connection |
| AI report fails | Check your OpenAI key — template reports still work |
| Exchange rates not live | Fallback values are used automatically |

---

## Stopping the Server

Press `Ctrl + C` in the terminal where uvicorn is running.

---

## Next Steps

- Read [README.md](README.md) for the full API reference and module documentation
- Try switching currencies while viewing the price — all numbers update instantly
- Compare Gold vs Bitcoin in the **Compare All** tab
- Generate an AI report with your OpenAI key
