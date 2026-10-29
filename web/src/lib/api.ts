import "server-only";

export const API_URL = process.env.PVF_API_URL ?? "http://localhost:8000";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; message: string };

/** Server-side fetch against the PVF marketplace API. */
export async function api<T>(path: string, init: RequestInit = {}): Promise<ApiResult<T>> {
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");

  let response: Response;
  try {
    response = await fetch(`${API_URL}/v1${path}`, { ...init, headers, cache: "no-store" });
  } catch {
    return { ok: false, status: 503, message: "API unreachable" };
  }
  if (response.ok) {
    const text = await response.text();
    return { ok: true, data: (text ? JSON.parse(text) : null) as T };
  }
  const body = await response.json().catch(() => ({}));
  const detail = body?.detail;
  return { ok: false, status: response.status, message: typeof detail === "string" ? detail : response.statusText };
}
