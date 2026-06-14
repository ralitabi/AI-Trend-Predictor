import type { SafetyInfo } from "../types";

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

// score (0 = safe … 100 = risky) → angle on the 180°(left)→0°(right) arc
const angleFor = (score: number) => 180 - (Math.max(0, Math.min(100, score)) / 100) * 180;

const LEVEL_COLOR: Record<SafetyInfo["level"], string> = {
  safe: "#16c784",
  caution: "#f5a623",
  risky: "#ea3943",
};

/**
 * Risk-management gauge: a speedometer-style needle that swings from green
 * (safe to act) through amber to red (stay out), driven by the safety score.
 */
export default function RiskMeter({ safety }: { safety: SafetyInfo }) {
  const cx = 100;
  const cy = 96;
  const r = 78;
  const score = Math.max(0, Math.min(100, safety.score ?? 50));
  const needle = angleFor(score);
  const [nx, ny] = polar(cx, cy, r - 14, needle);
  const color = LEVEL_COLOR[safety.level];

  return (
    <div className="riskmeter">
      <svg viewBox="0 0 200 116" className="rm-svg" role="img"
           aria-label={`Risk level ${safety.level}, ${score} of 100`}>
        {/* zone arcs: green (safe) → amber (caution) → red (risky) */}
        <path d={arc(cx, cy, r, 180, angleFor(40))} className="rm-zone" stroke="#16c784" />
        <path d={arc(cx, cy, r, angleFor(40), angleFor(68))} className="rm-zone" stroke="#f5a623" />
        <path d={arc(cx, cy, r, angleFor(68), 0)} className="rm-zone" stroke="#ea3943" />
        {/* needle + hub */}
        <line x1={cx} y1={cy} x2={nx} y2={ny} className="rm-needle" stroke={color} />
        <circle cx={cx} cy={cy} r={6} className="rm-hub" fill={color} />
        {/* end labels */}
        <text x={20} y={112} className="rm-end">SAFE</text>
        <text x={180} y={112} className="rm-end rm-end-r">RISKY</text>
      </svg>
      <div className="rm-readout">
        <span className="rm-level" style={{ color }}>{safety.level.toUpperCase()}</span>
        <span className="rm-action">{safety.action}</span>
      </div>
      <div className="rm-headline">{safety.headline}</div>
      {safety.factors && safety.factors.length > 0 && (
        <div className="rm-factors">
          {safety.factors.map((f) => (
            <span key={f.label} className={`rm-factor rmf-${f.state}`} title={`${f.label}: ${f.detail}`}>
              <span className="rmf-dot" />
              <span className="rmf-label">{f.label}</span>
              <span className="rmf-detail">{f.detail}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
