import type { TrendForecast as TF } from "../types";
import CollapsiblePanel from "./CollapsiblePanel";

const ARROW = { up: "▲", down: "▼", sideways: "→" } as const;

const fmt = (n: number) =>
  n >= 100 ? n.toLocaleString(undefined, { maximumFractionDigits: 2 }) : n.toFixed(5);

/**
 * Trend prediction: where price is likely to head over the next near / mid / far
 * windows. Each horizon shows a direction, the projected move and target, an
 * expected price band, and a confidence bar.
 */
export default function TrendForecast({ f }: { f: TF }) {
  return (
    <CollapsiblePanel title="Trend Prediction">
      <div className={`tf-headline tf-${f.bias}`}>{f.headline}</div>
      <div className="tf-rows">
        {f.horizons.map((h) => {
          const up = h.direction === "up";
          const down = h.direction === "down";
          const sign = h.move_pct > 0 ? "+" : "";
          return (
            <div key={h.bars} className={`tf-row tf-${h.direction}`}>
              <div className="tf-when">
                <span className="tf-when-label">next {h.label}</span>
                <span className={`tf-dir vote-${up ? "up" : down ? "down" : "neutral"}`}>
                  {ARROW[h.direction]} {h.direction.toUpperCase()}
                </span>
              </div>
              <div className="tf-proj">
                <span className={`tf-move ${up ? "up" : down ? "down" : "flat"}`}>
                  {sign}{h.move_pct}%
                </span>
                <span className="tf-target">→ {fmt(h.target)}</span>
                <span className="tf-band">({fmt(h.low)} – {fmt(h.high)})</span>
              </div>
              <div className="tf-conf">
                <span className="tf-conf-bar">
                  <span className="tf-conf-fill" style={{ width: `${h.confidence}%` }} />
                </span>
                <span className="tf-conf-num">{h.confidence}%</span>
              </div>
            </div>
          );
        })}
      </div>
      <div className="tf-foot">Statistical projection from recent drift &amp; volatility — not a promise.</div>
    </CollapsiblePanel>
  );
}
