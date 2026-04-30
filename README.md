# AI Trend Predictor

Predict market trends for Gold, S&P 500, and Bitcoin using a combination of statistical models, machine learning, and AI-generated analysis.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## Overview

AI Trend Predictor is a full-stack web application that analyses financial markets using:

- Time-series forecasting (ARIMA, Prophet, LSTM)
- Technical indicators (RSI, Bollinger Bands, MACD, ATR)
- Risk metrics (Sharpe Ratio, VaR, Drawdown)
- AI-generated reports using GPT-4o

The system retrieves two years of historical data, performs analysis, and presents results through an interactive dashboard.

This project is designed for **educational purposes**, helping users understand how market analysis tools and AI models work together.

---

## Disclaimer

This project is for educational use only. It does not provide financial advice. Always consult a qualified financial professional before making investment decisions.

---

## Quick Start

```bash
git clone https://github.com/ralitabi/AI-Trend-Predictor.git
cd ai-trend-predictor
pip install -r requirements.txt
python -m uvicorn frontend.server:app --port 8000
```

Open your browser at: **http://localhost:8000**

---

## Core Features

### Trend Forecasting
- ARIMA model for statistical baseline predictions
- Prophet for trend and seasonality modelling
- Optional LSTM model for deep learning predictions
- Ensemble model combining multiple approaches
- Confidence intervals for prediction ranges

### Technical Indicators
- **RSI** for momentum analysis
- **Bollinger Bands** for price volatility
- **MACD** for trend direction
- **ATR** for volatility-based calculations
- **Moving averages** (MA20, MA50)

### Risk Analysis
- Sharpe Ratio
- Maximum Drawdown
- Value at Risk (VaR)
- Conditional VaR
- Volatility and distribution metrics

### Multi-Currency and Units
Supports multiple currencies and unit conversions for assets such as gold and cryptocurrency.

### AI-Generated Reports
Generates plain-language summaries of market conditions using GPT-4o.

---

## Dashboard Interface

Interactive charts, multiple analysis tabs, light and dark themes, and real-time data updates.

### Dashboard Sections

| Section | Description |
|---|---|
| **Overview** | Price charts, indicators, and market summary |
| **Price Forecast** | Model predictions and confidence intervals |
| **Risk Analysis** | Risk metrics and drawdown visualisation |
| **Suggestions** | Buy, hold, or sell signals with targets |
| **AI Report** | Generated analysis using GPT |
| **Comparison** | Multi-asset comparison and correlation |

---

## System Architecture

```
Frontend (HTML, CSS, JavaScript)
        │
        │ REST API
        ▼
Backend (FastAPI)
        │
 ┌──────┴───────────────┐
 │                      │
Market Data         ML Models
(yfinance)          ARIMA, Prophet, LSTM
 │                      │
 │                Risk Analysis
 │                Technical Indicators
 │                      │
 └──────────────┬───────┘
                ▼
           AI Reporting
           (GPT-4o)
```

---

## Project Structure

```
ai-trend-predictor/
│
├── README.md
├── QUICKSTART.md
├── IMPLEMENTATION_SUMMARY.md
├── requirements.txt
├── .env.example
│
├── src/
│   ├── data/
│   ├── models/
│   ├── analysis/
│   └── reporting/
│
└── frontend/
    ├── server.py
    └── static/
```

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional configuration:

```bash
cp .env.example .env
```

Add your API keys if required.

---

## Running the Application

```bash
python -m uvicorn frontend.server:app --host 0.0.0.0 --port 8000
```

---

## API Overview

Interactive API documentation is available at: **http://localhost:8000/docs**

### Example Endpoint

```bash
curl http://localhost:8000/api/data/gold
```

Returns technical indicators, current RSI and trend signals, and volatility metrics.

---

## Technologies Used

- Python
- FastAPI
- NumPy and Pandas
- Statsmodels (ARIMA)
- Prophet
- TensorFlow (optional)
- Plotly.js
- OpenAI GPT-4o

---

## Configuration

### Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Enables AI-generated reports |
| `FRED_API_KEY` | Optional macroeconomic data |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Slow startup | Initial data loading and model training |
| Missing data | Check internet connection |
| API errors | Verify configuration keys |
| Port conflict | Use a different port |

---

## Future Improvements

- Additional assets (ETFs, forex pairs)
- More technical indicators
- Backtesting functionality
- News sentiment analysis
- Portfolio optimisation tools

---

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

---

*AI Trend Predictor · FastAPI · Plotly.js · OpenAI GPT-4o*
