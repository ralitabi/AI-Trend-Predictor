import type { MarketContextResponse } from "../types";
import CollapsiblePanel from "./CollapsiblePanel";

function fgColor(v: number): string {
  if (v < 25) return "#ea3943";
  if (v < 45) return "#f5a623";
  if (v < 55) return "#f5c518";
  if (v < 75) return "#62d98a";
  return "#16c784";
}

function fundCountdown(ts: number): string {
  const s = Math.max(0, ts - Math.floor(Date.now() / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

/**
 * Market context for crypto: the market-wide Fear & Greed index and the
 * perpetual funding rate (who's paying whom — a crowd-positioning read).
 */
export default function MarketContext({ c }: { c: MarketContextResponse }) {
  const fg = c.fear_greed;
  const fn = c.funding;
  if (!fg && !fn) return null;

  return (
    <CollapsiblePanel title="Market Context">
      {fg && (
        <div className="ctx-fg">
          <div className="ctx-fg-top">
            <span className="ctx-label">Fear &amp; Greed</span>
            <span className="ctx-fg-val" style={{ color: fgColor(fg.value) }}>
              {fg.value} · {fg.classification}
            </span>
          </div>
          <div className="ctx-fg-bar">
            <div className="ctx-fg-marker" style={{ left: `${fg.value}%`, borderColor: fgColor(fg.value) }} />
          </div>
          <div className="ctx-fg-scale"><span>Extreme fear</span><span>Extreme greed</span></div>
        </div>
      )}

      {fn && (
        <div className="ctx-fund">
          <div className="ctx-fund-top">
            <span className="ctx-label">Funding rate</span>
            <span className={`ctx-fund-rate ${fn.rate_pct >= 0 ? "pos" : "neg"}`}>
              {fn.rate_pct >= 0 ? "+" : ""}{fn.rate_pct}% <span className="ctx-fund-ann">({fn.annualized_pct >= 0 ? "+" : ""}{fn.annualized_pct}%/yr)</span>
            </span>
          </div>
          <div className="ctx-fund-sentiment">{fn.sentiment}</div>
          <div className="ctx-fund-next">Next funding in <b>{fundCountdown(fn.next_funding_time)}</b></div>
        </div>
      )}
    </CollapsiblePanel>
  );
}
