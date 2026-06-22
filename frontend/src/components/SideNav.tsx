import type { ReactNode } from "react";

export type View = "chart" | "signal" | "report" | "trades" | "alerts" | "settings";

const I = (paths: ReactNode) => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {paths}
  </svg>
);

const ICONS: Record<View, ReactNode> = {
  chart: I(<><path d="M3 3v18h18" /><path d="M7 14l3-4 3 3 4-6" /></>),
  signal: I(<path d="M3 12h3l3 8 4-16 3 8h5" />),
  report: I(<><path d="M3 3v18h18" /><rect x="7" y="11" width="3" height="6" /><rect x="13" y="7" width="3" height="10" /></>),
  trades: I(<><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></>),
  alerts: I(<><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 0 1-3.4 0" /></>),
  settings: I(<><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 0 1-4 0v-.1A1.6 1.6 0 0 0 7 19.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 4.6 15H4a2 2 0 0 1 0-4h.1A1.6 1.6 0 0 0 5.6 8.3l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 11 4.6V4a2 2 0 0 1 4 0v.1A1.6 1.6 0 0 0 17 5.6l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V8.6A1.6 1.6 0 0 0 21 11h.1" /></>),
};

const ITEMS: { key: View; label: string }[] = [
  { key: "chart", label: "Chart" },
  { key: "signal", label: "Signal" },
  { key: "report", label: "Report" },
  { key: "trades", label: "Trades" },
  { key: "alerts", label: "Alerts" },
  { key: "settings", label: "Settings" },
];

export default function SideNav({ view, onChange }:
  { view: View; onChange: (v: View) => void }) {
  return (
    <nav className="sidenav" aria-label="Primary">
      <div className="sidenav-items">
        {ITEMS.map((it) => (
          <button
            key={it.key}
            className={view === it.key ? "sn-item active" : "sn-item"}
            onClick={() => onChange(it.key)}
            title={it.label}
            aria-label={it.label}
            aria-current={view === it.key ? "page" : undefined}
          >
            {ICONS[it.key]}
            <span className="sn-label">{it.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
