import { Suspense } from "react";
import Link from "next/link";
import type { Metadata } from "next";

import { PriceChart } from "@/components/PriceChart";
import { ApiDown, Loading, Panel, StatCard, SubstitutionBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, sizeLabel, usd } from "@/lib/format";
import type { Dashboard, Trade } from "@/lib/types";

export const metadata: Metadata = { title: "Dashboard" };

const FLAGSHIP = { product_type: "pipe", nominal_size_in: 6, schedule_class: "Sch 40", grade: "A106-B" };

async function DashboardContent() {
  const [dashResult, historyResult] = await Promise.all([
    api<Dashboard>("/dashboard"),
    api<Trade[]>(
      `/trades/price-history?product_type=${FLAGSHIP.product_type}&nominal_size_in=${FLAGSHIP.nominal_size_in}&schedule_class=${encodeURIComponent(FLAGSHIP.schedule_class)}&grade=${encodeURIComponent(FLAGSHIP.grade)}&days=400`,
    ),
  ]);

  if (!dashResult.ok) return <ApiDown />;
  const dash = dashResult.data;
  const points = historyResult.ok
    ? historyResult.data.map((t) => ({ date: t.traded_at, delivered: t.delivered_price_per_unit, fob: t.price_per_unit_fob }))
    : [];

  return (
    <>
      <h1>Gulf Coast surplus line pipe</h1>
      <p className="sub">Carbon steel line pipe bids and asks, matched on delivered price including freight.</p>

      <div className="stat-grid">
        <StatCard label="Open asks" value={dash.open_asks} />
        <StatCard label="Open bids" value={dash.open_bids} />
        <StatCard label="Trades, last 30 days" value={dash.trades_30d} />
        <StatCard label="Volume, last 30 days" value={`${dash.volume_30d_units.toLocaleString()} ft`} />
      </div>

      <Panel title="" right={<Link href="/trades">All price history →</Link>}>
        <PriceChart points={points} title={sizeLabel(FLAGSHIP.nominal_size_in, FLAGSHIP.schedule_class, FLAGSHIP.grade)} />
      </Panel>

      <Panel title="Recent trades">
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Spec</th>
                <th>Match</th>
                <th className="num">Qty</th>
                <th className="num">FOB</th>
                <th className="num">Freight</th>
                <th className="num">Delivered</th>
              </tr>
            </thead>
            <tbody>
              {dash.recent_trades.map((t) => (
                <tr key={t.id}>
                  <td className="muted">{date(t.traded_at)}</td>
                  <td>{sizeLabel(t.nominal_size_in, t.schedule_class, t.grade)}</td>
                  <td><SubstitutionBadge type={t.substitution_type} /></td>
                  <td className="num">{t.quantity.toLocaleString()} {t.unit}</td>
                  <td className="num">{usd(t.price_per_unit_fob)}</td>
                  <td className="num">{usd(t.freight_per_unit)}</td>
                  <td className="num">{usd(t.delivered_price_per_unit)}</td>
                </tr>
              ))}
              {dash.recent_trades.length === 0 && (
                <tr>
                  <td colSpan={7} className="muted">No trades yet. Post an ask and a bid, then execute a match.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<Loading />}>
      <DashboardContent />
    </Suspense>
  );
}
