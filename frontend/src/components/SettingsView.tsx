import type { IndicatorDetail } from "../types";
import type { useIndicators } from "../useIndicators";
import IndicatorPanel from "./IndicatorPanel";

interface Props {
  theme: string;
  setTheme: (t: string) => void;
  indicators: IndicatorDetail[];
  overlayable: string[];
  ctrl: ReturnType<typeof useIndicators>;
  dataSource: string;
  live: boolean;
  symbol: string;
  name: string;
  updated?: number;
}

const THEMES: { key: string; label: string; swatch: string }[] = [
  { key: "dark", label: "Dark", swatch: "#0b0e14" },
  { key: "light", label: "Light", swatch: "#f5f7fa" },
  { key: "pink", label: "Pink", swatch: "#d6336c" },
];

export default function SettingsView({
  theme, setTheme, indicators, overlayable, ctrl, dataSource, live, symbol, name, updated,
}: Props) {
  return (
    <div className="view-wrap settings">
      <h1 className="view-title">Settings</h1>

      <section className="set-card">
        <h2 className="set-h">Appearance</h2>
        <p className="set-sub">Choose a theme for the whole platform.</p>
        <div className="set-themes">
          {THEMES.map((t) => (
            <button key={t.key} className={`set-theme${theme === t.key ? " active" : ""}`}
              onClick={() => setTheme(t.key)} aria-pressed={theme === t.key}>
              <span className="set-theme-swatch" style={{ background: t.swatch }} />
              {t.label}
            </button>
          ))}
        </div>
      </section>

      <section className="set-card">
        <h2 className="set-h">Indicators</h2>
        <p className="set-sub">
          Turn any of the 17 indicators on/off, feed them to the AI, or draw them on the chart.
          Changes apply live and are saved on this device.
        </p>
        {indicators.length > 0 ? (
          <IndicatorPanel indicators={indicators} overlayable={overlayable} ctrl={ctrl} />
        ) : (
          <div className="set-empty">Loading indicators…</div>
        )}
      </section>

      <section className="set-card">
        <h2 className="set-h">Data &amp; connection</h2>
        <div className="set-rows">
          <div className="set-row"><span>Market</span><span>{name} · {symbol}</span></div>
          <div className="set-row"><span>Data source</span><span>{dataSource}</span></div>
          <div className="set-row">
            <span>Status</span>
            <span><span className={live ? "live-dot" : "delayed-dot"} /> {live ? "Live" : "Delayed (~15 min)"}</span>
          </div>
          <div className="set-row">
            <span>Last update</span>
            <span>{updated ? new Date(updated * 1000).toLocaleTimeString() : "—"}</span>
          </div>
        </div>
      </section>

      <section className="set-card">
        <h2 className="set-h">About</h2>
        <p className="set-sub">
          Trading AI — real-time market intelligence across crypto, forex, commodities, indices
          and stocks. 17-indicator engine, AI reasoning, next-candle forecasting, backtest and a
          self-scoring accuracy report.
        </p>
      </section>
    </div>
  );
}
