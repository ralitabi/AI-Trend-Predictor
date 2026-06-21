import type { SignalData } from "../types";
import RiskMeter from "./RiskMeter";

const SAFETY_TONE = { safe: "good", caution: "mixed", risky: "bad" } as const;
const MARKET_TONE = { good: "good", mixed: "mixed", poor: "bad" } as const;
const MARKET_SUB = {
  good: "Trending · clean",
  mixed: "Choppy in spots",
  poor: "Hard to trade",
} as const;

/** UTC hour (0–23) → the viewer's local time, e.g. "5 PM". */
function utcHourLocal(h: number): string {
  const d = new Date();
  d.setUTCHours(h, 0, 0, 0);
  return d.toLocaleTimeString([], { hour: "numeric", hour12: true });
}

/** The two at-a-glance risk gauges (Trade safety + Market condition), shown at
 *  the top of the right panel. */
export default function MetersPanel({ s }: { s: SignalData }) {
  const { safety, market, best_window: bw } = s;
  const tfu = s.tf.toUpperCase();
  if (!safety && !market) return null;

  return (
    <div className={`safety safety-${safety?.level ?? "caution"}`}>
      <div className="meters-row">
        {safety && (
          <RiskMeter compact title={`Trade · ${tfu}`} score={safety.score}
            tone={SAFETY_TONE[safety.level]} label={safety.level.toUpperCase()}
            sub={safety.action} factors={safety.factors}
            leftCap="SAFE" rightCap="RISKY" />
        )}
        {market && (
          <RiskMeter compact title={`Market · ${tfu}`} score={market.score}
            tone={MARKET_TONE[market.level]} label={market.level.toUpperCase()}
            sub={MARKET_SUB[market.level]} factors={market.factors}
            leftCap="GOOD" rightCap="CHOPPY" />
        )}
      </div>
      {safety && <div className="meters-headline">{safety.headline}</div>}
      {bw && (
        <div className="safety-time">
          Best hours to trade: <b>{utcHourLocal(bw.start_utc)} – {utcHourLocal(bw.end_utc)}</b> (your time)
          {bw.intensity >= 1.15 && <span className="safety-time-note"> · {bw.intensity}× the usual movement</span>}
        </div>
      )}
    </div>
  );
}
