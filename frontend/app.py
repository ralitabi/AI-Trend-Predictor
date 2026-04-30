"""
AI Trend Predictor — SaaS Edition
Professional full-dashboard financial analysis system
"""

import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from analysis.risk_analysis import RiskAnalysis, RiskMetrics
from analysis.suggestions import SuggestionsEngine
from data.market_data import MacroeconomicData, MarketDataCollector
from models.predictors import EnsemblePredictor
from reporting.report_generator import AIReportGenerator

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════
D = {
    "bg0":      "#02060F",   # deepest background
    "bg1":      "#070E21",   # main page background
    "bg2":      "#0D1630",   # surface / sidebar
    "card":     "#111E3A",   # card fill
    "card2":    "#172444",   # elevated card
    "border":   "rgba(56,114,255,0.14)",
    "glow":     "rgba(56,114,255,0.30)",
    "blue":     "#3B82F6",
    "indigo":   "#6366F1",
    "teal":     "#14B8A6",
    "gold":     "#F59E0B",
    "green":    "#10B981",
    "red":      "#EF4444",
    "purple":   "#8B5CF6",
    "text1":    "#EEF2FF",
    "text2":    "#7C95C8",
    "text3":    "#3D5577",
    "radius":   "14px",
}

CHART = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(11,20,48,0.85)",
    font=dict(family="'Inter','Segoe UI',system-ui,sans-serif", color=D["text1"], size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)", zeroline=False, showgrid=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)", zeroline=False, showgrid=True),
    margin=dict(l=52, r=24, t=56, b=44),
    legend=dict(bgcolor="rgba(7,14,33,0.75)", bordercolor=D["border"], borderwidth=1, orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    hoverlabel=dict(bgcolor=D["card2"], bordercolor=D["border"], font_size=13),
)

ASSETS = {
    "Gold · GC=F":        ("gold",    "GC=F",    "Gold",    D["gold"],   "XAU/USD"),
    "S&P 500 · ^GSPC":   ("sp500",   "^GSPC",   "S&P 500", D["blue"],   "INDEX"),
    "Bitcoin · BTC-USD":  ("bitcoin", "BTC-USD", "Bitcoin", D["purple"], "BTC/USD"),
}

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Trend Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS — FULL DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(f"""
<style>
/* ── Fonts ───────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-feature-settings: "cv02","cv03","cv04","cv11";
}}

/* ── App shell ───────────────────────────────────────────────────────── */
.stApp {{
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(56,114,255,0.08) 0%, transparent 60%),
                linear-gradient(180deg, {D["bg0"]} 0%, {D["bg1"]} 100%);
    min-height: 100vh;
}}
.main .block-container {{
    padding: 0.6rem 2rem 3rem 2rem !important;
    max-width: 1500px !important;
}}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {D["bg2"]} 0%, {D["bg0"]} 100%) !important;
    border-right: 1px solid {D["border"]} !important;
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stCheckbox label span,
section[data-testid="stSidebar"] .stTextInput label {{
    color: {D["text2"]} !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stTextInput input {{
    background: {D["card"]} !important;
    border: 1px solid {D["border"]} !important;
    color: {D["text1"]} !important;
    border-radius: 8px !important;
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
    color: {D["text1"]};
}}

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {D["bg2"]};
    border-radius: 12px;
    padding: 5px 6px;
    gap: 2px;
    border: 1px solid {D["border"]};
    margin-bottom: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {D["text2"]} !important;
    border-radius: 9px !important;
    padding: 9px 20px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    border: none !important;
    transition: all 0.18s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: {D["card"]} !important;
    color: {D["text1"]} !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {D["blue"]}22, {D["indigo"]}33) !important;
    color: {D["blue"]} !important;
    box-shadow: 0 0 0 1px {D["blue"]}44, 0 2px 12px rgba(59,130,246,0.2) !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding: 0 !important;
}}

/* ── Metrics ─────────────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {{
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: {D["text1"]} !important;
    font-variant-numeric: tabular-nums;
}}
[data-testid="stMetricLabel"] > div {{
    color: {D["text2"]} !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 500 !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {D["blue"]} 0%, {D["indigo"]} 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 2.2rem !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(59,130,246,0.5) !important;
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
}}

/* ── Dataframe ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid {D["border"]} !important;
}}
[data-testid="stDataFrame"] table {{
    background: {D["card"]} !important;
}}
[data-testid="stDataFrame"] th {{
    background: {D["card2"]} !important;
    color: {D["text2"]} !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid {D["border"]} !important;
}}
[data-testid="stDataFrame"] td {{
    color: {D["text1"]} !important;
    font-size: 0.87rem !important;
    font-variant-numeric: tabular-nums;
    border-bottom: 1px solid {D["border"]} !important;
    padding: 9px 14px !important;
}}

/* ── Spinner ─────────────────────────────────────────────────────────── */
.stSpinner > div {{ border-top-color: {D["blue"]} !important; }}

/* ── Checkbox ────────────────────────────────────────────────────────── */
.stCheckbox label span {{ font-size: 0.85rem !important; }}

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {D["bg0"]}; }}
::-webkit-scrollbar-thumb {{ background: {D["card2"]}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {D["blue"]}66; }}

/* ── Alerts ──────────────────────────────────────────────────────────── */
.stAlert {{ border-radius: 10px !important; }}

/* ── Plotly charts ───────────────────────────────────────────────────── */
.js-plotly-plot .plotly {{ border-radius: 12px; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HTML COMPONENT BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _rgb(h: str) -> str:
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


def ticker_bar(prices: dict):
    """Animated live-prices ticker strip at the top of the page."""
    items = []
    for key, (label, chg, color) in prices.items():
        arrow = "▲" if chg >= 0 else "▼"
        items.append(f"""
        <div class="t-item">
            <span class="t-sym">{key}</span>
            <span class="t-price">{label}</span>
            <span class="t-chg" style="color:{color}">{arrow} {abs(chg):.2f}%</span>
        </div>
        <div class="t-sep">·</div>
        """)
    row = "".join(items * 4)   # repeat for seamless loop
    html = f"""
    <style>
    .ticker-wrap {{
        background: linear-gradient(90deg, {D["bg2"]} 0%, {D["card"]} 50%, {D["bg2"]} 100%);
        border-bottom: 1px solid {D["border"]};
        border-top: 1px solid {D["border"]};
        overflow: hidden;
        padding: 0;
        height: 36px;
        display: flex;
        align-items: center;
        margin: 0 -2rem 0 -2rem;
        position: relative;
    }}
    .ticker-wrap::before, .ticker-wrap::after {{
        content: '';
        position: absolute;
        top: 0; bottom: 0;
        width: 80px;
        z-index: 2;
    }}
    .ticker-wrap::before {{ left: 0; background: linear-gradient(90deg, {D["bg2"]}, transparent); }}
    .ticker-wrap::after  {{ right: 0; background: linear-gradient(270deg, {D["bg2"]}, transparent); }}
    .ticker-track {{
        display: flex;
        align-items: center;
        animation: scroll-left 38s linear infinite;
        white-space: nowrap;
        gap: 0;
    }}
    .t-item {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0 20px;
    }}
    .t-sym  {{ color: {D["text2"]}; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }}
    .t-price {{ color: {D["text1"]}; font-size: 0.82rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
    .t-chg  {{ font-size: 0.75rem; font-weight: 600; }}
    .t-sep  {{ color: {D["text3"]}; font-size: 0.7rem; }}
    @keyframes scroll-left {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-25%); }}
    }}
    </style>
    <div class="ticker-wrap">
        <div class="ticker-track">{row}</div>
    </div>
    """
    components.html(html, height=38, scrolling=False)


def hero(asset_name: str, pair: str, price: float, chg5d: float, hi: float, lo: float, color: str):
    chg_color = D["green"] if chg5d >= 0 else D["red"]
    arrow = "▲" if chg5d >= 0 else "▼"
    from_lo = (price - lo) / (hi - lo) * 100 if hi != lo else 50
    return f"""
    <div style="
        background: linear-gradient(135deg,{D['card']} 0%,{D['bg2']} 60%,{D['bg0']} 100%);
        border: 1px solid {D['border']};
        border-radius: 18px;
        padding: 28px 36px 22px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    ">
        <!-- Glow blob -->
        <div style="position:absolute;top:-80px;right:-80px;width:300px;height:300px;
                    background:radial-gradient({color},{color}00 70%);opacity:0.08;border-radius:50%;pointer-events:none;"></div>

        <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:16px;">
            <!-- Left: name + price -->
            <div>
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
                    <span style="color:{color};font-size:0.72rem;font-weight:700;text-transform:uppercase;
                                 letter-spacing:0.14em;background:{color}18;border:1px solid {color}44;
                                 padding:3px 10px;border-radius:100px;">{pair}</span>
                    <span style="color:{D['text3']};font-size:0.72rem;">AI Trend Predictor</span>
                </div>
                <div style="color:{D['text1']};font-size:2.4rem;font-weight:800;line-height:1;letter-spacing:-0.02em;
                            font-variant-numeric:tabular-nums;">{asset_name}</div>
                <div style="display:flex;align-items:baseline;gap:16px;margin-top:8px;">
                    <span style="color:{D['text1']};font-size:2.8rem;font-weight:900;letter-spacing:-0.03em;
                                 font-variant-numeric:tabular-nums;">${price:,.2f}</span>
                    <span style="color:{chg_color};font-size:1.1rem;font-weight:700;">
                        {arrow} {abs(chg5d):.2f}%
                        <span style="color:{D['text3']};font-size:0.8rem;font-weight:400;"> 5d</span>
                    </span>
                </div>
            </div>
            <!-- Right: 52-week range -->
            <div style="min-width:220px;">
                <div style="color:{D['text2']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">52-Week Range</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:{D['red']};font-size:0.82rem;font-weight:600;">${lo:,.0f}</span>
                    <span style="color:{D['green']};font-size:0.82rem;font-weight:600;">${hi:,.0f}</span>
                </div>
                <div style="background:{D['bg0']};border-radius:100px;height:6px;position:relative;overflow:hidden;">
                    <div style="position:absolute;left:0;top:0;bottom:0;width:{from_lo:.1f}%;
                                background:linear-gradient(90deg,{D['red']},{color},{D['green']});border-radius:100px;"></div>
                </div>
                <div style="color:{D['text3']};font-size:0.7rem;margin-top:4px;text-align:center;">
                    Position in range: {from_lo:.0f}%
                </div>
            </div>
        </div>
    </div>
    """


def kpi(label: str, value: str, sub: str = "", icon: str = "◆",
        color: str = None, glow: bool = False) -> str:
    color = color or D["blue"]
    shadow = f"0 0 24px {color}28, 0 2px 16px rgba(0,0,0,0.35)" if glow else "0 2px 16px rgba(0,0,0,0.28)"
    return f"""
    <div style="
        background: linear-gradient(135deg,{D['card']} 0%,{D['bg2']} 100%);
        border: 1px solid {D['border']};
        border-top: 2px solid {color}66;
        border-radius: 14px;
        padding: 20px 22px 18px;
        box-shadow: {shadow};
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    ">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <span style="width:28px;height:28px;background:{color}18;border-radius:7px;
                         display:flex;align-items:center;justify-content:center;font-size:0.9rem;">{icon}</span>
            <span style="color:{D['text2']};font-size:0.7rem;text-transform:uppercase;
                         letter-spacing:0.1em;font-weight:600;">{label}</span>
        </div>
        <div style="color:{D['text1']};font-size:1.6rem;font-weight:800;line-height:1;
                    font-variant-numeric:tabular-nums;letter-spacing:-0.02em;">{value}</div>
        <div style="color:{D['text3']};font-size:0.76rem;margin-top:8px;font-weight:400;">{sub}</div>
    </div>
    """


def section_title(title: str, badge: str = "", sub: str = ""):
    badge_html = f'<span style="background:{D["blue"]}22;color:{D["blue"]};border:1px solid {D["blue"]}44;border-radius:100px;padding:2px 10px;font-size:0.7rem;font-weight:600;letter-spacing:0.06em;">{badge}</span>' if badge else ""
    sub_html   = f'<div style="color:{D["text3"]};font-size:0.78rem;margin-top:3px;">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div style="margin:22px 0 14px;">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span style="color:{D['text1']};font-size:1.12rem;font-weight:700;letter-spacing:-0.01em;">{title}</span>
            {badge_html}
        </div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def action_card(action: str, confidence: float, risk: str, holding: str):
    cfg = {
        "Buy":        (D["green"],  D["green"]  + "18", "▲ BUY",        "Strong bullish signal"),
        "Accumulate": (D["teal"],   D["teal"]   + "18", "◆ ACCUMULATE", "Gradual entry advised"),
        "Hold":       (D["gold"],   D["gold"]   + "18", "● HOLD",       "Maintain position"),
        "Sell":       (D["red"],    D["red"]    + "18", "▼ SELL",       "Exit or reduce position"),
    }
    col, bg, label, hint = cfg.get(action, (D["blue"], D["blue"] + "18", action.upper(), ""))
    risk_color = D["green"] if risk == "Low" else D["gold"] if risk == "Medium" else D["red"]
    return f"""
    <div style="background:{D['card']};border:1px solid {D['border']};border-radius:16px;padding:28px;text-align:center;margin:8px 0;">
        <div style="display:inline-flex;flex-direction:column;align-items:center;
                    background:{bg};border:2px solid {col}66;border-radius:16px;
                    padding:22px 56px;box-shadow:0 0 48px {col}28;margin-bottom:20px;">
            <div style="color:{col};font-size:2rem;font-weight:900;letter-spacing:0.06em;">{label}</div>
            <div style="color:{D['text2']};font-size:0.82rem;margin-top:4px;">{hint}</div>
        </div>
        <div style="display:flex;justify-content:center;gap:32px;flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Confidence</div>
                <div style="color:{col};font-size:1.4rem;font-weight:800;">{int(confidence*100)}%</div>
            </div>
            <div style="text-align:center;">
                <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Risk Level</div>
                <div style="color:{risk_color};font-size:1.4rem;font-weight:800;">{risk}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Hold Period</div>
                <div style="color:{D['text1']};font-size:1.4rem;font-weight:800;">{holding}</div>
            </div>
        </div>
    </div>
    """


def price_target_row(entry: float, target: float, stop: float, upside: float, downside: float):
    rr = abs(upside / downside) if downside != 0 else 0
    return f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin:12px 0;">
        <div style="background:{D['card']};border:1px solid {D['border']};border-radius:12px;padding:16px;text-align:center;">
            <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Entry</div>
            <div style="color:{D['text1']};font-size:1.3rem;font-weight:800;font-variant-numeric:tabular-nums;">${entry:,.2f}</div>
        </div>
        <div style="background:{D['card']};border:1px solid {D['green']}44;border-radius:12px;padding:16px;text-align:center;
                    box-shadow:0 0 20px {D['green']}18;">
            <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Target</div>
            <div style="color:{D['green']};font-size:1.3rem;font-weight:800;font-variant-numeric:tabular-nums;">${target:,.2f}</div>
            <div style="color:{D['green']};font-size:0.75rem;margin-top:2px;">▲ {upside:.2f}%</div>
        </div>
        <div style="background:{D['card']};border:1px solid {D['red']}44;border-radius:12px;padding:16px;text-align:center;
                    box-shadow:0 0 20px {D['red']}18;">
            <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Stop Loss</div>
            <div style="color:{D['red']};font-size:1.3rem;font-weight:800;font-variant-numeric:tabular-nums;">${stop:,.2f}</div>
            <div style="color:{D['red']};font-size:0.75rem;margin-top:2px;">▼ {abs(downside):.2f}%</div>
        </div>
        <div style="background:{D['card']};border:1px solid {D['border']};border-radius:12px;padding:16px;text-align:center;">
            <div style="color:{D['text3']};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Risk/Reward</div>
            <div style="color:{D['gold']};font-size:1.3rem;font-weight:800;">{rr:.2f}x</div>
        </div>
    </div>
    """


def disclaimer_bar():
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,{D['gold']}0A,{D['gold']}14,{D['gold']}0A);
                border:1px solid {D['gold']}30;border-radius:10px;padding:11px 18px;
                display:flex;align-items:center;gap:12px;margin:10px 0;font-size:0.78rem;color:{D['text2']};">
        <span style="font-size:1rem;flex-shrink:0;">⚠️</span>
        <span>
            <strong style="color:{D['gold']};">Educational use only.</strong>
            This system does not constitute financial advice. All investments carry risk, including loss of principal.
            Past performance does not guarantee future results. Consult a licensed financial advisor.
        </span>
    </div>
    """, unsafe_allow_html=True)


def divider():
    st.markdown(f'<div style="height:1px;background:{D["border"]};margin:18px 0;"></div>', unsafe_allow_html=True)


def info_box(text: str, color: str = None):
    color = color or D["blue"]
    st.markdown(f"""
    <div style="background:{color}12;border:1px solid {color}35;border-left:3px solid {color};
                border-radius:10px;padding:14px 18px;font-size:0.86rem;color:{D['text1']};
                line-height:1.65;margin:10px 0;">{text}</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _apply(fig: go.Figure, height: int = 420, title: str = "") -> go.Figure:
    layout = dict(**CHART, height=height)
    if title:
        layout["title"] = dict(text=title, font=dict(size=13, color=D["text1"]), x=0.01, y=0.97)
    fig.update_layout(**layout)
    return fig


def ch_price(prices: pd.Series, name: str, color: str, forecast=None, ci=None) -> go.Figure:
    fig = go.Figure()
    rgb = _rgb(color)
    fig.add_trace(go.Scatter(
        x=prices.index, y=prices, name="Price",
        fill="tozeroy", fillcolor=f"rgba({rgb},0.07)",
        line=dict(color=color, width=2.5),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>$%{y:,.2f}<extra></extra>",
    ))
    if len(prices) >= 20:
        fig.add_trace(go.Scatter(x=prices.index, y=prices.rolling(20).mean(), name="MA 20",
            line=dict(color=D["text3"], width=1.2, dash="dot"), hoverinfo="skip"))
    if len(prices) >= 50:
        fig.add_trace(go.Scatter(x=prices.index, y=prices.rolling(50).mean(), name="MA 50",
            line=dict(color=D["purple"] + "99", width=1.2, dash="dot"), hoverinfo="skip"))
    if forecast is not None and len(forecast) > 0:
        fd = pd.date_range(prices.index[-1] + timedelta(days=1), periods=len(forecast), freq="D")
        if ci:
            fig.add_trace(go.Scatter(
                x=list(fd) + list(fd[::-1]),
                y=list(ci["upper_ci"]) + list(ci["lower_ci"][::-1]),
                fill="toself", fillcolor=f"rgba({_rgb(D['gold'])},0.10)",
                line=dict(color="rgba(0,0,0,0)"), name="90% CI", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=fd, y=forecast, name="Forecast",
            line=dict(color=D["gold"], width=2, dash="dash"),
            hovertemplate="<b>%{x|%b %d}</b><br>Forecast $%{y:,.2f}<extra></extra>"))
    return _apply(fig, 460, f"{name} · Price History")


def ch_forecast(prices: pd.Series, name: str, preds: dict, ci: dict, days: int) -> go.Figure:
    fig = go.Figure()
    hist = prices.tail(90)
    fd   = pd.date_range(prices.index[-1] + timedelta(days=1), periods=days, freq="D")
    fig.add_trace(go.Scatter(x=hist.index, y=hist, name="Historical",
        line=dict(color=D["blue"], width=2.5),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>$%{y:,.2f}<extra></extra>"))
    if ci:
        fig.add_trace(go.Scatter(
            x=list(fd) + list(fd[::-1]),
            y=list(ci["upper_ci"]) + list(ci["lower_ci"][::-1]),
            fill="toself", fillcolor=f"rgba({_rgb(D['gold'])},0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="90% CI", hoverinfo="skip"))
    colors_m = {"arima": D["blue"] + "CC", "prophet": D["purple"] + "CC"}
    for m, clr in colors_m.items():
        p = preds.get(m)
        if p is not None and len(p) > 0:
            fig.add_trace(go.Scatter(x=fd, y=p, name=m.upper(),
                line=dict(color=clr, width=1.5, dash="dot"), hoverinfo="skip"))
    ens = preds.get("ensemble")
    if ens is not None and len(ens) > 0:
        fig.add_trace(go.Scatter(x=fd, y=ens, name="Ensemble",
            line=dict(color=D["gold"], width=3),
            hovertemplate="<b>%{x|%b %d}</b><br>$%{y:,.2f}<extra></extra>"))
    return _apply(fig, 460, f"{name} · {days}-Day Forecast + 90% CI")


def ch_volatility(prices: pd.Series, name: str) -> go.Figure:
    vol = prices.pct_change().mul(100).rolling(20).std().mul(np.sqrt(252))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vol.index, y=vol, name="Ann. Vol (%)",
        fill="tozeroy", fillcolor=f"rgba({_rgb(D['red'])},0.10)",
        line=dict(color=D["red"], width=2),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f}%<extra></extra>"))
    for lvl, lbl in [(15, "Low"), (25, "Moderate"), (35, "High")]:
        fig.add_hline(y=lvl, line=dict(color="rgba(255,255,255,0.12)", dash="dot", width=1),
                      annotation_text=lbl, annotation_position="right",
                      annotation_font=dict(color=D["text3"], size=10))
    return _apply(fig, 320, f"{name} · 20-Day Rolling Volatility (Ann.)")


def ch_returns(prices: pd.Series, name: str) -> go.Figure:
    r = prices.pct_change().dropna().mul(100)
    mu, sig = r.mean(), r.std()
    x = np.linspace(r.min(), r.max(), 200)
    y = (1 / (sig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sig) ** 2)
    y *= len(r) * (r.max() - r.min()) / 55
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=r, nbinsx=55, name="Daily Return",
        marker=dict(color=D["blue"] + "CC", line=dict(color=D["border"], width=0.5)),
        hovertemplate="Return %{x:.2f}%<br>Count %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=y, name="Normal fit",
        line=dict(color=D["gold"], width=2.5), hoverinfo="skip"))
    return _apply(fig, 320, f"{name} · Daily Returns Distribution")


def ch_drawdown(prices: pd.Series, name: str) -> go.Figure:
    dd = (prices - prices.cummax()) / prices.cummax() * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd.index, y=dd, name="Drawdown %",
        fill="tozeroy", fillcolor=f"rgba({_rgb(D['red'])},0.15)",
        line=dict(color=D["red"], width=1.5),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f}%<extra></extra>"))
    fig.update_layout(yaxis=dict(ticksuffix="%"))
    return _apply(fig, 290, f"{name} · Drawdown from Peak")


def ch_compare(all_data: dict) -> go.Figure:
    KEY_CFG = {"gold": (D["gold"], "Gold"), "sp500": (D["blue"], "S&P 500"), "bitcoin": (D["purple"], "Bitcoin")}
    fig = go.Figure()
    for key, (clr, lbl) in KEY_CFG.items():
        df = all_data.get(key, pd.DataFrame())
        if df.empty: continue
        s = _close(df)
        norm = s / s.iloc[0] * 100
        fig.add_trace(go.Scatter(x=norm.index, y=norm, name=lbl,
            line=dict(color=clr, width=2.5),
            hovertemplate=f"<b>{lbl}</b><br>%{{x|%b %d %Y}}<br>%{{y:.1f}}<extra></extra>"))
    fig.add_hline(y=100, line=dict(color="rgba(255,255,255,0.15)", dash="dot", width=1))
    return _apply(fig, 420, "Normalised Performance (base = 100)")


def ch_correlation(all_data: dict):
    KEY_CFG = {"gold": "Gold", "sp500": "S&P 500", "bitcoin": "Bitcoin"}
    rets = {}
    for key, lbl in KEY_CFG.items():
        df = all_data.get(key, pd.DataFrame())
        if not df.empty: rets[lbl] = _close(df).pct_change()
    if len(rets) < 2: return None
    corr = pd.DataFrame(rets).dropna().corr()
    fig = px.imshow(corr, text_auto=".2f",
        color_continuous_scale=[[0, D["red"]], [0.5, D["bg2"]], [1, D["blue"]]],
        zmin=-1, zmax=1)
    return _apply(fig, 320, "Return Correlation Matrix")


def ch_volume_profile(prices: pd.Series, name: str) -> go.Figure:
    """Monthly return bar chart as a proxy for seasonality."""
    monthly = prices.resample("ME").last().pct_change().dropna() * 100
    colors = [D["green"] if v >= 0 else D["red"] for v in monthly]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly.index, y=monthly,
        name="Monthly Return",
        marker=dict(color=colors, opacity=0.85,
                    line=dict(color=[D["green"] + "66" if v >= 0 else D["red"] + "66" for v in monthly], width=1)),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y:.2f}%<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.2)", width=1))
    return _apply(fig, 280, f"{name} · Monthly Returns")


# ══════════════════════════════════════════════════════════════════════════════
#  DATA / CACHE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _close(df: pd.DataFrame) -> pd.Series:
    for col in ("adj close", "close", "Close", "Adj Close"):
        if col in df.columns:
            return df[col].dropna()
    return df.iloc[:, 0].dropna()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all(lookback: int = 365) -> dict:
    c = MarketDataCollector(lookback_days=lookback)
    return {"gold": c.get_gold_data(), "sp500": c.get_sp500_data(),
            "bitcoin": c.get_bitcoin_data(), "vix": c.get_vix_data()}


def get_preds(key: str, days: int, lstm: bool) -> dict:
    sk = f"p_{key}_{days}_{lstm}"
    if sk not in st.session_state:
        df = st.session_state.mdata[key]
        if df.empty:
            st.session_state[sk] = {}
            return {}
        prices = _close(df)
        e = EnsemblePredictor()
        e.fit_all_models(prices, use_lstm=lstm)
        st.session_state[sk] = {
            "preds": e.predict_ensemble(days, use_lstm=lstm),
            "ci":    e.predict_with_confidence_intervals(days, use_lstm=lstm),
        }
    return st.session_state[sk]


def get_risk(key: str, name: str) -> dict:
    sk = f"r_{key}"
    if sk not in st.session_state:
        df = st.session_state.mdata[key]
        if df.empty:
            st.session_state[sk] = {}
            return {}
        prices = _close(df)
        st.session_state[sk] = RiskMetrics().get_risk_summary(prices, name)
    return st.session_state[sk]


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def build_sidebar() -> tuple:
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:20px 16px 18px;border-bottom:1px solid {D['border']};margin-bottom:18px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:36px;height:36px;background:linear-gradient(135deg,{D['blue']},{D['indigo']});
                            border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📊</div>
                <div>
                    <div style="color:{D['text1']};font-weight:800;font-size:0.95rem;letter-spacing:0.02em;">AI Terminal</div>
                    <div style="color:{D['blue']};font-size:0.65rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;">Investment · SaaS</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # API Key
        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin-bottom:4px;'>🔑 OpenAI API Key</p>", unsafe_allow_html=True)
        api_key = st.text_input("api_key", value=os.getenv("OPENAI_API_KEY", ""),
                                 type="password", placeholder="sk-proj-...",
                                 label_visibility="collapsed")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.markdown(f"<p style='color:{D['green']};font-size:0.73rem;margin-top:2px;'>✓ GPT-4o enabled</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{D['text3']};font-size:0.73rem;margin-top:2px;'>Template reports (no key)</p>", unsafe_allow_html=True)

        st.markdown(f"<div style='height:1px;background:{D['border']};margin:14px 0;'></div>", unsafe_allow_html=True)

        # Asset
        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin-bottom:4px;'>Asset</p>", unsafe_allow_html=True)
        asset_choice = st.selectbox("asset", list(ASSETS.keys()), label_visibility="collapsed")
        asset_key, ticker, asset_name, asset_color, pair = ASSETS[asset_choice]

        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin:12px 0 4px;'>Risk Profile</p>", unsafe_allow_html=True)
        risk_profile = st.selectbox("risk", ["Conservative", "Moderate", "Aggressive"], label_visibility="collapsed")

        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin:12px 0 4px;'>Forecast Horizon</p>", unsafe_allow_html=True)
        forecast_days = st.slider("days", 5, 30, 7, label_visibility="collapsed")

        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin:12px 0 6px;'>Models</p>", unsafe_allow_html=True)
        use_lstm = st.checkbox("Include LSTM  *(slow)*", value=False)

        # Macro
        st.markdown(f"<div style='height:1px;background:{D['border']};margin:14px 0;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{D['text3']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;margin-bottom:10px;'>🌐 Macro Indicators</p>", unsafe_allow_html=True)
        macro = MacroeconomicData.get_economic_indicators()
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:{D['text3']};font-size:0.78rem;">Inflation Est.</span>
                <span style="color:{D['gold']};font-size:0.82rem;font-weight:700;background:{D['gold']}18;padding:2px 8px;border-radius:6px;">{macro['inflation']:.1f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:{D['text3']};font-size:0.78rem;">Fed Funds Rate</span>
                <span style="color:{D['blue']};font-size:0.82rem;font-weight:700;background:{D['blue']}18;padding:2px 8px;border-radius:6px;">{macro['interest_rate']:.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Footer
        st.markdown(f"""
        <div style="margin-top:auto;padding:16px 0 0;border-top:1px solid {D['border']};margin-top:20px;text-align:center;">
            <div style="color:{D['text3']};font-size:0.68rem;">v2.0 · {datetime.now().strftime('%Y-%m-%d')}</div>
            <div style="color:{D['text3']};font-size:0.65rem;margin-top:2px;">Educational purposes only</div>
        </div>
        """, unsafe_allow_html=True)

    return asset_key, ticker, asset_name, asset_color, pair, risk_profile, forecast_days, use_lstm


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    inject_css()

    asset_key, ticker, asset_name, asset_color, pair, risk_profile, forecast_days, use_lstm = build_sidebar()

    # ── Load data ─────────────────────────────────────────────────────────────
    if "mdata" not in st.session_state:
        with st.spinner("Loading market data…"):
            st.session_state.mdata = fetch_all(lookback=365)

    all_data = st.session_state.mdata
    data = all_data.get(asset_key, pd.DataFrame())

    if data.empty:
        st.error(f"Could not load data for {asset_name}. Check your internet connection and try refreshing.")
        return

    prices = _close(data)
    cur   = float(prices.iloc[-1])
    chg5  = (cur - float(prices.iloc[-5])) / float(prices.iloc[-5]) * 100
    hi52  = float(prices.tail(252).max())
    lo52  = float(prices.tail(252).min())

    # ── Ticker bar ────────────────────────────────────────────────────────────
    ticker_prices = {}
    TICKER_KEYS = {
        "GOLD":  ("gold",    D["gold"]),
        "SPX":   ("sp500",   D["blue"]),
        "BTC":   ("bitcoin", D["purple"]),
    }
    for sym, (key, clr) in TICKER_KEYS.items():
        df = all_data.get(key, pd.DataFrame())
        if not df.empty:
            s = _close(df)
            p = float(s.iloc[-1])
            c = (p - float(s.iloc[-2])) / float(s.iloc[-2]) * 100 if len(s) > 1 else 0
            lbl = f"${p:,.0f}" if p > 10000 else f"${p:,.2f}"
            chg_col = D["green"] if c >= 0 else D["red"]
            ticker_prices[sym] = (lbl, c, chg_col)
    ticker_bar(ticker_prices)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(hero(asset_name, pair, cur, chg5, hi52, lo52, asset_color), unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    ret30 = (cur - float(prices.iloc[-22])) / float(prices.iloc[-22]) * 100 if len(prices) > 22 else 0
    ytd   = (cur - float(prices.iloc[0]))  / float(prices.iloc[0])  * 100
    vol20 = float(prices.pct_change().tail(20).std() * np.sqrt(252) * 100)
    vix   = _close(all_data.get("vix", pd.DataFrame()))
    vix_v = f"{float(vix.iloc[-1]):.1f}" if not vix.empty else "N/A"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi("Current Price",   f"${cur:,.2f}",    f"{'▲' if chg5>=0 else '▼'} {abs(chg5):.2f}% (5d)",  "💰", asset_color, glow=True), unsafe_allow_html=True)
    c2.markdown(kpi("52-Week High",    f"${hi52:,.0f}",   "Peak in range",          "🏔️", D["green"]),   unsafe_allow_html=True)
    c3.markdown(kpi("30-Day Return",   f"{ret30:+.2f}%",  f"YTD: {ytd:+.1f}%",     "📅", D["blue"]  if ret30>=0 else D["red"]), unsafe_allow_html=True)
    c4.markdown(kpi("Volatility (20d)",f"{vol20:.1f}%",   "Annualised std dev",     "🌊", D["gold"]),    unsafe_allow_html=True)
    c5.markdown(kpi("VIX Index",       vix_v,             "Fear & greed indicator", "😰", D["purple"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    disclaimer_bar()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📈  Price Analysis",
        "🔮  Forecast",
        "⚠️  Risk",
        "💡  Recommendations",
        "🤖  AI Report",
        "🔄  Compare",
    ])

    # ── T1: Price Analysis ────────────────────────────────────────────────────
    with t1:
        cached = st.session_state.get(f"p_{asset_key}_{forecast_days}_{use_lstm}", {})
        fc  = cached.get("preds", {}).get("ensemble")
        ci  = cached.get("ci")
        st.plotly_chart(ch_price(prices, asset_name, asset_color, fc, ci), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(ch_volatility(prices, asset_name), use_container_width=True)
        with c2: st.plotly_chart(ch_returns(prices, asset_name), use_container_width=True)

        st.plotly_chart(ch_volume_profile(prices, asset_name), use_container_width=True)

    # ── T2: Forecast ──────────────────────────────────────────────────────────
    with t2:
        section_title("Price Forecast", badge=f"{forecast_days}d horizon",
                      sub="ARIMA + Prophet weighted ensemble with 90% confidence interval")

        with st.spinner("Fitting ARIMA & Prophet…"):
            try:
                pc    = get_preds(asset_key, forecast_days, use_lstm)
                preds = pc.get("preds", {})
                ci    = pc.get("ci", {})
                ens   = preds.get("ensemble", np.array([]))
            except Exception as e:
                st.error(f"Prediction error: {e}")
                preds, ci, ens = {}, {}, np.array([])

        if len(ens) > 0:
            pred_price = float(ens[-1])
            pred_chg   = (pred_price - cur) / cur * 100
            pclr       = D["green"] if pred_chg >= 0 else D["red"]
            ci_hi      = float(ci["upper_ci"][-1]) if ci else 0
            ci_lo      = float(ci["lower_ci"][-1]) if ci else 0

            c1, c2, c3 = st.columns(3)
            c1.markdown(kpi(f"Forecast ({forecast_days}d)", f"${pred_price:,.2f}",
                             f"{'▲' if pred_chg>=0 else '▼'} {abs(pred_chg):.2f}% expected", "🔮", pclr, glow=True), unsafe_allow_html=True)
            c2.markdown(kpi("CI Upper (90%)", f"${ci_hi:,.2f}", "Optimistic scenario", "⬆️", D["green"]), unsafe_allow_html=True)
            c3.markdown(kpi("CI Lower (90%)", f"${ci_lo:,.2f}", "Conservative scenario", "⬇️", D["red"]), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(ch_forecast(prices, asset_name, preds, ci, forecast_days), use_container_width=True)

            divider()
            section_title("Model Comparison")
            rows = []
            for m, arr in preds.items():
                if len(arr) > 0:
                    d = (float(arr[-1]) - cur) / cur * 100
                    rows.append({"Model": m.upper(), "1-Day": f"${float(arr[0]):,.2f}",
                                 f"{forecast_days}-Day": f"${float(arr[-1]):,.2f}",
                                 "Expected Δ": f"{'▲' if d>=0 else '▼'} {abs(d):.2f}%",
                                 "Signal": "Bullish 📈" if d > 0 else "Bearish 📉"})
            st.dataframe(pd.DataFrame(rows).set_index("Model"), use_container_width=True)

            info_box(f"<strong>Ensemble logic:</strong> ARIMA (statistical baseline) 30% · Prophet (trend+seasonality) 40% · {'LSTM (deep learning) 30%' if use_lstm else 'LSTM disabled — enable in sidebar for higher accuracy'}. The shaded region is the 90% confidence interval derived from ARIMA forecast bounds.")

    # ── T3: Risk ──────────────────────────────────────────────────────────────
    with t3:
        section_title("Risk & Volatility Analysis", sub="Sharpe, VaR, CVaR, max drawdown, skewness")

        try:
            rm = get_risk(asset_key, asset_name)
            if not rm:
                st.warning("Insufficient data for risk analysis.")
            else:
                vol     = rm.get("volatility_pct", 0)
                sharpe  = rm.get("sharpe_ratio", 0)
                dd      = rm.get("max_drawdown_pct", 0)
                var95   = rm.get("var_95_pct", 0)
                cvar95  = rm.get("cvar_95_pct", 0)
                ann_ret = rm.get("annual_return", 0)
                dd_days = rm.get("max_drawdown_duration_days", 0)
                skew    = rm.get("skewness", 0)
                kurt    = rm.get("kurtosis", 0)

                sh_clr  = D["green"] if sharpe > 1 else D["gold"] if sharpe > 0 else D["red"]
                vol_clr = D["green"] if vol < 15 else D["gold"] if vol < 25 else D["red"]
                ret_clr = D["green"] if ann_ret > 0 else D["red"]

                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(kpi("Annual Return",  f"{ann_ret:+.1f}%",   "YoY performance",  "📈", ret_clr, glow=True), unsafe_allow_html=True)
                c2.markdown(kpi("Volatility",     f"{vol:.1f}%",        rm.get("volatility_classification", ""), "🌊", vol_clr), unsafe_allow_html=True)
                c3.markdown(kpi("Sharpe Ratio",   f"{sharpe:.2f}",      ">1 = good risk-adj.", "⚖️", sh_clr), unsafe_allow_html=True)
                c4.markdown(kpi("Max Drawdown",   f"{dd:.1f}%",         f"Duration: {dd_days}d", "📉", D["red"]), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c5, c6, c7, c8 = st.columns(4)
                c5.markdown(kpi("VaR (95%)",  f"{var95:.2f}%",  "Daily loss threshold", "🛡️", D["purple"]), unsafe_allow_html=True)
                c6.markdown(kpi("CVaR (95%)", f"{cvar95:.2f}%", "Expected shortfall",   "⚡", D["red"]),    unsafe_allow_html=True)
                c7.markdown(kpi("Skewness",   f"{skew:.3f}",    "Left<0 = tail risk",   "📐", D["gold"]),   unsafe_allow_html=True)
                c8.markdown(kpi("Kurtosis",   f"{kurt:.2f}",    ">3 = fat tails",       "📏", D["teal"]),   unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(ch_drawdown(prices, asset_name), use_container_width=True)
                with c2: st.plotly_chart(ch_volatility(prices, asset_name), use_container_width=True)

                info_box(
                    f"📌 <strong>Sharpe {sharpe:.2f}</strong>: {'strong risk-adjusted performance' if sharpe>1 else 'acceptable performance' if sharpe>0 else 'poor risk-adjusted performance'}. "
                    f"&nbsp;|&nbsp; <strong>Skewness {skew:.2f}</strong>: {'left-skewed — beware of large negative tails' if skew<0 else 'right-skewed — upside surprises more likely'}. "
                    f"&nbsp;|&nbsp; <strong>Kurtosis {kurt:.2f}</strong>: {'fat tails (higher black-swan risk)' if kurt>3 else 'thin tails (lower extreme-event risk)'}.",
                    color=D["gold"]
                )

        except Exception as e:
            st.error(f"Risk calculation error: {e}")

    # ── T4: Recommendations ───────────────────────────────────────────────────
    with t4:
        section_title("Investment Recommendations",
                      sub=f"Data-driven, risk-aware signals for {risk_profile.lower()} investors")

        try:
            pc   = get_preds(asset_key, forecast_days, use_lstm)
            ens  = pc.get("preds", {}).get("ensemble", np.array([]))
            rm   = get_risk(asset_key, asset_name)

            if len(ens) == 0 or not rm:
                st.info("Visit the **Forecast** tab first to fit the models, then return here.")
            else:
                trend = "bullish" if float(ens[-1]) > cur else "bearish"
                sug = SuggestionsEngine.generate_suggestion(
                    asset_name=asset_name, current_price=cur,
                    predictions={"trend": trend, "confidence": 0.65, "price_target": float(ens[-1]),
                                 "volatility": rm.get("volatility_pct", 20),
                                 "sharpe_ratio": rm.get("sharpe_ratio", 0)},
                    risk_metrics=rm, timeframe="mid-term",
                )
                s = sug.to_dict()

                st.markdown(action_card(sug.action, sug.confidence, sug.risk_level, sug.holding_period),
                            unsafe_allow_html=True)
                st.markdown(price_target_row(sug.entry_price, sug.target_price, sug.stop_loss,
                                             s["upside_pct"], s["downside_pct"]),
                            unsafe_allow_html=True)

                info_box(f"<strong>Rationale:</strong> {sug.rationale}", color=asset_color)
                disclaimer_bar()

        except Exception as e:
            st.error(f"Recommendation error: {e}")

    # ── T5: AI Report ─────────────────────────────────────────────────────────
    with t5:
        section_title("AI-Generated Market Report",
                      badge="Claude AI", sub="Natural-language analysis powered by Anthropic")

        has_key = bool(os.getenv("OPENAI_API_KEY"))
        if not has_key:
            st.markdown(f"""
            <div style="background:{D['card']};border:1px solid {D['gold']}33;border-radius:14px;
                        padding:32px;text-align:center;margin:16px 0;">
                <div style="font-size:2.5rem;margin-bottom:12px;">🤖</div>
                <div style="color:{D['text1']};font-size:1.1rem;font-weight:700;margin-bottom:8px;">
                    Enter your Anthropic API key to unlock AI reports
                </div>
                <div style="color:{D['text2']};font-size:0.85rem;max-width:400px;margin:0 auto;">
                    Paste your <code style="background:{D['bg0']};padding:2px 6px;border-radius:4px;
                    color:{D['gold']};">sk-proj-...</code> OpenAI key in the sidebar.
                    Without a key, template-based reports are generated.
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("✨  Generate Report", type="primary"):
            with st.spinner("Generating AI-powered analysis with Claude…"):
                try:
                    pc   = get_preds(asset_key, forecast_days, use_lstm)
                    ens  = pc.get("preds", {}).get("ensemble", np.array([]))
                    rm   = get_risk(asset_key, asset_name)

                    if len(ens) == 0:
                        st.warning("Run the Forecast tab first.")
                    else:
                        rg = AIReportGenerator()
                        trend_st = "bullish" if float(ens[min(2, len(ens)-1)]) > cur else "bearish"
                        rpt = rg.generate_trend_analysis(
                            asset_name=asset_name,
                            predictions={"short_term": trend_st, "confidence": 0.65,
                                         "volatility": f"{rm.get('volatility_pct',0):.1f}%",
                                         "volatility_classification": rm.get("volatility_classification"),
                                         "sharpe_ratio": f"{rm.get('sharpe_ratio',0):.2f}",
                                         "max_drawdown": f"{rm.get('max_drawdown_pct',0):.1f}%"},
                            current_price=cur,
                            historical_context=f"{len(prices)}-day analysis. Ann. return {rm.get('annual_return',0):.1f}%.",
                        )
                        rec = rg.generate_recommendation(
                            asset_name=asset_name, risk_profile=risk_profile,
                            predictions={"trend": trend_st,
                                         "price_range": f"${float(ens.min()):,.2f} – ${float(ens.max()):,.2f}",
                                         "upside": (float(ens[-1])-cur)/cur*100,
                                         "downside": (float(ens.min())-cur)/cur*100},
                            risk_metrics={"volatility_class": rm.get("volatility_classification"),
                                          "sharpe_ratio": rm.get("sharpe_ratio", 0),
                                          "max_drawdown": rm.get("max_drawdown_pct", 0),
                                          "var_95": rm.get("var_95_pct", 0)},
                        )
                        st.session_state[f"rpt_{asset_key}"] = (rpt, rec, risk_profile)
                except Exception as e:
                    st.error(f"Report error: {e}")

        if f"rpt_{asset_key}" in st.session_state:
            rpt, rec, rp = st.session_state[f"rpt_{asset_key}"]
            divider()
            section_title("Market Analysis", badge="Claude AI")
            st.markdown(f"""
            <div style="background:{D['card']};border:1px solid {D['border']};border-radius:14px;
                        padding:28px 32px;line-height:1.75;color:{D['text1']};font-size:0.9rem;">
            """, unsafe_allow_html=True)
            st.markdown(rpt)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section_title(f"Personalised Recommendation", badge=rp)
            st.markdown(f"""
            <div style="background:{D['card']};border:1px solid {D['border']};border-left:3px solid {D['gold']};
                        border-radius:14px;padding:28px 32px;line-height:1.75;color:{D['text1']};font-size:0.9rem;">
            """, unsafe_allow_html=True)
            st.markdown(rec)
            st.markdown("</div>", unsafe_allow_html=True)
            disclaimer_bar()

    # ── T6: Compare ───────────────────────────────────────────────────────────
    with t6:
        section_title("Multi-Asset Comparison",
                      sub="Gold · S&P 500 · Bitcoin — performance, risk and correlation")

        try:
            st.plotly_chart(ch_compare(all_data), use_container_width=True)

            divider()
            section_title("Risk Metrics Side-by-Side")
            KEY_CFG = {"gold": "Gold", "sp500": "S&P 500", "bitcoin": "Bitcoin"}
            rows = []
            for key, lbl in KEY_CFG.items():
                df = all_data.get(key, pd.DataFrame())
                if df.empty: continue
                m = RiskMetrics().get_risk_summary(_close(df), lbl)
                if not m: continue
                rows.append({
                    "Asset":         lbl,
                    "Ann. Return":   f"{m['annual_return']:+.1f}%",
                    "Volatility":    f"{m['volatility_pct']:.1f}%",
                    "Sharpe":        f"{m['sharpe_ratio']:.2f}",
                    "Max Drawdown":  f"{m['max_drawdown_pct']:.1f}%",
                    "VaR 95%":       f"{m['var_95_pct']:.2f}%",
                    "Risk Level":    m["volatility_classification"],
                })
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Asset"), use_container_width=True)

            divider()
            c1, c2 = st.columns([3, 2])
            with c1:
                fig_corr = ch_correlation(all_data)
                if fig_corr: st.plotly_chart(fig_corr, use_container_width=True)
            with c2:
                section_title("Diversification Insight")
                st.markdown(f"""
                <div style="background:{D['card']};border:1px solid {D['border']};border-radius:12px;padding:20px;
                            display:flex;flex-direction:column;gap:12px;font-size:0.82rem;">
                    <div style="color:{D['text2']};line-height:1.7;">
                        A <strong style="color:{D['text1']};">correlation of +1.0</strong> means assets
                        move in lockstep. <strong style="color:{D['text1']};">0.0</strong> means independent.
                        <strong style="color:{D['text1']};">-1.0</strong> means perfect hedge.
                    </div>
                    <div style="height:1px;background:{D['border']};"></div>
                    <div style="color:{D['gold']};font-size:0.78rem;line-height:1.65;">
                        ✦ Lower correlation between holdings reduces portfolio volatility
                        through diversification — a core principle of Modern Portfolio Theory (MPT).
                    </div>
                    <div style="color:{D['text2']};font-size:0.78rem;line-height:1.65;">
                        Gold is traditionally a safe-haven with low correlation to equities,
                        making it a natural hedge in volatile markets.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Comparison error: {e}")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:28px 0 6px;margin-top:40px;
                border-top:1px solid {D['border']};font-size:0.75rem;color:{D['text3']};">
        <span>AI Trend Predictor v2.0</span>
        &nbsp;·&nbsp;
        <span>Data: Yahoo Finance</span>
        &nbsp;·&nbsp;
        <span>Models: ARIMA · Prophet · LSTM</span>
        &nbsp;·&nbsp;
        <span>AI: OpenAI GPT-4o</span>
        &nbsp;·&nbsp;
        <span style="color:{D['red']};">⚠️ Educational only — not financial advice</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
