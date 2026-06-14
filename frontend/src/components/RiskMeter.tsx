import type { RiskFactor } from "../types";

/** Point on the gauge arc for a given angle (deg, measured CCW from +x axis). */
function polar(cx: number, cy: number, r: number, deg: number): [number, number] {
  const rad = (deg * Math.PI) / 180;
  return [cx + r * Math.cos(rad), cy - r * Math.sin(rad)];
}

/** SVG arc path between two angles on the top semicircle (sweeps clockwise). */
function arc(cx: number, cy: number, r: number, startDeg: number, endDeg: number): string {
  const [x1, y1] = polar(cx, cy, r, startDeg);
  const [x2, y2] = polar(cx, cy, r, endDeg);
  const large = Math.abs(endDeg - startDeg) > 180 ? 1 : 0;
  return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
}

// score (0 = good/left … 100 = bad/right) → angle on the 180°→0° arc
const angleFor = (score: number) => 180 - (Math.max(0, Math.min(100, score)) / 100) * 180;

const TONE_COLOR = { good: "#16c784", mixed: "#f5a623", bad: "#ea3943" } as const;

interface Props {
  /** small heading above the gauge, e.g. "Trade · 1H" or "Market" */
  title: string;
  /** 0 = green/left (good) … 100 = red/right (bad) */
  score: number;
  tone: "good" | "mixed" | "bad";
  /** big readout under the needle, e.g. "RISKY" / "POOR" */
  label: string;
  /** one-line subtitle (action or short condition) */
  sub?: string;
  factors?: RiskFactor[];
  /** smaller footprint for the two-up side-by-side layout */
  compact?: boolean;
  /** end-cap labels under the arc */
  leftCap?: string;
  rightCap?: string;
}

/**
 * A speedometer-style gauge: a needle that swings from green (left/good) through
 * amber to red (right/bad), driven by a 0–100 score. Used for both the
 * trade-entry risk meter and the overall market-condition meter.
 */
export default function RiskMeter({
  title, score, tone, label, sub, factors, compact, leftCap = "SAFE", rightCap = "RISKY",
}: Props) {
  const cx = 100;
  const cy = 96;
  const r = 78;
  const s = Math.max(0, Math.min(100, score ?? 50));
  const [nx, ny] = polar(cx, cy, r - 14, angleFor(s));
  const color = TONE_COLOR[tone];

  return (
    <div className={compact ? "riskmeter compact" : "riskmeter"}>
      <div className="rm-title">{title}</div>
      <svg viewBox="0 0 200 116" className="rm-svg" role="img"
           aria-label={`${title}: ${label}, ${s} of 100`}>
        <path d={arc(cx, cy, r, 180, angleFor(40))} className="rm-zone" stroke="#16c784" />
        <path d={arc(cx, cy, r, angleFor(40), angleFor(68))} className="rm-zone" stroke="#f5a623" />
        <path d={arc(cx, cy, r, angleFor(68), 0)} className="rm-zone" stroke="#ea3943" />
        <line x1={cx} y1={cy} x2={nx} y2={ny} className="rm-needle" stroke={color} />
        <circle cx={cx} cy={cy} r={6} className="rm-hub" fill={color} />
        <text x={18} y={112} className="rm-end">{leftCap}</text>
        <text x={182} y={112} className="rm-end rm-end-r">{rightCap}</text>
      </svg>
      <div className="rm-readout">
        <span className="rm-level" style={{ color }}>{label}</span>
      </div>
      {sub && <div className="rm-sub">{sub}</div>}
      {factors && factors.length > 0 && (
        <div className="rm-factors">
          {factors.map((f) => (
            <span key={f.label} className={`rm-factor rmf-${f.state}`} title={`${f.label}: ${f.detail}`}>
              <span className="rmf-dot" />
              {!compact && <span className="rmf-label">{f.label}</span>}
              <span className="rmf-detail">{f.detail}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
