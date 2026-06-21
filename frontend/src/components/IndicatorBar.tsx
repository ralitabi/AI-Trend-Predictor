import { useMemo } from "react";
import type { IndicatorDetail } from "../types";

/** Thin indicator-sentiment strip below the chart: counts + a slim
 *  bullish/neutral/bearish bar + the overall lean. Compact, one row. */
export default function IndicatorBar({ indicators }: { indicators: IndicatorDetail[] }) {
  const { up, neu, down, total, lean, cls } = useMemo(() => {
    const avail = indicators.filter((i) => i.available !== false);
    const up = avail.filter((i) => i.vote === "up").length;
    const down = avail.filter((i) => i.vote === "down").length;
    const neu = avail.filter((i) => i.vote === "neutral").length;
    const diff = up - down;
    const lean =
      diff >= 3 ? "Bullish" : diff <= -3 ? "Bearish"
        : diff > 0 ? "Slightly bullish" : diff < 0 ? "Slightly bearish" : "Mixed";
    const cls = diff > 0 ? "up" : diff < 0 ? "down" : "neu";
    return { up, neu, down, total: avail.length || 1, lean, cls };
  }, [indicators]);

  if (!indicators.length) return null;
  const pct = (n: number) => `${(n / total) * 100}%`;

  return (
    <div className="indbar" title={`${up} bullish · ${neu} neutral · ${down} bearish`}>
      <span className="indbar-label">Indicators</span>
      <span className="indbar-counts">
        <span className="ic up">▲ {up}</span>
        <span className="ic neu">■ {neu}</span>
        <span className="ic down">▼ {down}</span>
      </span>
      <div className="indbar-track" role="img"
        aria-label={`${up} bullish, ${neu} neutral, ${down} bearish`}>
        <span className="indbar-seg up" style={{ width: pct(up) }} />
        <span className="indbar-seg neu" style={{ width: pct(neu) }} />
        <span className="indbar-seg down" style={{ width: pct(down) }} />
      </div>
      <span className={`indbar-lean ${cls}`}>{lean}</span>
    </div>
  );
}
