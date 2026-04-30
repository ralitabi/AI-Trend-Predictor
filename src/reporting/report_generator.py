"""
AI Report Generation Module
Generates investment insights using the OpenAI API (GPT-4o).
Falls back to template-based reports when no API key is set.
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIReportGenerator:
    """Generate AI-powered investment reports via OpenAI GPT-4o."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o"

        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY not set — using template-based fallback reports."
            )

    # ------------------------------------------------------------------ #
    # Public interface                                                      #
    # ------------------------------------------------------------------ #

    def generate_trend_analysis(
        self,
        asset_name: str,
        predictions: Dict,
        current_price: float,
        historical_context: str,
    ) -> str:
        if not self.api_key:
            return self._fallback_analysis(asset_name, predictions)

        prompt = f"""You are an expert financial analyst. Analyse the following data for **{asset_name}**
and write a concise, professional investment insight report.

**Current Price:** ${current_price:,.2f}
**Short-term outlook (1 week):** {predictions.get('short_term', 'N/A')}
**Model confidence:** {predictions.get('confidence', 'N/A')}
**Historical context:** {historical_context}

**Risk Metrics:**
- Volatility: {predictions.get('volatility', 'N/A')}
- Sharpe Ratio: {predictions.get('sharpe_ratio', 'N/A')}
- Max Drawdown: {predictions.get('max_drawdown', 'N/A')}

Provide a structured response covering:
1. **Market Outlook** (2–3 sentences)
2. **Key Price Drivers** (bullet points)
3. **Risk Assessment** — Low / Medium / High with justification
4. **Suggested Action** — Buy / Hold / Sell / Accumulate with reasoning
5. **Recommended Holding Period**
6. **Price Target** for next 30 days

Write in a professional but accessible tone. End with a one-line disclaimer."""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are a senior financial analyst at a tier-1 investment bank. "
                                "Provide data-driven, objective insights. Always include a brief "
                                "disclaimer that analysis is for educational purposes only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=900,
            )
            report = response.choices[0].message.content
            logger.info("Generated trend analysis for %s via GPT-4o", asset_name)
            return report

        except Exception as exc:
            logger.error("OpenAI error: %s", exc)
            return self._fallback_analysis(asset_name, predictions)

    def generate_recommendation(
        self,
        asset_name: str,
        risk_profile: str,
        predictions: Dict,
        risk_metrics: Dict,
    ) -> str:
        if not self.api_key:
            return self._fallback_recommendation(asset_name, risk_profile)

        prompt = f"""You are a robo-advisor. Given the data below for **{asset_name}**,
write a personalised investment recommendation for a **{risk_profile}** investor.

**Prediction Outlook:**
- Trend: {predictions.get('trend', 'N/A')}
- Price Range (30d): {predictions.get('price_range', 'N/A')}
- Upside Potential: {predictions.get('upside', 0):.1f}%
- Downside Risk: {predictions.get('downside', 0):.1f}%

**Risk Metrics:**
- Volatility Classification: {risk_metrics.get('volatility_class', 'N/A')}
- Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}
- Maximum Drawdown: {risk_metrics.get('max_drawdown', 0):.1f}%
- Value at Risk (95%): {risk_metrics.get('var_95', 0):.2f}%

Provide:
1. **Suitability** — Suitable / Moderately Suitable / Not Suitable for this risk profile
2. **Recommended Allocation** — % of relevant portfolio
3. **Rationale** — tailored to a {risk_profile} investor
4. **Key Risks to Monitor** (3 bullet points)
5. **Entry Strategy** (if suitable)

Be concise and actionable. Close with a one-line disclaimer."""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are a professional robo-advisor providing personalised, "
                                "risk-profile-aware investment recommendations. Always remind "
                                "users this is educational, not financial advice."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=700,
            )
            rec = response.choices[0].message.content
            logger.info("Generated recommendation for %s via GPT-4o", asset_name)
            return rec

        except Exception as exc:
            logger.error("OpenAI error: %s", exc)
            return self._fallback_recommendation(asset_name, risk_profile)

    # ------------------------------------------------------------------ #
    # Fallback templates                                                   #
    # ------------------------------------------------------------------ #

    def _fallback_analysis(self, asset_name: str, predictions: Dict) -> str:
        return f"""## Market Analysis — {asset_name.upper()}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Template mode (no API key)*

**Market Outlook**
Based on an ARIMA + Prophet ensemble, {asset_name} shows a **{predictions.get('short_term', 'mixed')}**
short-term signal with {int(float(predictions.get('confidence', 0.5)) * 100)}% model confidence.

**Key Price Drivers**
- Technical momentum from time-series analysis
- Historical volatility: {predictions.get('volatility', 'N/A')}
- Risk-adjusted performance (Sharpe): {predictions.get('sharpe_ratio', 'N/A')}
- Maximum drawdown context: {predictions.get('max_drawdown', 'N/A')}

**Risk Assessment:** {self._classify_risk(predictions.get('volatility_classification'))}

**Suggested Action:** Hold with active monitoring
**Holding Period:** Medium-term (1–3 months)

---
*This analysis is for educational purposes only and does not constitute financial advice.*"""

    def _fallback_recommendation(self, asset_name: str, risk_profile: str) -> str:
        alloc = {"Conservative": "5–20%", "Moderate": "15–35%", "Aggressive": "25–50%"}
        return f"""## Investment Recommendation — {asset_name.upper()}
*Risk Profile: {risk_profile} · Template mode (no API key)*

**Suitability:** Moderately Suitable for {risk_profile} investors

**Recommended Allocation:** {alloc.get(risk_profile, '15–30%')} of growth-oriented portfolio

**Rationale**
{asset_name} offers diversification benefits broadly aligned with {risk_profile.lower()} risk tolerance.
Current valuation and historical performance support a measured position.

**Key Risks to Monitor**
- Macroeconomic shifts (interest rates, inflation trajectory)
- Sector-specific or geopolitical volatility
- Liquidity conditions during market stress events

**Entry Strategy**
1. Start with 25–30% of the intended allocation
2. Dollar-cost average over 3–6 months
3. Set a stop-loss consistent with your risk tolerance

---
*Educational purposes only — not financial advice. Consult a licensed financial advisor.*"""

    # ------------------------------------------------------------------ #
    # Utilities                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _classify_risk(vol_str) -> str:
        if not vol_str or not isinstance(vol_str, str):
            return "Medium"
        v = vol_str.lower()
        if "very high" in v or "high" in v:
            return "High"
        if "low" in v:
            return "Low"
        return "Medium"

    @staticmethod
    def generate_full_report(asset_analysis: Dict) -> str:
        return f"""<!DOCTYPE html>
<html><head><title>Investment Report</title>
<style>
body{{font-family:Inter,sans-serif;background:#0a0f1e;color:#e2e8f0;margin:0;padding:24px}}
.card{{background:#111e3a;border:1px solid rgba(56,114,255,.14);border-radius:14px;padding:24px;margin-bottom:20px}}
.label{{color:#7c95c8;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em}}
.value{{font-size:1.4rem;font-weight:700;color:#e2e8f0;margin-top:4px}}
.disclaimer{{background:#78350f22;border:1px solid #f59e0b44;border-radius:10px;padding:14px;font-size:.8rem;color:#94a3b8}}
</style></head><body>
<div class="card">
  <div class="label">Asset</div>
  <div class="value">{asset_analysis.get('asset_name','Investment Analysis')}</div>
  <div style="color:#94a3b8;font-size:.8rem;margin-top:4px">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>
<div class="card" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div><div class="label">Current Price</div><div class="value">${asset_analysis.get('current_price',0):,.2f}</div></div>
  <div><div class="label">Trend</div><div class="value">{asset_analysis.get('trend','N/A')}</div></div>
  <div><div class="label">Volatility</div><div class="value">{asset_analysis.get('volatility',0):.1f}%</div></div>
  <div><div class="label">Risk Level</div><div class="value">{asset_analysis.get('risk_level','N/A')}</div></div>
</div>
<div class="disclaimer">⚠️ This report is for educational purposes only and does not constitute financial advice.
Past performance does not guarantee future results. All investments carry risk.</div>
</body></html>"""
