"use server";

import { redirect } from "next/navigation";

import { api } from "@/lib/api";

function str(formData: FormData, key: string): string {
  return String(formData.get(key) ?? "").trim();
}

function num(formData: FormData, key: string): number {
  return Number(formData.get(key));
}

function optionalNum(formData: FormData, key: string): number | null {
  const raw = str(formData, key);
  return raw === "" ? null : Number(raw);
}

export async function createAsk(formData: FormData) {
  const payload = {
    seller_name: str(formData, "seller_name"),
    location_id: num(formData, "location_id"),
    product_type: str(formData, "product_type"),
    nominal_size_in: num(formData, "nominal_size_in"),
    schedule_class: str(formData, "schedule_class"),
    grade: str(formData, "grade"),
    manufacture: str(formData, "manufacture"),
    end_type: str(formData, "end_type"),
    quantity: num(formData, "quantity"),
    unit: "ft",
    condition: str(formData, "condition"),
    has_mtr: formData.get("has_mtr") === "on",
    price_per_unit: num(formData, "price_per_unit"),
  };
  const result = await api("/asks", { method: "POST", body: JSON.stringify(payload) });
  if (!result.ok) redirect(`/asks?error=${encodeURIComponent(result.message)}`);
  redirect("/asks?posted=1");
}

export async function createBid(formData: FormData) {
  const payload = {
    buyer_name: str(formData, "buyer_name"),
    destination_location_id: num(formData, "destination_location_id"),
    product_type: str(formData, "product_type"),
    nominal_size_in: num(formData, "nominal_size_in"),
    schedule_class: str(formData, "schedule_class"),
    grade: str(formData, "grade"),
    end_type: "na",
    quantity: num(formData, "quantity"),
    unit: "ft",
    min_condition: str(formData, "min_condition"),
    require_mtr: formData.get("require_mtr") === "on",
    max_delivered_price_per_unit: optionalNum(formData, "max_delivered_price_per_unit"),
  };
  const result = await api("/bids", { method: "POST", body: JSON.stringify(payload) });
  if (!result.ok) redirect(`/bids?error=${encodeURIComponent(result.message)}`);
  redirect("/bids?posted=1");
}

export async function executeTrade(formData: FormData) {
  const bidId = str(formData, "bid_id");
  const payload = {
    ask_id: num(formData, "ask_id"),
    bid_id: num(formData, "bid_id"),
    quantity: num(formData, "quantity"),
  };
  const result = await api("/trades/execute", { method: "POST", body: JSON.stringify(payload) });
  if (!result.ok) redirect(`/bids/${bidId}?error=${encodeURIComponent(result.message)}`);
  redirect(`/bids/${bidId}?traded=1`);
}
