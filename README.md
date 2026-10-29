# Pipe — surplus PVF marketplace (prototype)

A working prototype of a bid/ask marketplace for surplus pipe, valves, fittings and
flanges, scoped to carbon steel line pipe on the Texas/Gulf Coast. It covers:

- A standard spec format for listings (product type, size, schedule/class, grade,
  manufacture, end type, condition, MTR).
- Bid and ask entry.
- A matching engine that ranks asks against a bid by **delivered price**
  (FOB price + an estimated freight cost), including **close substitute grades**
  (e.g. A106-B/A53-B dual-cert, API 5L X52 satisfying an X42 request).
- Trade execution, which records a completed deal.
- A price history chart and table per spec — the beginning of a price index.

## Stack

Same shape as the LASO project: FastAPI + Postgres + SQLAlchemy/Alembic on the
backend, Next.js (App Router) on the frontend, both run with Docker Compose.

```
backend/   FastAPI API, matching engine, freight estimator, Alembic migrations
web/       Next.js app (dashboard, asks, bids, bid matches, price history)
docker-compose.yml
```

There's no login/auth in this prototype — it's meant to be clicked through and
shared internally, not deployed publicly as-is.

## Running it (Windows, Docker Desktop + PowerShell)

```powershell
docker compose up -d --build
```

Then open:
- **http://localhost:3000** — the web app
- **http://localhost:8000/docs** — the API's interactive docs (Swagger UI)

First boot runs database migrations and seeds reference data (Gulf Coast yards,
grade substitution rules) plus demo asks, bids, and ~6 months of synthetic trade
history for 6" Sch 40 A106-B, so the price chart isn't empty on day one.

To stop: `docker compose down` (add `-v` to also wipe the database volume).

## Running it without Docker (local dev)

Requires `uv` (Python), `pnpm`/Node, and a local Postgres.

```powershell
make setup     # install backend + web dependencies
make db        # start just Postgres via Docker
make migrate
make seed
make api       # :8000, separate terminal
make web       # :3000, separate terminal
```

Run `make test` to lint and test the backend, and lint/build the frontend.

## How the matching engine works

For a bid, the engine (`backend/src/pvf/matching.py`) looks for open asks with the
same product type, nominal size, and schedule/class, then:

1. **Grade**: exact match, or a substitute per `backend/src/pvf/reference.py`'s
   `GRADE_SUBSTITUTIONS` table (e.g. X52 satisfies an X42 bid one-way; A106-B and
   A53-B dual-cert pipe satisfy each other).
2. **Condition / MTR**: excludes asks below the bid's minimum acceptable condition,
   or without a mill test report if the bid requires one.
3. **Freight**: estimates truckload freight from the ask's yard to the bid's
   delivery location, using the standard pipe weight table (lb/ft) to convert the
   quantity to truckloads, then a flat $/mile lane-rate assumption
   (`backend/src/pvf/pricing.py`). These rate assumptions
   (`PVF_FREIGHT_RATE_PER_MILE`, `PVF_FREIGHT_MIN_PER_LOAD`,
   `PVF_TRUCK_CAPACITY_TONS`) are placeholders — swap them for real lane rates or
   a freight API once you're quoting live.
4. **Ranking**: all matches that clear the bid's max delivered price (if set) are
   ranked by delivered price, cheapest first — exact and substitute matches ranked
   together, since a cheaper substitute should outrank a pricier exact match.

Executing a match (`POST /v1/trades/execute`) records a `Trade` — the row that
feeds the price history chart and, eventually, a published price index.

## What's intentionally not built yet

This is a first prototype, not the full plan. Missing on purpose:
- **Auth / accounts** — no login; anyone who can reach the app can post and trade.
- **Real freight quoting/booking** — freight is an estimate for ranking, not a
  bookable quote from a carrier.
- **AI intake** (turning seller spreadsheets/emails/stencil photos/MTR PDFs into
  listings) — listings are entered by hand via the form.
- **Payments, escrow, inspection, fees/subscriptions** — no billing of any kind.
- **Valves, fittings, flanges** — the schema supports them (`product_type`), but
  there's no seed data, weight table, or substitution logic for them yet; only
  line pipe is wired up end to end.
- **Non-Gulf-Coast locations** — freight assumes flatbed truck lanes; it doesn't
  know about rail or anything outside Texas.

## Repo layout

```
backend/
  src/pvf/
    models.py       SQLAlchemy models (Ask, Bid, Trade, Location, GradeSubstitution)
    reference.py     Standard spec vocabulary, pipe weight table, grade substitutions
    pricing.py       Freight estimator
    matching.py      The matching engine
    api/routes/      asks, bids, trades, specs, locations, dashboard
    seed.py          Reference + demo data
  tests/             pytest (matching engine + freight calc)
web/
  src/app/           dashboard, /asks, /bids, /bids/[id], /trades
  src/components/     PriceChart (inline SVG), shared UI
  src/lib/           API client, server actions (createAsk/createBid/executeTrade)
```
