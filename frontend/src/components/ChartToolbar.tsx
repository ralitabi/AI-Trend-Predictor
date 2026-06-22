import type { SafetyInfo, MarketInfo } from "../types";

interface Props {
  bias?: "up" | "down" | "neutral";
  confidence?: number;
  safety?: SafetyInfo;
  market?: MarketInfo;
  drawMode: "trendline" | "fib" | null;
  setDrawMode: (m: "trendline" | "fib" | null) => void;
  onClear: () => void;
  showForecastHist: boolean;
  setShowForecastHist: (v: boolean) => void;
  showAvgLine: boolean;
  setShowAvgLine: (v: boolean) => void;
  showPatterns: boolean;
  setShowPatterns: (v: boolean) => void;
}

const BIAS = {
  up: { label: "BULLISH", arrow: "▲", cls: "up" },
  down: { label: "BEARISH", arrow: "▼", cls: "down" },
  neutral: { label: "NO EDGE", arrow: "■", cls: "neutral" },
} as const;

const SAFETY_TONE = { safe: "good", caution: "mixed", risky: "bad" } as const;
const MARKET_TONE = { good: "good", mixed: "mixed", poor: "bad" } as const;

/** Compact readable meter: a label, a green→red gradient bar with a marker at
 *  the score, and the state word — much clearer than a tiny dial in a toolbar. */
function MiniMeter({ name, score, tone, state }:
  { name: string; score: number; tone: "good" | "mixed" | "bad"; state: string }) {
  const pos = Math.max(0, Math.min(100, score));
  return (
    <span className={`tbm tbm-${tone}`} title={`${name}: ${state} (${score}/100)`}>
      <span className="tbm-name">{name}</span>
      <span className="tbm-bar"><span className="tbm-dot" style={{ left: `${pos}%` }} /></span>
      <span className="tbm-state">{state}</span>
    </span>
  );
}

/** Toolbar above the chart: bias chip + the two risk meters + overlay toggles +
 *  drawing tools. */
export default function ChartToolbar({
  bias, confidence, safety, market, drawMode, setDrawMode, onClear,
  showForecastHist, setShowForecastHist, showAvgLine, setShowAvgLine,
  showPatterns, setShowPatterns,
}: Props) {
  const b = bias ? BIAS[bias] : null;

  return (
    <div className="charttb">
      {b && (
        <span className={`charttb-bias ${b.cls}`}>
          <span className="charttb-bias-arrow">{b.arrow}</span>
          {b.label}
          {confidence !== undefined && <span className="charttb-bias-conf">{confidence}%</span>}
        </span>
      )}

      {safety && (
        <MiniMeter name="TRADE" score={safety.score}
          tone={SAFETY_TONE[safety.level]} state={safety.level.toUpperCase()} />
      )}
      {market && (
        <MiniMeter name="MARKET" score={market.score}
          tone={MARKET_TONE[market.level]} state={market.level.toUpperCase()} />
      )}

      <div className="charttb-spacer" />

      <div className="charttb-group" role="group" aria-label="Chart overlays">
        <button className={`tb-btn${showForecastHist ? " on" : ""}`}
          onClick={() => setShowForecastHist(!showForecastHist)}
          title="Predicted-candle history">Forecast</button>
        <button className={`tb-btn${showAvgLine ? " on" : ""}`}
          onClick={() => setShowAvgLine(!showAvgLine)}
          title="Average trend line + projection">Avg line</button>
        <button className={`tb-btn${showPatterns ? " on" : ""}`}
          onClick={() => setShowPatterns(!showPatterns)}
          title="Candlestick & chart patterns">Patterns</button>
      </div>

      <span className="charttb-div" />

      <div className="charttb-group" role="group" aria-label="Drawing tools">
        <button className={`tb-btn${drawMode === "trendline" ? " on" : ""}`}
          onClick={() => setDrawMode(drawMode === "trendline" ? null : "trendline")}
          title="Trendline">╱ Trend</button>
        <button className={`tb-btn${drawMode === "fib" ? " on" : ""}`}
          onClick={() => setDrawMode(drawMode === "fib" ? null : "fib")}
          title="Fibonacci retracement">𝑭 Fib</button>
        <button className="tb-btn" onClick={onClear} title="Clear drawings">Clear</button>
      </div>
    </div>
  );
}
