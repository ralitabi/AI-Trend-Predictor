import type { FearGreed } from "../types";

/** Vertical Fear & Greed gauge on the left of the chart: red (fear) at the
 *  bottom → green (greed) at the top, with a live pulsing marker at the value. */
export default function FearGreedBar({ fg }: { fg: FearGreed }) {
  const v = Math.max(0, Math.min(100, fg.value));
  const tone = v < 25 ? "ef" : v < 45 ? "f" : v < 55 ? "n" : v < 75 ? "g" : "eg";

  return (
    <div className="fgbar" title={`Fear & Greed: ${fg.value} · ${fg.classification}`}>
      <div className="fg-cap fg-top">Greed</div>
      <div className="fg-track">
        <span className="fg-dot" style={{ bottom: `${v}%` }} />
      </div>
      <div className="fg-cap fg-bot">Fear</div>
      <div className={`fg-val fg-${tone}`}>{fg.value}</div>
    </div>
  );
}
