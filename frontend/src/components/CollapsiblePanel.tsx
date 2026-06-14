import { type ReactNode, useState } from "react";

interface Props {
  title: string;
  right?: ReactNode;
  defaultOpen?: boolean;
  className?: string;
  id?: string;
  children: ReactNode;
}

/** A panel whose body collapses when you tap its header — handy on mobile. */
export default function CollapsiblePanel({ title, right, defaultOpen = true, className, id, children }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`panel${className ? ` ${className}` : ""}`} id={id}>
      <button className="panel-head" onClick={() => setOpen((o) => !o)}>
        <span className="panel-title-inline">{title}</span>
        <span className="panel-head-right">
          {right}
          <span className={open ? "chev up" : "chev"}>▾</span>
        </span>
      </button>
      {open && <div className="panel-body">{children}</div>}
    </div>
  );
}
