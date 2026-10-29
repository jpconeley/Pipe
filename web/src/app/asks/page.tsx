import { Suspense } from "react";
import type { Metadata } from "next";

import { ApiDown, Loading, Panel, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { createAsk } from "@/lib/actions";
import { date, label, usd } from "@/lib/format";
import type { Ask, Location, Reference } from "@/lib/types";

export const metadata: Metadata = { title: "Asks" };

async function AsksContent({ searchParams }: { searchParams: PageProps<"/asks">["searchParams"] }) {
  const params = await searchParams;
  const posted = params.posted === "1";
  const error = typeof params.error === "string" ? params.error : undefined;

  const [asksResult, refResult, locResult] = await Promise.all([
    api<Ask[]>("/asks"),
    api<Reference>("/specs/reference"),
    api<Location[]>("/locations"),
  ]);

  if (!asksResult.ok || !refResult.ok || !locResult.ok) return <ApiDown />;
  // Historical seed data (backing the price chart) is posted fully filled, so
  // excluding filled/cancelled keeps this table to live, actionable interest.
  const asks = asksResult.data.filter((a) => a.status === "open" || a.status === "partially_filled");
  const ref = refResult.data;
  const locations = locResult.data;

  return (
    <>
      <h1>Asks</h1>
      <p className="sub">Surplus material sellers are offering, priced FOB at their yard.</p>

      {posted && <div className="banner banner-success">Ask posted.</div>}
      {error && <div className="banner banner-error">{error}</div>}

      <Panel title="Post an ask">
        <form className="inline-form" action={createAsk}>
          <div className="field">
            <label htmlFor="seller_name">Seller</label>
            <input id="seller_name" name="seller_name" required />
          </div>
          <div className="field">
            <label htmlFor="location_id">Yard location</label>
            <select id="location_id" name="location_id" required>
              {locations.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="product_type">Product type</label>
            <select id="product_type" name="product_type" required defaultValue="pipe">
              {ref.product_types.map((p) => (
                <option key={p} value={p}>
                  {label(p)}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="nominal_size_in">Nominal size (in)</label>
            <select id="nominal_size_in" name="nominal_size_in" required defaultValue="6">
              {ref.nominal_sizes_in.map((s) => (
                <option key={s} value={s}>
                  {s}&quot;
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="schedule_class">Schedule / class</label>
            <select id="schedule_class" name="schedule_class" required>
              {ref.schedules.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="grade">Grade</label>
            <select id="grade" name="grade" required>
              {ref.grades.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="manufacture">Manufacture</label>
            <select id="manufacture" name="manufacture" defaultValue="seamless">
              {ref.manufactures.map((m) => (
                <option key={m} value={m}>
                  {label(m)}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="end_type">End type</label>
            <select id="end_type" name="end_type" defaultValue="plain_end">
              {ref.end_types.map((e) => (
                <option key={e} value={e}>
                  {label(e)}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="condition">Condition</label>
            <select id="condition" name="condition" defaultValue="new_surplus">
              {ref.conditions.map((c) => (
                <option key={c} value={c}>
                  {label(c)}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="quantity">Quantity (ft)</label>
            <input id="quantity" name="quantity" type="number" step="1" min="1" required />
          </div>
          <div className="field">
            <label htmlFor="price_per_unit">FOB price ($/ft)</label>
            <input id="price_per_unit" name="price_per_unit" type="number" step="0.01" min="0" required />
          </div>
          <div className="checkbox-field">
            <input id="has_mtr" name="has_mtr" type="checkbox" defaultChecked />
            <label htmlFor="has_mtr">Has mill test report (MTR)</label>
          </div>
          <div>
            <button type="submit">Post ask</button>
          </div>
        </form>
      </Panel>

      <Panel title="Open asks" right={<span className="muted">{asks.length}</span>}>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Seller</th>
                <th>Yard</th>
                <th>Spec</th>
                <th>Cond.</th>
                <th>MTR</th>
                <th className="num">Available</th>
                <th className="num">FOB $/ft</th>
                <th>Status</th>
                <th>Posted</th>
              </tr>
            </thead>
            <tbody>
              {asks.map((a) => (
                <tr key={a.id}>
                  <td>{a.seller_name}</td>
                  <td className="muted">{a.location.city}, {a.location.state}</td>
                  <td>{a.nominal_size_in}&quot; {a.schedule_class} {a.grade}</td>
                  <td className="muted">{label(a.condition)}</td>
                  <td>{a.has_mtr ? "Yes" : "No"}</td>
                  <td className="num">{a.quantity_available.toLocaleString()} {a.unit}</td>
                  <td className="num">{usd(a.price_per_unit)}</td>
                  <td><StatusBadge status={a.status} /></td>
                  <td className="muted">{date(a.created_at)}</td>
                </tr>
              ))}
              {asks.length === 0 && (
                <tr>
                  <td colSpan={9} className="muted">No asks posted yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

export default function AsksPage({ searchParams }: PageProps<"/asks">) {
  return (
    <Suspense fallback={<Loading />}>
      <AsksContent searchParams={searchParams} />
    </Suspense>
  );
}
