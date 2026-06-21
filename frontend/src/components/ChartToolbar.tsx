interface Props {
  bias?: "up" | "down" | "neutral";
  confidence?: number;
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

/** Toolbar attached above the chart: live bias chip + chart overlay toggles +
 *  drawing tools — keeps all chart controls on the chart (TradingView-style). */
export default function ChartToolbar({
  bias, confidence, drawMode, setDrawMode, onClear,
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

      <div className="charttb-spacer" />

      <div className="charttb-group" role="group" aria-label="Chart overlays">
        <button className={`tb-btn${showForecastHist ? " on" : ""}`}
          onClick={() => setShowForecastHist(!showForecastHist)}
          title="Predicted-candle history — faint ghost candles over the real ones">Forecast</button>
        <button className={`tb-btn${showAvgLine ? " on" : ""}`}
          onClick={() => setShowAvgLine(!showAvgLine)}
          title="Average trend line + forward projection">Avg line</button>
        <button className={`tb-btn${showPatterns ? " on" : ""}`}
          onClick={() => setShowPatterns(!showPatterns)}
          title="Candlestick & chart patterns + divergences">Patterns</button>
      </div>

      <span className="charttb-div" />

      <div className="charttb-group" role="group" aria-label="Drawing tools">
        <button className={`tb-btn${drawMode === "trendline" ? " on" : ""}`}
          onClick={() => setDrawMode(drawMode === "trendline" ? null : "trendline")}
          title="Trendline — click two points">╱ Trend</button>
        <button className={`tb-btn${drawMode === "fib" ? " on" : ""}`}
          onClick={() => setDrawMode(drawMode === "fib" ? null : "fib")}
          title="Fibonacci retracement — click two points">𝑭 Fib</button>
        <button className="tb-btn" onClick={onClear} title="Clear all drawings">Clear</button>
      </div>
    </div>
  );
}
