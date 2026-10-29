import { Suspense } from "react";
import type { Metadata } from "next";

import { ApiDown, Loading, Panel, StatusBadge, SubstitutionBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { executeTrade } from "@/lib/actions";
import { label, usd } from "@/lib/format";
import type { Bid, Match } from "@/lib/types";

export const metadata: Metadata = { title: "Bid matches" };

async function BidContent({
  params,
  searchParams,
}: {
  params: PageProps<"/bids/[id]">["params"];
  searchParams: PageProps<"/bids/[id]">["searchParams"];
}) {
  const { id } = await params;
  const search = await searchParams;
  const traded = search.traded === "1";
  const error = typeof search.error === "string" ? search.error : undefined;

  const [bidResult, matchesResult] = await Promise.all([api<Bid>(`/bids/${id}`), api<Match[]>(`/bids/${id}/matches`)]);

  if (!bidResult.ok) return <ApiDown />;
  const bid = bidResult.data;
  const matches = matchesResult.ok ? matchesResult.data : [];

  return (
    <>
      <h1>
        {bid.buyer_name} — {bid.nominal_size_in}&quot; {bid.schedule_class} {bid.grade}
      </h1>
      <p className="sub">
        Delivered to {bid.destination.name} · wants {bid.quantity_remaining.toLocaleString()} {bid.unit} ·{" "}
        min condition {label(bid.min_condition)} · {bid.require_mtr ? "requires MTR" : "MTR not required"} ·{" "}
        max delivered {bid.max_delivered_price_per_unit != null ? usd(bid.max_delivered_price_per_unit) : "no cap"} ·{" "}
        <StatusBadge status={bid.status} />
      </p>

      {traded && <div className="banner banner-success">Trade executed.</div>}
      {error && <div className="banner banner-error">{error}</div>}

      <Panel title="Ranked matches" right={<span className="muted">by delivered price, lowest first</span>}>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Seller</th>
                <th>Yard</th>
                <th>Grade</th>
                <th>Match</th>
                <th className="num">Distance</th>
                <th className="num">FOB $/ft</th>
                <th className="num">Freight $/ft</th>
                <th className="num">Delivered $/ft</th>
                <th className="num">Qty available</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {matches.map((m) => (
                <tr key={m.ask.id}>
                  <td>{m.ask.seller_name}</td>
                  <td className="muted">{m.ask.location.city}, {m.ask.location.state}</td>
                  <td>
                    {m.ask.grade}
                    {m.substitution_note && <div className="muted" style={{ fontSize: "0.75rem" }}>{m.substitution_note}</div>}
                  </td>
                  <td><SubstitutionBadge type={m.substitution_type} /></td>
                  <td className="num">{m.distance_miles != null ? `${Math.round(m.distance_miles)} mi` : "—"}</td>
                  <td className="num">{usd(m.price_per_unit_fob)}</td>
                  <td className="num">{usd(m.freight_per_unit)}</td>
                  <td className="num"><strong>{usd(m.delivered_price_per_unit)}</strong></td>
                  <td className="num">{m.matched_quantity.toLocaleString()} {m.ask.unit}</td>
                  <td>
                    <form action={executeTrade}>
                      <input type="hidden" name="ask_id" value={m.ask.id} />
                      <input type="hidden" name="bid_id" value={bid.id} />
                      <input type="hidden" name="quantity" value={m.matched_quantity} />
                      <button type="submit" disabled={bid.status === "filled"}>
                        Execute
                      </button>
                    </form>
                  </td>
                </tr>
              ))}
              {matches.length === 0 && (
                <tr>
                  <td colSpan={10} className="muted">No matching asks right now.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

export default function BidPage({ params, searchParams }: PageProps<"/bids/[id]">) {
  return (
    <Suspense fallback={<Loading />}>
      <BidContent params={params} searchParams={searchParams} />
    </Suspense>
  );
}
