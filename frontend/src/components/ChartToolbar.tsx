import type { SafetyInfo, MarketInfo } from "../types";
import RiskMeter from "./RiskMeter";

interface Props {
  bias?: "up" | "down" | "neutral";
  confidence?: number;
  safety?: SafetyInfo;
  market?: MarketInfo;
  tf?: string;
  drawMode: "trendline" | "fib" | null;
  setDrawMode: (m: "trendline" | "fib" | null) => void;
  onClear: () => void;
  showForecastHist: boolean;
  setShowForecastHist: (v: boolean) => void;
  showAvgLine: boolean;
  setShowAvgLine: (v: boolean) => void;
  showPatterns: boolean;
  setShowPatterns: (v: boolean) => void;
  rightOpen: boolean;
  onToggleRight: () => void;
}

const BIAS = {
  up: { label: "BULLISH", arrow: "▲", cls: "up" },
  down: { label: "BEARISH", arrow: "▼", cls: "down" },
  neutral: { label: "NO EDGE", arrow: "■", cls: "neutral" },
} as const;

const SAFETY_TONE = { safe: "good", caution: "mixed", risky: "bad" } as const;
const MARKET_TONE = { good: "good", mixed: "mixed", poor: "bad" } as const;

/** Toolbar above the chart: bias chip + the two risk gauges + overlay toggles +
 *  drawing tools + a button to collapse the right panel. */
export default function ChartToolbar({
  bias, confidence, safety, market, tf, drawMode, setDrawMode, onClear,
  showForecastHist, setShowForecastHist, showAvgLine, setShowAvgLine,
  showPatterns, setShowPatterns, rightOpen, onToggleRight,
}: Props) {
  const b = bias ? BIAS[bias] : null;
  const tfu = tf ? tf.toUpperCase() : "";

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
        <div className="charttb-meter">
          <RiskMeter compact title={`Trade · ${tfu}`} score={safety.score}
            tone={SAFETY_TONE[safety.level]} label={safety.level.toUpperCase()}
            leftCap="SAFE" rightCap="RISKY" />
        </div>
      )}
      {market && (
        <div className="charttb-meter">
          <RiskMeter compact title={`Market · ${tfu}`} score={market.score}
            tone={MARKET_TONE[market.level]} label={market.level.toUpperCase()}
            leftCap="GOOD" rightCap="CHOPPY" />
        </div>
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

      <button className="tb-collapse" onClick={onToggleRight}
        title={rightOpen ? "Hide side panel" : "Show side panel"} aria-label="Toggle side panel">
        {rightOpen ? "⟩" : "⟨"}
      </button>
    </div>
  );
}
