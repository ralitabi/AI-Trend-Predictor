# 🔮 AI Trend Predictor — Implementation Summary

Technical architecture and engineering decisions for v2.0.

---

## System Architecture

```
Browser (Vanilla HTML/CSS/JS + Plotly.js)
           |
     REST API (FastAPI)
           |
    +------+------+
    |             |
 Data Layer    Analysis Layer
 yfinance       RSI / BB / MACD / ATR
 open.er-api    ARIMA / Prophet / Ensemble
 MacroData      RiskMetrics / Suggestions
                    |
              OpenAI GPT-4o
              (AI Reports)
```

No framework on the frontend (React, Vue, Angular). Vanilla JS with `fetch()` and Plotly.js keeps the stack minimal and the bundle size at zero.

---

## Backend (`frontend/server.py`)

**FastAPI** serves both the static files and the REST API from a single process.

### In-memory caching strategy

All expensive operations are cached in a Python `dict` (`_cache`) keyed by `asset + params`:

| Cache key | Content | TTL |
|---|---|---|
| `df_{asset}_{lookback}` | Raw OHLCV DataFrame | Process lifetime |
| `tech_{asset}` | RSI, BB, MACD, ATR | Process lifetime |
| `risk_{asset}` | Full risk summary | Process lifetime |
| `pred_{asset}_{days}_{lstm}` | Ensemble predictions + CI | Process lifetime |
| `exchange_rates` | FX rates dict | Process lifetime (refreshed hourly by frontend) |

A server restart clears all caches. For production, replace with Redis.

### Exchange rate fetching

```python
urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=6)
```

Uses the standard library only — no extra dependency. Falls back to hardcoded approximate rates if the request fails.

---

## Data Layer (`src/data/market_data.py`)

### yfinance compatibility

yfinance >= 0.2.38 returns MultiIndex columns for single-ticker downloads. Fixed with:

```python
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
data.columns = [str(col).lower() for col in data.columns]
```

### Technical indicators

All indicators are implemented in pure NumPy/Pandas — no TA-Lib dependency:

| Indicator | Implementation |
|---|---|
| RSI (14) | Wilder smoothing via `rolling().mean()` on gains/losses |
| Bollinger Bands | 20-period MA ± 2 std dev |
| MACD | EWM fast/slow difference + signal EWM |
| ATR | True range = max(H-L, abs(H-C_prev), abs(L-C_prev)), 14-period rolling mean |

---

## Prediction Models (`src/models/predictors.py`)

### Ensemble weights

```
ARIMA   30%  — statistical baseline
Prophet 40%  — best for trend + seasonality
LSTM    30%  — deep learning (optional, disabled on Python 3.14)
```

When a model fails (e.g., LSTM not installed), remaining weights are renormalised automatically.

### Confidence intervals

Primary source: ARIMA `get_forecast().conf_int(alpha=0.10)` → 90% CI.

Fallback (when ARIMA unavailable): ±2% bands around the ensemble forecast.

### LSTM fix

The original code passed `np.array([1])` (garbage data) to `lstm.predict()`. Fixed by storing `_last_sequence` (the final `lookback_period` scaled values) after `fit()` and using it automatically:

```python
def predict(self, data=None, periods=5):
    if data is not None and len(data) >= self.lookback_period:
        current_seq = ...  # from data
    elif self._last_sequence is not None:
        current_seq = self._last_sequence.reshape(...)  # from fit()
```

---

## Risk Analysis (`src/analysis/risk_analysis.py`)

### ATR integration

ATR (Average True Range) is computed from raw OHLC data when available:

```python
tr = pd.concat([
    data['high'] - data['low'],
    (data['high'] - close.shift()).abs(),
    (data['low']  - close.shift()).abs(),
], axis=1).max(axis=1)
atr = tr.rolling(14).mean()
```

Falls back to a 14-day rolling close price range when OHLC is unavailable (e.g., VIX index).

### Safe NaN guard

```python
if len(returns) < 10:
    logger.warning("Insufficient data for risk analysis")
    return {}
```

---

## Suggestion Engine (`src/analysis/suggestions.py`)

### Bug fixed: risk classification thresholds

Original thresholds classified 22% volatility + 17% drawdown as **Low** risk.

Root cause: `avg_score = risk_score / 3` produced 0.67, which was below the `< 1.0` threshold for Low.

Fix — adjusted thresholds to match real-world classification:

```python
if   volatility_pct < 12:  score += 0   # Low
elif volatility_pct < 20:  score += 1   # Moderate
elif volatility_pct < 30:  score += 2   # High
else:                      score += 3   # Very High

avg = score / 3.0
if   avg < 1.0:  return "Low"
elif avg < 2.0:  return "Medium"
else:            return "High"
```

### Bug fixed: price targets

Original: `stop_loss = entry * 0.95` → fixed 5% regardless of asset volatility.  
Result: 0.51% upside vs −5% stop = 0.1× risk/reward.

Fix — ATR-based targets give data-driven levels:

```python
if action == "Buy":
    target_price = entry + 3.0 * atr   # 1.5× R/R minimum
    stop_loss    = entry - 2.0 * atr
```

Gold ATR ~$87 → target +$261, stop −$174 → 1.5× R/R.

### Multi-factor signal

The suggestion engine now uses RSI, MACD, and trend alignment together:

```python
if rsi_signal == "Oversold" and trend == "bullish" and confidence > 0.5:
    return "Buy"
if rsi_signal == "Overbought" and trend == "bearish":
    return "Sell"
if trend == "bullish" and macd_bull:
    return "Buy" if expected_return > 0.01 else "Accumulate"
```

---

## Report Generator (`src/reporting/report_generator.py`)

Switched from OpenAI `gpt-3.5-turbo` to `gpt-4o` for significantly better analysis quality.

GPT-4o prompt now includes RSI, MACD signal, and Bollinger Band position — not just raw price metrics — giving the AI genuine technical context.

Template fallback uses the same structure so reports look consistent with or without an API key.

---

## Frontend Architecture (`frontend/static/`)

### No build step

Plain HTML + CSS + JS. Plotly.js and Marked.js are loaded from CDN. Zero webpack, zero npm, zero bundler. The entire frontend is three files.

### Conversion engine

All prices flow through `App.fmt(usdPrice)`:

```javascript
fmt(usdPrice) {
    const converted = usdPrice * this.exchangeRates[this.currency] * sizeUnitFactor;
    return `${currencySymbol}${formatted}`;
}
```

When currency or unit changes → `App._reRenderAll()` rebuilds every chart and text label.

Charts receive pre-converted price arrays:

```javascript
const prices = this.cvtArr(d.prices);  // multiplied by fxRate × sizeFactor
plot('chartPrice', [{y: prices, ...}], layout);
```

The Plotly Y-axis automatically shows the correct scale.

### Theme system

```css
[data-theme="dark"]  { --bg0: #02060F; --text1: #EEF2FF; ... }
[data-theme="light"] { --bg0: #E8EDF5; --text1: #0F172A; ... }
```

`App.toggleTheme()` swaps the attribute and calls `_reRenderAll()` — charts re-render with new background and grid colors.

---

## Key Engineering Decisions

| Decision | Rationale |
|---|---|
| FastAPI over Streamlit | Full control over HTML/CSS/JS — Streamlit CSS overrides are fragile |
| Vanilla JS over React | Zero build tooling, zero dependencies, instant load |
| In-memory cache over DB | Simple, fast; acceptable for single-user educational tool |
| urllib.request for FX | No extra dependency — httpx/requests already available but not needed |
| open.er-api.com for FX | Free, no API key, supports PKR/SAR/AED/etc. |
| ATR for stops | Data-driven, volatility-adjusted — eliminates arbitrary fixed-% stops |
| 730-day lookback | More historical data = better ARIMA/Prophet fitting |

---

## Files Changed from Original

| File | Change |
|---|---|
| `src/data/market_data.py` | Added RSI, BB, MACD, ATR; fixed yfinance MultiIndex columns |
| `src/models/predictors.py` | Fixed LSTM predict bug; added `predict_with_confidence_intervals()` |
| `src/analysis/risk_analysis.py` | Added ATR to summary; NaN guard for short series |
| `src/analysis/suggestions.py` | Rewrote risk thresholds; ATR-based targets; RSI/MACD signals |
| `src/reporting/report_generator.py` | Switched to GPT-4o; OpenAI v2 SDK; richer prompts |
| `frontend/server.py` | New FastAPI server replacing Streamlit; exchange rates endpoint |
| `frontend/static/index.html` | Full SaaS dashboard with 6 tabs |
| `frontend/static/css/app.css` | Complete design system — light + dark |
| `frontend/static/js/app.js` | Conversion engine; RSI/BB/MACD charts; theme toggle |

---

*🔮 AI Trend Predictor v2.0 — Built April 2026*
