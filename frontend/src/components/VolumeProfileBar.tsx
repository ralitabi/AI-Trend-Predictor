import type { VolProfile } from "../types";

/** Vertical volume-by-price strip shown on the left edge of the chart: each row
 *  is a price level, bar length = volume traded there. POC highlighted; the
 *  value-area levels are brighter. */
export default function VolumeProfileBar({ p }: { p: VolProfile }) {
  if (!p?.bins?.length) return null;
  const max = p.max_volume || Math.max(...p.bins.map((b) => b.volume)) || 1;
  const bins = [...p.bins].sort((a, b) => b.price - a.price); // high price → top

  return (
    <div className="volprofile" title="Volume traded by price level">
      <div className="vp-title">VOL</div>
      <div className="vp-bins">
        {bins.map((b) => {
          const w = Math.max(2, (b.volume / max) * 100);
          const isPoc = b.volume === max;
          const inVA = b.price >= p.value_area_low && b.price <= p.value_area_high;
          return (
            <div key={b.price} className="vp-row" title={`${b.price}`}>
              <span className={`vp-bar${isPoc ? " poc" : inVA ? " va" : ""}`} style={{ width: `${w}%` }} />
            </div>
          );
        })}
      </div>
      <div className="vp-poc">POC {p.poc}</div>
    </div>
  );
}
