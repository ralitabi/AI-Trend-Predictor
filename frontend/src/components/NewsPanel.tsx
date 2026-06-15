import type { CalendarEvent, NewsResponse } from "../types";
import CollapsiblePanel from "./CollapsiblePanel";

const DOT = { bullish: "▲", bearish: "▼", neutral: "·" } as const;

function eventWhen(ts: number): string {
  const s = ts - Math.floor(Date.now() / 1000);
  if (s < 0) return "now";
  if (s < 3600) return `in ${Math.floor(s / 60)}m`;
  if (s < 86400) return `in ${Math.floor(s / 3600)}h`;
  return `in ${Math.floor(s / 86400)}d`;
}

/**
 * Headline sentiment (lexicon-based) for the asset's class, plus upcoming
 * high-impact economic events that can move markets.
 */
export default function NewsPanel({ news, events }: { news: NewsResponse | null; events: CalendarEvent[] }) {
  const s = news?.sentiment;
  if (!s && events.length === 0) return null;
  const toneClass = s ? (s.score >= 15 ? "bullish" : s.score <= -15 ? "bearish" : "neutral") : "neutral";

  return (
    <CollapsiblePanel title="News & Events"
      right={s ? <span className={`news-tag news-${toneClass}`}>{s.label}</span> : undefined}>
      {s && (
        <>
          <div className="news-meter">
            <div className="news-meter-bar">
              <div className="news-meter-fill" style={{
                width: `${Math.abs(s.score)}%`,
                marginLeft: s.score < 0 ? `${50 - Math.abs(s.score) / 2}%` : "50%",
                background: s.score >= 0 ? "var(--green)" : "var(--red)",
              }} />
              <div className="news-meter-mid" />
            </div>
            <div className="news-meter-counts">
              <span className="bull">{s.bullish}▲</span>
              <span className="bear">{s.bearish}▼</span>
            </div>
          </div>
          <ul className="news-list">
            {s.headlines.map((h, i) => (
              <li key={i} className={`news-row news-${h.sentiment}`}>
                <span className="news-dot">{DOT[h.sentiment]}</span>
                <span className="news-title">{h.title}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {events.length > 0 && (
        <div className="cal">
          <div className="cal-head">Upcoming economic events</div>
          {events.slice(0, 6).map((e, i) => (
            <div key={i} className="cal-row">
              <span className={`cal-impact ci-${e.impact.toLowerCase()}`} title={`${e.impact} impact`} />
              <span className="cal-ccy">{e.country}</span>
              <span className="cal-title">{e.title}</span>
              <span className="cal-when">{eventWhen(e.time)}</span>
            </div>
          ))}
        </div>
      )}
    </CollapsiblePanel>
  );
}
