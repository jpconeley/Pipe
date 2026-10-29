import type { ReactNode } from "react";

export function Panel({ title, right, children }: { title: string; right?: ReactNode; children: ReactNode }) {
  return (
    <section className="panel">
      <header className="panel-head">
        <h2>{title}</h2>
        {right}
      </header>
      {children}
    </section>
  );
}

export function Loading() {
  return <p className="muted">Loading…</p>;
}

export function ApiDown() {
  return (
    <div className="banner banner-error">
      Can&apos;t reach the API. Make sure the backend container is running (<code>docker compose up</code>).
    </div>
  );
}

export function StatCard({ label, value, sub }: { label: string; value: ReactNode; sub?: string }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

const STATUS_CLASS: Record<string, string> = {
  open: "badge-open",
  partially_filled: "badge-partial",
  filled: "badge-filled",
  cancelled: "badge-cancelled",
};

export function StatusBadge({ status }: { status: string }) {
  return <span className={`badge ${STATUS_CLASS[status] ?? ""}`}>{status.replaceAll("_", " ")}</span>;
}

export function SubstitutionBadge({ type }: { type: "exact" | "substitute" }) {
  return (
    <span className={`badge ${type === "exact" ? "badge-exact" : "badge-substitute"}`}>
      {type === "exact" ? "Exact" : "Substitute"}
    </span>
  );
}
