import { Suspense } from "react";
import Link from "next/link";
import type { Metadata } from "next";

import { ApiDown, Loading, Panel, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { createBid } from "@/lib/actions";
import { date, label, usd } from "@/lib/format";
import type { Bid, Location, Reference } from "@/lib/types";

export const metadata: Metadata = { title: "Bids" };

async function BidsContent({ searchParams }: { searchParams: PageProps<"/bids">["searchParams"] }) {
  const params = await searchParams;
  const posted = params.posted === "1";
  const error = typeof params.error === "string" ? params.error : undefined;

  const [bidsResult, refResult, locResult] = await Promise.all([
    api<Bid[]>("/bids"),
    api<Reference>("/specs/reference"),
    api<Location[]>("/locations"),
  ]);

  if (!bidsResult.ok || !refResult.ok || !locResult.ok) return <ApiDown />;
  // Historical seed data (backing the price chart) is posted fully filled, so
  // excluding filled/cancelled keeps this table to live, actionable interest.
  const bids = bidsResult.data.filter((b) => b.status === "open" || b.status === "partially_filled");
  const ref = refResult.data;
  const locations = locResult.data;

  return (
    <>
      <h1>Bids</h1>
      <p className="sub">What buyers want, delivered to their site. The matching engine ranks asks for each bid by delivered price.</p>

      {posted && <div className="banner banner-success">Bid posted.</div>}
      {error && <div className="banner banner-error">{error}</div>}

      <Panel title="Post a bid">
        <form className="inline-form" action={createBid}>
          <div className="field">
            <label htmlFor="buyer_name">Buyer</label>
            <input id="buyer_name" name="buyer_name" required />
          </div>
          <div className="field">
            <label htmlFor="destination_location_id">Delivery destination</label>
            <select id="destination_location_id" name="destination_location_id" required>
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
            <label htmlFor="grade">Grade wanted</label>
            <select id="grade" name="grade" required>
              {ref.grades.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="min_condition">Min. acceptable condition</label>
            <select id="min_condition" name="min_condition" defaultValue="used_as_is">
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
            <label htmlFor="max_delivered_price_per_unit">Max delivered price ($/ft, optional)</label>
            <input id="max_delivered_price_per_unit" name="max_delivered_price_per_unit" type="number" step="0.01" min="0" />
          </div>
          <div className="checkbox-field">
            <input id="require_mtr" name="require_mtr" type="checkbox" />
            <label htmlFor="require_mtr">Require mill test report (MTR)</label>
          </div>
          <div>
            <button type="submit">Post bid</button>
          </div>
        </form>
      </Panel>

      <Panel title="Open bids" right={<span className="muted">{bids.length}</span>}>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Buyer</th>
                <th>Destination</th>
                <th>Spec</th>
                <th className="num">Remaining</th>
                <th className="num">Max delivered $/ft</th>
                <th>Status</th>
                <th>Posted</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {bids.map((b) => (
                <tr key={b.id}>
                  <td>{b.buyer_name}</td>
                  <td className="muted">{b.destination.city}, {b.destination.state}</td>
                  <td>{b.nominal_size_in}&quot; {b.schedule_class} {b.grade}</td>
                  <td className="num">{b.quantity_remaining.toLocaleString()} {b.unit}</td>
                  <td className="num">{b.max_delivered_price_per_unit != null ? usd(b.max_delivered_price_per_unit) : "—"}</td>
                  <td><StatusBadge status={b.status} /></td>
                  <td className="muted">{date(b.created_at)}</td>
                  <td><Link href={`/bids/${b.id}`}>View matches →</Link></td>
                </tr>
              ))}
              {bids.length === 0 && (
                <tr>
                  <td colSpan={8} className="muted">No bids posted yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

export default function BidsPage({ searchParams }: PageProps<"/bids">) {
  return (
    <Suspense fallback={<Loading />}>
      <BidsContent searchParams={searchParams} />
    </Suspense>
  );
}
