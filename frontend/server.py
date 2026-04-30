"""
AI Trend Predictor — FastAPI Backend v2
Full technical analysis: RSI, Bollinger Bands, MACD, ATR + improved suggestions.
"""
import json
import os
import sys
import logging
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

ROOT   = Path(__file__).parent.parent
STATIC = Path(__file__).parent / "static"
sys.path.insert(0, str(ROOT / "src"))

from analysis.risk_analysis import RiskMetrics
from analysis.suggestions import SuggestionsEngine
from data.market_data import MacroeconomicData, MarketDataCollector
from models.predictors import EnsemblePredictor
from reporting.report_generator import AIReportGenerator

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("terminal")

app = FastAPI(title="AI Trend Predictor", version="2.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

# ── In-memory cache ──────────────────────────────────────────────────────────
_cache: dict = {}

ASSET_MAP = {
    "gold":    ("GC=F",    "Gold",    "#F59E0B"),
    "sp500":   ("^GSPC",   "S&P 500", "#3B82F6"),
    "bitcoin": ("BTC-USD", "Bitcoin", "#8B5CF6"),
    "vix":     ("^VIX",    "VIX",     "#EF4444"),
}

COLLECTOR = MarketDataCollector(lookback_days=730)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fetch(asset_key: str, lookback: int = 730) -> pd.DataFrame:
    ck = f"df_{asset_key}_{lookback}"
    if ck not in _cache:
        info = ASSET_MAP.get(asset_key)
        if not info:
            return pd.DataFrame()
        data = MarketDataCollector(lookback_days=lookback).fetch_price_data(info[0])
        _cache[ck] = data
    return _cache[ck]


def _close(df: pd.DataFrame) -> pd.Series:
    for col in ("adj close", "close", "Close", "Adj Close"):
        if col in df.columns:
            return df[col].dropna()
    return df.iloc[:, 0].dropna()


def _safe(v):
    if v is None:                            return None
    if isinstance(v, (np.integer,)):         return int(v)
    if isinstance(v, (np.floating,)):        return None if np.isnan(v) else float(v)
    if isinstance(v, np.ndarray):            return [_safe(x) for x in v]
    if isinstance(v, pd.Series):             return [_safe(x) for x in v]
    return v


def _price_list(s: pd.Series) -> list:
    return [None if (isinstance(v, float) and np.isnan(v)) else float(v) for v in s]


def _get_tech(asset_key: str, df: pd.DataFrame) -> dict:
    ck = f"tech_{asset_key}"
    if ck not in _cache:
        c = MarketDataCollector()
        _cache[ck] = c.get_technical_indicators(df)
    return _cache[ck]


def _get_risk(asset_key: str, df: pd.DataFrame) -> dict:
    ck = f"risk_{asset_key}"
    if ck not in _cache:
        s  = _close(df)
        rm = RiskMetrics().get_risk_summary(s, ASSET_MAP[asset_key][1], raw_data=df)
        _cache[ck] = rm
    return _cache[ck]


def _get_preds(asset_key: str, days: int, use_lstm: bool, df: pd.DataFrame):
    ck = f"pred_{asset_key}_{days}_{use_lstm}"
    if ck not in _cache:
        s = _close(df)
        e = EnsemblePredictor()
        e.fit_all_models(s, use_lstm=use_lstm)
        _cache[ck] = {
            "preds":  e.predict_ensemble(days, use_lstm=use_lstm),
            "ci":     e.predict_with_confidence_intervals(days, use_lstm=use_lstm),
            "series": s,
        }
    return _cache[ck]


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(str(STATIC / "index.html"))


@app.get("/api/ticker")
async def ticker():
    result = {}
    for key in ("gold", "sp500", "bitcoin"):
        df = _fetch(key, lookback=10)
        if df.empty:
            continue
        s = _close(df)
        if len(s) < 2:
            continue
        price  = float(s.iloc[-1])
        chg1d  = float((s.iloc[-1] - s.iloc[-2]) / s.iloc[-2] * 100)
        chg5d  = float((s.iloc[-1] - s.iloc[-5]) / s.iloc[-5] * 100) if len(s) >= 5 else chg1d
        _, name, color = ASSET_MAP[key]
        result[key] = {"name": name, "price": price, "change1d": chg1d,
                       "change5d": chg5d, "color": color}
    return JSONResponse(result)


@app.get("/api/data/{asset_key}")
async def data(asset_key: str, lookback: int = 730):
    df = _fetch(asset_key, lookback)
    if df.empty:
        raise HTTPException(404, f"No data for '{asset_key}'")

    s    = _close(df)
    ma20 = s.rolling(20).mean()
    ma50 = s.rolling(50).mean()
    rets = s.pct_change().dropna() * 100
    vol_s = s.pct_change().rolling(20).std().dropna() * np.sqrt(252) * 100
    monthly = s.resample("ME").last().pct_change().dropna() * 100

    # Technical indicators
    tech = _get_tech(asset_key, df)

    # Basic metrics
    chg5d  = float((s.iloc[-1]-s.iloc[-5])/s.iloc[-5]*100) if len(s)>=5 else 0
    chg30d = float((s.iloc[-1]-s.iloc[-22])/s.iloc[-22]*100) if len(s)>=22 else 0
    chg1d  = float(rets.iloc[-1]) if not rets.empty else 0

    return JSONResponse({
        "dates":    [d.strftime("%Y-%m-%d") for d in s.index],
        "prices":   _price_list(s),
        "ma20":     _price_list(ma20),
        "ma50":     _price_list(ma50),
        "current":  float(s.iloc[-1]),
        "hi52":     float(s.tail(252).max()),
        "lo52":     float(s.tail(252).min()),
        "chg1d":    chg1d,
        "chg5d":    chg5d,
        "chg30d":   chg30d,
        "volatility": float(vol_s.iloc[-1]) if not vol_s.empty else 0.0,
        "returns": {
            "dates":  [d.strftime("%Y-%m-%d") for d in rets.index],
            "values": [float(v) for v in rets.values],
        },
        "vol_series": {
            "dates":  [d.strftime("%Y-%m-%d") for d in vol_s.index],
            "values": [float(v) for v in vol_s.values],
        },
        "monthly": {
            "dates":  [d.strftime("%Y-%m-%d") for d in monthly.index],
            "values": [float(v) for v in monthly.values],
        },
        # ── Technical indicators ─────────────────────────────────────
        "tech": {
            "rsi":          tech["rsi"],
            "rsi_now":      tech["rsi_now"],
            "rsi_signal":   tech["rsi_signal"],
            "bb_upper":     tech["bb_upper"],
            "bb_middle":    tech["bb_middle"],
            "bb_lower":     tech["bb_lower"],
            "bb_pct":       tech["bb_pct"],
            "bb_signal":    tech["bb_signal"],
            "macd":         tech["macd"],
            "macd_signal":  tech["macd_signal"],
            "macd_hist":    tech["macd_hist"],
            "macd_now":     tech["macd_now"],
            "macd_signal_now": tech["macd_signal_now"],
            "atr":          tech["atr"],
            "atr_pct":      tech["atr_pct"],
        },
    })


@app.get("/api/predict/{asset_key}")
async def predict(asset_key: str, days: int = 7, use_lstm: bool = False):
    df = _fetch(asset_key)
    if df.empty:
        raise HTTPException(404, f"No data for '{asset_key}'")

    cached = _get_preds(asset_key, days, use_lstm, df)
    preds, ci, s = cached["preds"], cached["ci"], cached["series"]
    last  = s.index[-1]
    fdates = pd.date_range(last + pd.Timedelta(days=1), periods=days, freq="D")

    return JSONResponse({
        "dates":      [d.strftime("%Y-%m-%d") for d in fdates],
        "ensemble":   [float(v) for v in preds["ensemble"]],
        "arima":      [float(v) for v in preds.get("arima", [])],
        "prophet":    [float(v) for v in preds.get("prophet", [])],
        "ci_upper":   [float(v) for v in ci["upper_ci"]],
        "ci_lower":   [float(v) for v in ci["lower_ci"]],
        "current":    float(s.iloc[-1]),
        "hist_dates": [d.strftime("%Y-%m-%d") for d in s.tail(90).index],
        "hist_prices":[float(v) for v in s.tail(90).values],
    })


@app.get("/api/risk/{asset_key}")
async def risk(asset_key: str):
    df = _fetch(asset_key)
    if df.empty:
        raise HTTPException(404, f"No data for '{asset_key}'")

    rm = _get_risk(asset_key, df)
    s  = _close(df)
    dd = (s - s.cummax()) / s.cummax() * 100
    vs = s.pct_change().rolling(20).std().dropna() * np.sqrt(252) * 100

    return JSONResponse({
        **{k: _safe(v) for k, v in rm.items()},
        "drawdown": {
            "dates":  [d.strftime("%Y-%m-%d") for d in dd.index],
            "values": [float(v) for v in dd.values],
        },
        "vol_series": {
            "dates":  [d.strftime("%Y-%m-%d") for d in vs.index],
            "values": [float(v) for v in vs.values],
        },
    })


@app.get("/api/suggest/{asset_key}")
async def suggest(asset_key: str, risk_profile: str = "Moderate", days: int = 7):
    df = _fetch(asset_key)
    if df.empty:
        raise HTTPException(404, f"No data for '{asset_key}'")

    cached = _get_preds(asset_key, days, False, df)
    ens, s = cached["preds"]["ensemble"], cached["series"]
    rm     = _get_risk(asset_key, df)
    tech   = _get_tech(asset_key, df)
    cur    = float(s.iloc[-1])
    trend  = "bullish" if float(ens[-1]) > cur else "bearish"

    sug = SuggestionsEngine.generate_suggestion(
        asset_name=ASSET_MAP[asset_key][1],
        current_price=cur,
        predictions={"trend": trend, "confidence": 0.65,
                     "price_target": float(ens[-1]),
                     "volatility": rm.get("volatility_pct", 20),
                     "sharpe_ratio": rm.get("sharpe_ratio", 0)},
        risk_metrics=rm,
        timeframe="mid-term",
        technical=tech,
    )
    return JSONResponse({k: _safe(v) for k, v in sug.to_dict().items()})


@app.post("/api/report/{asset_key}")
async def report(asset_key: str,
                 risk_profile: str = Query("Moderate"),
                 days: int = Query(7)):
    df = _fetch(asset_key)
    if df.empty:
        raise HTTPException(404, f"No data for '{asset_key}'")

    cached = _get_preds(asset_key, days, False, df)
    ens, s = cached["preds"]["ensemble"], cached["series"]
    rm     = _get_risk(asset_key, df)
    tech   = _get_tech(asset_key, df)
    cur    = float(s.iloc[-1])
    trend_st = "bullish" if float(ens[min(2, len(ens)-1)]) > cur else "bearish"

    rg  = AIReportGenerator()
    rpt = rg.generate_trend_analysis(
        asset_name=ASSET_MAP[asset_key][1],
        predictions={
            "short_term":             trend_st,
            "confidence":             0.65,
            "volatility":             f"{rm.get('volatility_pct',0):.1f}%",
            "volatility_classification": rm.get("volatility_classification"),
            "sharpe_ratio":           f"{rm.get('sharpe_ratio',0):.2f}",
            "max_drawdown":           f"{rm.get('max_drawdown_pct',0):.1f}%",
            "rsi":                    f"{tech.get('rsi_now',50):.0f} ({tech.get('rsi_signal','Neutral')})",
            "macd_signal":            tech.get("macd_signal_now", "Neutral"),
            "bb_position":            tech.get("bb_signal", "Mid-range"),
        },
        current_price=cur,
        historical_context=(
            f"{len(s)}-day analysis. Annual return {rm.get('annual_return',0):.1f}%. "
            f"RSI={tech.get('rsi_now',50):.0f} ({tech.get('rsi_signal','Neutral')}). "
            f"MACD momentum {tech.get('macd_signal_now','Neutral').lower()}. "
            f"Bollinger Band position: {tech.get('bb_signal','mid-range')}."
        ),
    )
    rec = rg.generate_recommendation(
        asset_name=ASSET_MAP[asset_key][1], risk_profile=risk_profile,
        predictions={
            "trend":       trend_st,
            "price_range": f"${float(ens.min()):,.2f}–${float(ens.max()):,.2f}",
            "upside":      (float(ens[-1])-cur)/cur*100,
            "downside":    (float(ens.min())-cur)/cur*100,
        },
        risk_metrics={
            "volatility_class": rm.get("volatility_classification"),
            "sharpe_ratio":     rm.get("sharpe_ratio", 0),
            "max_drawdown":     rm.get("max_drawdown_pct", 0),
            "var_95":           rm.get("var_95_pct", 0),
        },
    )
    return JSONResponse({"report": rpt, "recommendation": rec})


@app.get("/api/compare")
async def compare():
    result = {}
    for key in ("gold", "sp500", "bitcoin"):
        df = _fetch(key)
        if df.empty:
            continue
        s    = _close(df)
        norm = s / s.iloc[0] * 100
        rm   = {}
        try:
            rm = {k: _safe(v) for k, v in _get_risk(key, df).items()}
        except Exception:
            pass
        result[key] = {
            "name":       ASSET_MAP[key][1],
            "color":      ASSET_MAP[key][2],
            "dates":      [d.strftime("%Y-%m-%d") for d in norm.index],
            "normalized": [float(v) for v in norm.values],
            "rets":       [float(v) for v in s.pct_change().dropna().values],
            "metrics":    rm,
        }
    return JSONResponse(result)


@app.get("/api/macro")
async def macro():
    m = MacroeconomicData.get_economic_indicators()
    return JSONResponse({"inflation": m["inflation"], "interest_rate": m["interest_rate"]})


# ── Exchange rates ────────────────────────────────────────────────────────────
_FX_FALLBACK = {
    "EUR": 0.921, "GBP": 0.792, "PKR": 278.50, "SAR": 3.750,
    "AED": 3.672, "INR": 83.50, "CNY": 7.230,  "JPY": 151.20,
    "BDT": 110.0, "MYR": 4.720, "TRY": 32.50,  "EGP": 48.70,
    "KWD": 0.307, "QAR": 3.640, "OMR": 0.385,  "BHD": 0.376,
}

@app.get("/api/exchange-rates")
async def exchange_rates():
    """Fetch live USD-based exchange rates; falls back to approximate values."""
    ck = "exchange_rates"
    if ck in _cache:
        return JSONResponse(_cache[ck])
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Terminal/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())
        raw = data.get("rates", {})
        rates = {k: round(float(raw[k]), 6) for k in _FX_FALLBACK if k in raw}
        rates["USD"] = 1.0
        _cache[ck] = rates
        log.info("Exchange rates fetched: %s currencies", len(rates))
        return JSONResponse(rates)
    except Exception as exc:
        log.warning("Exchange rate fetch failed (%s) — using fallback", exc)
        fallback = {"USD": 1.0, **_FX_FALLBACK}
        _cache[ck] = fallback
        return JSONResponse(fallback)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
