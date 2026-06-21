import type { OrderBook } from "../types";

/** Order-book buy/sell pressure: live bid vs ask volume, shown as a split bar
 *  just above the indicator strip. */
export default function PressureBar({ book }: { book: OrderBook }) {
  const buy = book.bid_volume || 0;
  const sell = book.ask_volume || 0;
  const total = buy + sell;
  if (total <= 0) return null;
  const buyPct = (buy / total) * 100;
  const sellPct = 100 - buyPct;

  return (
    <div className="pressure" title="Order-book buy vs sell volume">
      <span className="pr-label">Pressure</span>
      <div className="pr-track">
        <span className="pr-buy" style={{ width: `${buyPct}%` }}>
          {buyPct >= 14 && `BUY ${Math.round(buyPct)}%`}
        </span>
        <span className="pr-sell" style={{ width: `${sellPct}%` }}>
          {sellPct >= 14 && `SELL ${Math.round(sellPct)}%`}
        </span>
      </div>
    </div>
  );
}
