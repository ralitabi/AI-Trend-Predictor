import type { SignalData } from "../types";
import CollapsiblePanel from "./CollapsiblePanel";
import RiskMeter from "./RiskMeter";

const ARROWS = { up: "▲", down: "▼", neutral: "■" } as const;

const fmt = (n: number) =>
  n >= 100 ? n.toLocaleString(undefined, { maximumFractionDigits: 2 }) : n.toFixed(5);

/** UTC hour (0–23) → the viewer's local time, e.g. "5 PM". */
function utcHourLocal(h: number): string {
  const d = new Date();
  d.setUTCHours(h, 0, 0, 0);
  return d.toLocaleTimeString([], { hour: "numeric", hour12: true });
}

const SAFETY_TONE = { safe: "good", caution: "mixed", risky: "bad" } as const;
const MARKET_TONE = { good: "good", mixed: "mixed", poor: "bad" } as const;
const MARKET_SUB = {
  good: "Trending · clean",
  mixed: "Choppy in spots",
  poor: "Hard to trade",
} as const;

export default function TradeSetup({ s }: { s: SignalData }) {
  const pctFrom = (level: number) => (((level - s.price) / s.price) * 100).toFixed(2);
  const nc = s.next_candle;
  const safety = s.safety;
  const market = s.market;
  const bw = s.best_window;
  const tfu = s.tf.toUpperCase();

  return (
    <CollapsiblePanel title="Trade Setup">
      {(safety || market) && (
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
      )}

      {nc && (
        <div className={`forecast forecast-${nc.direction}`}>
          <div className="forecast-head">
            Next candle forecast
            <span className={`forecast-dir vote-${nc.direction}`}>
              {ARROWS[nc.direction]} {nc.direction.toUpperCase()}
            </span>
          </div>
          <div className="forecast-ohlc">
            <span>O <b>{fmt(nc.open)}</b></span>
            <span>H <b>{fmt(nc.high)}</b></span>
            <span>L <b>{fmt(nc.low)}</b></span>
            <span>C <b>{fmt(nc.close)}</b></span>
          </div>
          <div className="forecast-meta">
            body ~{nc.body_pct}% · range ~{nc.range_pct}% · statistical projection, not a promise
          </div>
        </div>
      )}

      {(s.levels.support || s.levels.resistance) && (
        <div className="levels">
          {s.levels.resistance && (
            <div className="level">
              <span className="level-tag res">R</span>
              <span className="level-price">{fmt(s.levels.resistance)}</span>
              <span className="level-dist">{pctFrom(s.levels.resistance)}%</span>
            </div>
          )}
          {s.levels.support && (
            <div className="level">
              <span className="level-tag sup">S</span>
              <span className="level-price">{fmt(s.levels.support)}</span>
              <span className="level-dist">{pctFrom(s.levels.support)}%</span>
            </div>
          )}
        </div>
      )}

      {s.plan && (
        <div className={`plan plan-${s.plan.direction}`}>
          <div className="plan-head">
            ATR trade plan · {s.plan.direction.toUpperCase()} · R:R 1:{s.plan.rr}
          </div>
          <div className="plan-row">
            <span>Entry <b>{fmt(s.plan.entry)}</b></span>
            <span className="plan-stop">Stop <b>{fmt(s.plan.stop)}</b> ({pctFrom(s.plan.stop)}%)</span>
            <span className="plan-target">Target <b>{fmt(s.plan.target)}</b> ({pctFrom(s.plan.target)}%)</span>
          </div>
        </div>
      )}

      <button
        className="full-analysis-btn"
        onClick={() =>
          document.getElementById("ai-analysis-card")?.scrollIntoView({ behavior: "smooth", block: "start" })
        }
      >
        View Full Analysis <span className="fa-arrow">↗</span>
      </button>
    </CollapsiblePanel>
  );
}
