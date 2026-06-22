import type { OrderBook } from "../types";

/** Thin order-book buy/sell pressure strip (bid vs ask volume) — one slim row
 *  above the indicator strip. */
export default function PressureBar({ book }: { book: OrderBook }) {
  const buy = book.bid_volume || 0;
  const sell = book.ask_volume || 0;
  const total = buy + sell;
  if (total <= 0) return null;
  const buyPct = (buy / total) * 100;

  return (
    <div className="pressure" title="Order-book buy vs sell volume">
      <span className="pr-label">Pressure</span>
      <div className="pr-track">
        <span className="pr-buy" style={{ width: `${buyPct}%` }} />
        <span className="pr-sell" style={{ width: `${100 - buyPct}%` }} />
      </div>
      <span className="pr-nums">
        <span className="pr-b">{Math.round(buyPct)}% buy</span>
        <span className="pr-s">{Math.round(100 - buyPct)}% sell</span>
      </span>
    </div>
  );
}
