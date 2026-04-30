# 🔮 AI Trend Predictor

> **Predict market trends for Gold, S&P 500, and Bitcoin** — powered by ARIMA, Prophet, RSI, Bollinger Bands, MACD, and GPT-4o AI reports.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai)
![License](https://img.shields.io/badge/License-Educational-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## What Is This?

**AI Trend Predictor** is an open-source, full-stack web app that analyses financial market trends using a combination of classical time-series statistics, machine learning, and generative AI. It fetches 2 years of live market data, runs three forecasting models, computes professional-grade technical indicators, and writes plain-English reports — all served through a modern SaaS-style dark/light dashboard.

It is designed to be **educational**: to help you understand how markets move, what technical indicators mean, and how AI can assist in trend analysis — not to tell you what to buy or sell.

> ⚠️ **Disclaimer**: For **educational purposes only**. Not financial advice. Always consult a licensed financial advisor.

---

## Live Preview

```bash
git clone https://github.com/your-username/ai-trend-predictor.git
cd ai-trend-predictor
pip install -r requirements.txt
python -m uvicorn frontend.server:app --port 8000
```

Open **http://localhost:8000**

---

## Key Features

### Trend Forecasting
- **ARIMA** — statistical time-series baseline
- **Facebook Prophet** — trend + seasonality decomposition
- **LSTM** — deep learning (optional, requires TensorFlow)
- **Weighted Ensemble** — combines all models into one prediction
- **90% Confidence Interval** — shows the likely price range, not just a single number

### Technical Indicators
| Indicator | What It Shows |
|---|---|
| **RSI (14)** | Overbought / oversold momentum — key entry & exit signals |
| **Bollinger Bands (20, ±2σ)** | Price envelope — breakouts and squeeze patterns |
| **MACD (12/26/9)** | Trend momentum and direction changes |
| **ATR (14)** | Volatility-based stop-loss and price target calculation |
| **MA 20 / MA 50** | Short and medium-term trend direction |

### Risk Metrics
Sharpe Ratio · Max Drawdown · VaR (95%) · CVaR · Skewness · Kurtosis · ATR

### Multi-Currency + Multi-Unit
Switch any price to your local currency and preferred unit instantly:

| Currencies | Gold Units |
|---|---|
| USD · EUR · GBP · PKR · SAR · AED · INR · CNY · JPY · KWD · QAR · OMR · BHD · EGP · BDT · MYR · TRY | Troy Oz · Gram · 10g Bar · **Tola** · **Mithqal** · Tael · 100g Bar · Kg |

Exchange rates are fetched live every hour.

### AI-Written Reports
Click **Generate Report** — GPT-4o writes a plain-English trend analysis including RSI, MACD, and Bollinger Band context, plus a personalised recommendation for your risk profile. Template reports work offline without an API key.

### ATR-Based Price Targets
No arbitrary fixed percentages. Stop-loss and price targets are derived from the **Average True Range**:

| Signal | Target | Stop | Min R/R |
|---|---|---|---|
| Buy | Entry + 3× ATR | Entry − 2× ATR | 1.5× |
| Accumulate | Entry + 2× ATR | Entry − 1.5× ATR | 1.33× |
| Hold | Entry + 1× ATR | Entry − 1× ATR | 1.0× |

### Light + Dark Theme
One-click theme toggle. Remembers your preference. Charts, cards, and text all adapt.

---

## Dashboard Tabs

| Tab | Content |
|---|---|
| **📈 Overview** | Price chart with Bollinger Bands + MA toggles · RSI gauge + chart · MACD histogram · Volatility · Monthly returns |
| **🔮 Price Forecast** | Ensemble prediction + 90% CI band · ARIMA / Prophet comparison table |
| **🛡️ Risk Check** | 8 risk KPI cards (traffic-light status) · Drawdown chart · Plain-English summary |
| **💡 What To Do** | BUY / HOLD / SELL / ACCUMULATE · ATR-based price targets · Risk/reward ratio |
| **🤖 AI Analysis** | GPT-4o trend report + personalised recommendation |
| **🔄 Compare All** | Normalised performance · Risk metrics table · Correlation heatmap |

---

## Architecture

```
Browser  ──────────────────────────────────────────────────
Vanilla HTML + CSS + JS (no framework)
Plotly.js (charts) · Marked.js (AI report rendering)
        │  REST API (JSON)
FastAPI ──────────────────────────────────────────────────
/api/data   /api/predict   /api/risk    /api/suggest
/api/report /api/compare   /api/ticker  /api/exchange-rates
        │
  ┌─────┴──────────────────────────────────┐
  │                                        │
Data (yfinance)               ML + Analysis
RSI / Bollinger / MACD / ATR  ARIMA + Prophet + LSTM
Live FX (open.er-api.com)     Risk Metrics + Suggestions
                                        │
                              OpenAI GPT-4o
                              (trend reports)
```

---

## Project Structure

```
ai-trend-predictor/
│
├── README.md                        ← You are here
├── QUICKSTART.md                    ← 5-step setup guide
├── IMPLEMENTATION_SUMMARY.md        ← Engineering decisions
├── requirements.txt                 ← Python dependencies
├── .env.example                     ← Config template (copy to .env)
├── .gitignore
│
├── src/                             ← Core Python library
│   ├── data/
│   │   └── market_data.py           ← Data fetch + RSI/BB/MACD/ATR
│   ├── models/
│   │   └── predictors.py            ← ARIMA, Prophet, LSTM, Ensemble
│   ├── analysis/
│   │   ├── risk_analysis.py         ← VaR, CVaR, Sharpe, Drawdown, ATR
│   │   └── suggestions.py           ← ATR-based recommendation engine
│   └── reporting/
│       └── report_generator.py      ← GPT-4o trend report generation
│
└── frontend/
    ├── server.py                    ← FastAPI backend (9 REST endpoints)
    └── static/
        ├── index.html               ← Full SaaS dashboard
        ├── css/app.css              ← Design system (light + dark theme)
        └── js/app.js                ← Frontend logic + currency converter
```

---

## Quick Start

### 1 — Install

```bash
pip install -r requirements.txt
```

### 2 — Configure (optional)

```bash
cp .env.example .env
# Add your OpenAI key for AI reports (app works without it)
```

### 3 — Run

```bash
python -m uvicorn frontend.server:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000**

> First load: 15–30 seconds (downloading 2 years of data + fitting models).
> After that: instant tab switching.

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Optional | GPT-4o API key — enables AI trend reports |
| `FRED_API_KEY` | Optional | FRED API for real macroeconomic data |

### Runtime (no restart needed)

Change everything live in the navbar:

| Control | Options |
|---|---|
| **Asset** | Gold · S&P 500 · Bitcoin |
| **Currency** | 17 currencies |
| **Unit** | Tola / Mithqal / Tael / Gram / BTC / Satoshi / … |
| **Risk Tolerance** | Conservative · Moderate · Aggressive |
| **Forecast Period** | 5 · 7 · 14 · 30 days |
| **Theme** | Dark / Light |

---

## API Reference

Interactive docs at **http://localhost:8000/docs**

| Endpoint | Method | Returns |
|---|---|---|
| `/api/ticker` | GET | Live prices + daily change |
| `/api/data/{asset}` | GET | OHLC, MA, RSI, Bollinger, MACD, ATR |
| `/api/predict/{asset}` | GET | Ensemble forecast + 90% CI |
| `/api/risk/{asset}` | GET | Sharpe, VaR, CVaR, drawdown, ATR |
| `/api/suggest/{asset}` | GET | Trend signal + ATR price targets |
| `/api/report/{asset}` | POST | GPT-4o written trend analysis |
| `/api/compare` | GET | All assets normalised + correlation |
| `/api/exchange-rates` | GET | Live USD-based rates (17 currencies) |
| `/api/macro` | GET | Inflation + Fed rate estimates |

### Quick example

```bash
# Current RSI and trend signal for Gold
curl http://localhost:8000/api/data/gold | python -m json.tool | grep -A5 '"tech"'
```

```json
"tech": {
  "rsi_now": 62.4,
  "rsi_signal": "Neutral",
  "macd_signal_now": "Bullish",
  "bb_signal": "Near upper band — potential resistance",
  "atr": 87.40
}
```

---

## Module Reference

### Technical Indicators

```python
from src.data.market_data import MarketDataCollector

c = MarketDataCollector(lookback_days=730)
df = c.get_gold_data()

tech = c.get_technical_indicators(df)
# rsi, rsi_now, rsi_signal
# bb_upper, bb_middle, bb_lower, bb_pct, bb_signal
# macd, macd_signal, macd_hist, macd_signal_now
# atr, atr_pct
```

### Forecasting

```python
from src.models.predictors import EnsemblePredictor

e = EnsemblePredictor()
e.fit_all_models(prices, use_lstm=False)

forecast  = e.predict_ensemble(periods=7)
# {"arima": [...], "prophet": [...], "ensemble": [...]}

ci = e.predict_with_confidence_intervals(periods=7)
# {"forecast": [...], "lower_ci": [...], "upper_ci": [...]}
```

### Risk Analysis

```python
from src.analysis.risk_analysis import RiskMetrics

summary = RiskMetrics().get_risk_summary(prices, "Gold", raw_data=df)
# annual_return, volatility_pct, sharpe_ratio,
# max_drawdown_pct, var_95_pct, cvar_95_pct,
# skewness, kurtosis, atr, atr_pct
```

### Trend Suggestions

```python
from src.analysis.suggestions import SuggestionsEngine

sug = SuggestionsEngine.generate_suggestion(
    asset_name="Gold",
    current_price=4572.40,
    predictions={"trend": "bullish", "confidence": 0.65, "price_target": 4600},
    risk_metrics=summary,
    timeframe="mid-term",
    technical=tech,          # RSI + MACD used in decision
)

d = sug.to_dict()
# action, confidence, risk_level,
# entry_price, target_price, stop_loss,
# upside_pct, downside_pct, risk_reward, rationale
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JS |
| Charts | Plotly.js (CDN) |
| Market Data | yfinance (Yahoo Finance) |
| Trend Models | statsmodels (ARIMA) + Prophet |
| Deep Learning | TensorFlow / Keras (optional) |
| Risk Maths | NumPy + Pandas |
| AI Reports | OpenAI GPT-4o |
| Exchange Rates | open.er-api.com (free, no key) |

---

## Supported Currencies

`USD` `EUR` `GBP` `PKR` `SAR` `AED` `INR` `CNY` `JPY` `KWD` `QAR` `OMR` `BHD` `EGP` `BDT` `MYR` `TRY`

Live rates refresh hourly from `open.er-api.com`. Hardcoded fallback values activate automatically if the API is unreachable.

---

## Gold Units

| Unit | Weight | Region |
|---|---|---|
| Troy Ounce | 31.10 g | Global standard |
| Gram | 1 g | Universal |
| 10g Bar | 10 g | Common retail bar |
| **Tola** | **11.66 g** | **Pakistan · India · Bangladesh** |
| **Mithqal** | **4.25 g** | **Saudi Arabia · UAE · Kuwait** |
| Tael HK | 37.43 g | Hong Kong · China · SE Asia |
| 100g Bar | 100 g | Investment bars |
| Kilogram | 1000 g | Wholesale / bullion |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Slow first load | Normal — 2 years of data is downloading and models are fitting |
| "No data" error | Check internet connection; Yahoo Finance may be temporarily down |
| AI report fails | Check OpenAI key in the navbar — template reports still work |
| Exchange rates static | Fallback values activate automatically |
| LSTM not available | Uncheck LSTM in the sidebar — ARIMA + Prophet still give a quality ensemble |
| Port in use | `python -m uvicorn frontend.server:app --port 8001` |

---

## Contributing

Contributions welcome. High-value areas:

- **More assets** — commodities, ETFs, forex pairs, more crypto
- **More indicators** — Ichimoku, Fibonacci, Stochastic, Williams %R
- **Backtesting** — compare prediction accuracy against actual price history
- **News sentiment** — FinBERT integration for news-based trend signals
- **FRED integration** — real inflation and interest rate data
- **Portfolio view** — MPT / Black-Litterman optimisation
- **Alerts** — email or webhook when RSI crosses thresholds

### Dev setup

```bash
git clone https://github.com/your-username/ai-trend-predictor.git
cd ai-trend-predictor
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn frontend.server:app --reload --port 8000
```

---

## GitHub Topics

```
trend-prediction  financial-analysis  python  fastapi  openai  gpt4
arima  prophet  technical-analysis  rsi  macd  bollinger-bands  atR
gold  bitcoin  cryptocurrency  forex  pkr  sar  multi-currency  saas
```

---

## Disclaimer

This project is **educational only**. It does not constitute financial advice, investment advice, or any recommendation to buy, sell, or hold any asset. All predictions are probabilistic estimates based on historical data — past trends do not guarantee future results. Always do your own research and consult a qualified financial advisor before making any investment decision.

---

## License

MIT — free to use, modify, and distribute for educational and non-commercial purposes.

---

*AI Trend Predictor v2.0 · FastAPI · Plotly.js · OpenAI GPT-4o*
