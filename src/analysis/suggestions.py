"""
Investment Suggestions Engine
Generates risk-aware, ATR-based investment recommendations.
"""

import logging
from typing import Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class InvestmentSuggestion:
    """Container for a single investment suggestion."""

    def __init__(self, asset_name, action, confidence, risk_level,
                 rationale, entry_price, target_price, stop_loss, holding_period):
        self.asset_name    = asset_name
        self.action        = action
        self.confidence    = confidence
        self.risk_level    = risk_level
        self.rationale     = rationale
        self.entry_price   = entry_price
        self.target_price  = target_price
        self.stop_loss     = stop_loss
        self.holding_period = holding_period

    def to_dict(self) -> Dict:
        upside   = (self.target_price - self.entry_price) / self.entry_price * 100
        downside = (self.stop_loss    - self.entry_price) / self.entry_price * 100
        rr_ratio = abs(upside / downside) if downside != 0 else 0
        return {
            "asset":          self.asset_name,
            "action":         self.action,
            "confidence":     self.confidence,
            "risk_level":     self.risk_level,
            "rationale":      self.rationale,
            "entry_price":    self.entry_price,
            "target_price":   self.target_price,
            "stop_loss":      self.stop_loss,
            "upside_pct":     upside,
            "downside_pct":   downside,
            "risk_reward":    round(rr_ratio, 2),
            "holding_period": self.holding_period,
        }


class SuggestionsEngine:
    """Generate data-driven investment suggestions."""

    # ── Public interface ────────────────────────────────────────────────

    @staticmethod
    def generate_suggestion(
        asset_name: str,
        current_price: float,
        predictions: Dict,
        risk_metrics: Dict,
        timeframe: str = "mid-term",
        technical: Dict = None,
    ) -> InvestmentSuggestion:
        """
        Generate a single investment suggestion.

        Parameters
        ----------
        asset_name    : Name of the asset.
        current_price : Latest close price.
        predictions   : {'trend', 'confidence', 'price_target', 'volatility', 'sharpe_ratio'}
        risk_metrics  : Output of RiskMetrics.get_risk_summary().
        timeframe     : 'short-term' | 'mid-term' | 'long-term'
        technical     : Optional dict from MarketDataCollector.get_technical_indicators().
        """
        trend      = predictions.get("trend", "neutral")
        confidence = float(predictions.get("confidence", 0.5))
        pt_raw     = float(predictions.get("price_target", current_price))

        vol_pct    = float(risk_metrics.get("volatility_pct")
                           or risk_metrics.get("current_volatility", 0.20) * 100)
        sharpe     = float(risk_metrics.get("sharpe_ratio", 0))
        max_dd     = abs(float(risk_metrics.get("max_drawdown_pct", -15)))

        # ATR: prefer from risk_metrics, fall back to volatility proxy
        atr = float(risk_metrics.get("atr") or current_price * vol_pct / 100 / np.sqrt(252) * 14)
        atr = max(atr, current_price * 0.005)   # floor at 0.5%

        # ── RSI adjustment ────────────────────────────────────────────
        rsi_now    = float((technical or {}).get("rsi_now", 50))
        rsi_signal = (technical or {}).get("rsi_signal", "Neutral")
        macd_bull  = (technical or {}).get("macd_signal_now", "Neutral") == "Bullish"

        # ── Confidence adjustment ─────────────────────────────────────
        if sharpe < -0.5:     confidence *= 0.55
        elif sharpe < 0:      confidence *= 0.75
        elif sharpe >= 1.5:   confidence = min(confidence * 1.1, 0.9)

        # Overbought/oversold adjustment
        if rsi_now > 75 and trend == "bullish":
            confidence *= 0.80   # Reduce confidence on overbought buy signal
        elif rsi_now < 25 and trend == "bearish":
            confidence *= 0.80

        confidence = float(np.clip(confidence, 0.0, 1.0))

        # ── Action ────────────────────────────────────────────────────
        action = SuggestionsEngine._determine_action(
            trend, confidence, current_price, pt_raw, sharpe,
            rsi_now, rsi_signal, macd_bull
        )

        # ── ATR-based price targets (data-driven) ─────────────────────
        if action == "Buy":
            target_price = current_price + 3.0 * atr   # 3:2 risk/reward
            stop_loss    = current_price - 2.0 * atr
        elif action == "Accumulate":
            target_price = current_price + 2.0 * atr   # 2:1.5 risk/reward
            stop_loss    = current_price - 1.5 * atr
        elif action == "Sell":
            target_price = current_price - 2.5 * atr
            stop_loss    = current_price + 1.0 * atr   # stop above entry on shorts
        else:  # Hold
            target_price = current_price + 1.0 * atr
            stop_loss    = current_price - 1.0 * atr

        # Sanity check: stops/targets can't invert
        if action != "Sell" and stop_loss >= current_price:
            stop_loss = current_price * 0.97
        if action == "Sell" and stop_loss <= current_price:
            stop_loss = current_price * 1.03

        # ── Risk classification ───────────────────────────────────────
        risk_level = SuggestionsEngine._classify_risk(vol_pct, max_dd, sharpe)

        # ── Holding period ────────────────────────────────────────────
        if timeframe == "short-term":
            holding_period = "1–5 days"
        elif timeframe == "mid-term":
            holding_period = "2–6 weeks"
        else:
            holding_period = "3–12 months"

        # ── Rationale ─────────────────────────────────────────────────
        rationale = SuggestionsEngine._build_rationale(
            asset_name, action, trend, risk_level, vol_pct, sharpe,
            confidence, rsi_now, rsi_signal, macd_bull
        )

        return InvestmentSuggestion(
            asset_name=asset_name,
            action=action,
            confidence=confidence,
            risk_level=risk_level,
            rationale=rationale,
            entry_price=current_price,
            target_price=round(target_price, 2),
            stop_loss=round(stop_loss, 2),
            holding_period=holding_period,
        )

    # ── Internals ───────────────────────────────────────────────────────

    @staticmethod
    def _determine_action(trend, confidence, current_price, price_target,
                          sharpe, rsi_now, rsi_signal, macd_bull) -> str:
        expected_return = (price_target - current_price) / current_price

        # Overbought + bearish → Sell
        if rsi_signal == "Overbought" and trend == "bearish" and confidence > 0.5:
            return "Sell"
        # Oversold + bullish → strong Buy
        if rsi_signal == "Oversold" and trend == "bullish" and confidence > 0.5:
            return "Buy"

        # MACD + trend alignment → stronger signal
        if trend == "bullish" and macd_bull:
            if expected_return > 0.01 and confidence >= 0.55:
                return "Buy"
            if expected_return > 0 and confidence >= 0.50:
                return "Accumulate"
        if trend == "bearish" and not macd_bull:
            if expected_return < -0.01 and confidence >= 0.55:
                return "Sell"

        # Fallback rule-based
        if trend == "bullish" and expected_return > 0.02 and confidence >= 0.60:
            return "Buy"
        if trend == "bullish" and expected_return >= 0 and confidence >= 0.50:
            return "Accumulate"
        if trend == "bearish" and expected_return < -0.01:
            return "Sell"

        return "Hold"

    @staticmethod
    def _classify_risk(volatility_pct: float, max_drawdown_pct: float, sharpe: float) -> str:
        """
        Score each dimension 0–3, normalise to 0–3 average.
        Thresholds corrected so 22% vol + 17% DD = Medium (not Low).
        """
        score = 0

        # Volatility (0-3)
        if   volatility_pct < 12:  score += 0
        elif volatility_pct < 20:  score += 1
        elif volatility_pct < 30:  score += 2
        else:                      score += 3

        # Max drawdown — already absolute value (0-3)
        if   max_drawdown_pct < 8:   score += 0
        elif max_drawdown_pct < 18:  score += 1
        elif max_drawdown_pct < 30:  score += 2
        else:                        score += 3

        # Sharpe (0-3, inverted — lower Sharpe = more risk)
        if   sharpe > 1.5:  score += 0
        elif sharpe > 0.5:  score += 1
        elif sharpe > -0.5: score += 2
        else:               score += 3

        avg = score / 3.0
        if   avg < 1.0:  return "Low"
        elif avg < 2.0:  return "Medium"
        else:            return "High"

    @staticmethod
    def _build_rationale(asset_name, action, trend, risk_level, vol_pct,
                          sharpe, confidence, rsi_now, rsi_signal, macd_bull) -> str:
        parts = []

        # Trend
        trend_map = {
            "bullish": f"{asset_name} shows bullish price momentum",
            "bearish": f"{asset_name} shows bearish price pressure",
            "neutral": f"{asset_name} has mixed directional signals",
        }
        parts.append(trend_map.get(trend, f"{asset_name} shows mixed signals"))

        # RSI insight
        if rsi_signal == "Oversold":
            parts.append(f"RSI at {rsi_now:.0f} signals oversold conditions — historically a buying opportunity")
        elif rsi_signal == "Overbought":
            parts.append(f"RSI at {rsi_now:.0f} signals overbought conditions — caution warranted")
        else:
            parts.append(f"RSI at {rsi_now:.0f} is in neutral territory")

        # MACD
        parts.append(f"MACD momentum is {'positive (upward trend)' if macd_bull else 'negative (downward pressure)'}")

        # Risk
        risk_desc = {
            "Low":    "with low overall risk characteristics",
            "Medium": "with moderate risk — suitable for balanced investors",
            "High":   "with elevated risk — suitable only for risk-tolerant investors",
        }
        parts.append(risk_desc.get(risk_level, ""))

        # Sharpe
        if sharpe >= 1.5:
            parts.append(f"Strong risk-adjusted returns (Sharpe {sharpe:.2f})")
        elif sharpe >= 0.5:
            parts.append(f"Acceptable risk-adjusted returns (Sharpe {sharpe:.2f})")
        else:
            parts.append(f"Weak risk-adjusted returns (Sharpe {sharpe:.2f}) — be cautious")

        # Confidence
        parts.append(f"Model confidence: {int(confidence*100)}%")

        return ". ".join(p.capitalize() for p in parts if p) + "."

    @staticmethod
    def generate_portfolio_suggestions(
        assets, current_prices, predictions, risk_metrics,
        portfolio_risk_profile="Moderate", technical_data=None,
    ) -> List["InvestmentSuggestion"]:
        suggestions = []
        for asset in assets:
            if asset not in current_prices:
                continue
            tech = (technical_data or {}).get(asset)
            sug  = SuggestionsEngine.generate_suggestion(
                asset_name=asset,
                current_price=current_prices[asset],
                predictions=predictions.get(asset, {}),
                risk_metrics=risk_metrics.get(asset, {}),
                timeframe="mid-term",
                technical=tech,
            )
            if portfolio_risk_profile == "Conservative" and sug.risk_level == "High":
                sug.confidence *= 0.7
            suggestions.append(sug)
        return suggestions
