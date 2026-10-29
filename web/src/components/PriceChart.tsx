export type PricePoint = { date: string; delivered: number; fob: number };

const WIDTH = 760;
const HEIGHT = 320;
const PAD = { top: 24, right: 16, bottom: 36, left: 56 };
const PLOT_W = WIDTH - PAD.left - PAD.right;
const PLOT_H = HEIGHT - PAD.top - PAD.bottom;

function niceTicks(min: number, max: number, count = 4): number[] {
  if (min === max) return [min];
  const step = (max - min) / count;
  const rounded = Math.max(0.5, Math.round(step * 2) / 2);
  const ticks: number[] = [];
  for (let v = Math.floor(min / rounded) * rounded; v <= max + rounded / 2; v += rounded) {
    ticks.push(Math.round(v * 100) / 100);
  }
  return ticks;
}

/** A small, static price-history line chart: delivered price vs. FOB price over time. */
export function PriceChart({ points, title }: { points: PricePoint[]; title: string }) {
  if (points.length === 0) {
    return <p className="muted">No completed trades yet for this spec.</p>;
  }

  const sorted = [...points].sort((a, b) => a.date.localeCompare(b.date));
  const dates = sorted.map((p) => new Date(p.date).getTime());
  const minDate = Math.min(...dates);
  const maxDate = Math.max(...dates);
  const allValues = sorted.flatMap((p) => [p.delivered, p.fob]);
  const rawMin = Math.min(...allValues);
  const rawMax = Math.max(...allValues);
  const span = rawMax - rawMin || 1;
  const yMin = rawMin - span * 0.1;
  const yMax = rawMax + span * 0.1;

  const x = (t: number) => (maxDate === minDate ? PLOT_W / 2 : ((t - minDate) / (maxDate - minDate)) * PLOT_W);
  const y = (v: number) => PLOT_H - ((v - yMin) / (yMax - yMin)) * PLOT_H;

  const deliveredPath = sorted.map((p, i) => `${i === 0 ? "M" : "L"}${x(new Date(p.date).getTime())},${y(p.delivered)}`).join(" ");
  const fobPath = sorted.map((p, i) => `${i === 0 ? "M" : "L"}${x(new Date(p.date).getTime())},${y(p.fob)}`).join(" ");

  const ticks = niceTicks(yMin, yMax);
  const last = sorted[sorted.length - 1];
  const first = sorted[0];
  const mid = sorted[Math.floor(sorted.length / 2)];
  const fmtDate = (iso: string) => new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const fmtMoney = (v: number) => `$${v.toFixed(2)}`;

  const deliveredLabelY = y(last.delivered);
  const fobLabelY = y(last.fob);
  const labelsConverge = Math.abs(deliveredLabelY - fobLabelY) < 14;

  return (
    <div className="chart">
      <style>{`
        .chart { --series-delivered: #2a78d6; --series-fob: #eb6834; --grid: #e1e0d9; --axis: #c3c2b7; --ink-2: #52514e; --ink-3: #898781; }
        @media (prefers-color-scheme: dark) {
          .chart { --series-delivered: #3987e5; --series-fob: #d95926; --grid: #2c2c2a; --axis: #383835; --ink-2: #c3c2b7; --ink-3: #898781; }
        }
      `}</style>
      <div className="chart-head">
        <h3>{title}</h3>
        <div className="legend">
          <span className="legend-item"><i style={{ background: "var(--series-delivered)" }} /> Delivered price</span>
          <span className="legend-item"><i style={{ background: "var(--series-fob)" }} /> FOB (yard) price</span>
        </div>
      </div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={`${title} price history chart`}>
        <g transform={`translate(${PAD.left},${PAD.top})`}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={0} x2={PLOT_W} y1={y(t)} y2={y(t)} stroke="var(--grid)" strokeWidth={1} />
              <text x={-8} y={y(t)} textAnchor="end" dominantBaseline="middle" fontSize={11} fill="var(--ink-3)">
                {fmtMoney(t)}
              </text>
            </g>
          ))}
          <line x1={0} x2={PLOT_W} y1={PLOT_H} y2={PLOT_H} stroke="var(--axis)" strokeWidth={1} />

          <path d={fobPath} fill="none" stroke="var(--series-fob)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
          <path d={deliveredPath} fill="none" stroke="var(--series-delivered)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />

          {sorted.map((p, i) => (
            <g key={i}>
              <circle cx={x(new Date(p.date).getTime())} cy={y(p.fob)} r={4} fill="var(--series-fob)" stroke="var(--grid)" strokeWidth={2}>
                <title>{`${fmtDate(p.date)} · FOB ${fmtMoney(p.fob)}`}</title>
              </circle>
              <circle
                cx={x(new Date(p.date).getTime())}
                cy={y(p.delivered)}
                r={4}
                fill="var(--series-delivered)"
                stroke="var(--grid)"
                strokeWidth={2}
              >
                <title>{`${fmtDate(p.date)} · Delivered ${fmtMoney(p.delivered)}`}</title>
              </circle>
            </g>
          ))}

          <text x={PLOT_W} y={labelsConverge ? deliveredLabelY - 6 : deliveredLabelY - 4} textAnchor="end" fontSize={11} fill="var(--ink-2)">
            {fmtMoney(last.delivered)}
          </text>
          <text x={PLOT_W} y={labelsConverge ? fobLabelY + 12 : fobLabelY - 4} textAnchor="end" fontSize={11} fill="var(--ink-2)">
            {fmtMoney(last.fob)}
          </text>

          <text x={0} y={PLOT_H + 20} fontSize={11} fill="var(--ink-3)">
            {fmtDate(first.date)}
          </text>
          <text x={x(new Date(mid.date).getTime())} y={PLOT_H + 20} textAnchor="middle" fontSize={11} fill="var(--ink-3)">
            {fmtDate(mid.date)}
          </text>
          <text x={PLOT_W} y={PLOT_H + 20} textAnchor="end" fontSize={11} fill="var(--ink-3)">
            {fmtDate(last.date)}
          </text>
        </g>
      </svg>
    </div>
  );
}
