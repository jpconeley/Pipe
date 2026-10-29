import { Suspense } from "react";
import type { Metadata } from "next";

import { PriceChart } from "@/components/PriceChart";
import { ApiDown, Loading, Panel, SubstitutionBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, usd } from "@/lib/format";
import type { Reference, Trade } from "@/lib/types";

export const metadata: Metadata = { title: "Price history" };

const DEFAULTS = { product_type: "pipe", nominal_size_in: "6", schedule_class: "Sch 40", grade: "A106-B" };

async function TradesContent({ searchParams }: { searchParams: PageProps<"/trades">["searchParams"] }) {
  const params = await searchParams;
  const spec = {
    product_type: DEFAULTS.product_type,
    nominal_size_in: typeof params.nominal_size_in === "string" ? params.nominal_size_in : DEFAULTS.nominal_size_in,
    schedule_class: typeof params.schedule_class === "string" ? params.schedule_class : DEFAULTS.schedule_class,
    grade: typeof params.grade === "string" ? params.grade : DEFAULTS.grade,
  };

  const [refResult, historyResult] = await Promise.all([
    api<Reference>("/specs/reference"),
    api<Trade[]>(
      `/trades/price-history?product_type=${spec.product_type}&nominal_size_in=${spec.nominal_size_in}&schedule_class=${encodeURIComponent(spec.schedule_class)}&grade=${encodeURIComponent(spec.grade)}&days=400`,
    ),
  ]);

  if (!refResult.ok) return <ApiDown />;
  const ref = refResult.data;
  const trades = historyResult.ok ? historyResult.data : [];
  const points = trades.map((t) => ({ date: t.traded_at, delivered: t.delivered_price_per_unit, fob: t.price_per_unit_fob }));

  return (
    <>
      <h1>Price history</h1>
      <p className="sub">Every completed deal, by spec. This is the index — nothing like it exists for surplus PVF today.</p>

      <Panel title="Spec">
        <form className="inline-form" method="get">
          <div className="field">
            <label htmlFor="nominal_size_in">Nominal size (in)</label>
            <select id="nominal_size_in" name="nominal_size_in" defaultValue={spec.nominal_size_in}>
              {ref.nominal_sizes_in.map((s) => (
                <option key={s} value={s}>
                  {s}&quot;
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="schedule_class">Schedule / class</label>
            <select id="schedule_class" name="schedule_class" defaultValue={spec.schedule_class}>
              {ref.schedules.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="grade">Grade</label>
            <select id="grade" name="grade" defaultValue={spec.grade}>
              {ref.grades.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div>
            <button type="submit">Update chart</button>
          </div>
        </form>
      </Panel>

      <Panel title="">
        <PriceChart points={points} title={`${spec.nominal_size_in}" ${spec.schedule_class} ${spec.grade}`} />
      </Panel>

      <Panel title="Trades" right={<span className="muted">{trades.length}</span>}>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Match</th>
                <th className="num">Qty</th>
                <th className="num">FOB $/ft</th>
                <th className="num">Freight $/ft</th>
                <th className="num">Delivered $/ft</th>
              </tr>
            </thead>
            <tbody>
              {[...trades].reverse().map((t) => (
                <tr key={t.id}>
                  <td className="muted">{date(t.traded_at)}</td>
                  <td><SubstitutionBadge type={t.substitution_type} /></td>
                  <td className="num">{t.quantity.toLocaleString()} {t.unit}</td>
                  <td className="num">{usd(t.price_per_unit_fob)}</td>
                  <td className="num">{usd(t.freight_per_unit)}</td>
                  <td className="num">{usd(t.delivered_price_per_unit)}</td>
                </tr>
              ))}
              {trades.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted">No trades for this spec yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

export default function TradesPage({ searchParams }: PageProps<"/trades">) {
  return (
    <Suspense fallback={<Loading />}>
      <TradesContent searchParams={searchParams} />
    </Suspense>
  );
}
