import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from pvf.config import get_settings
from pvf.models import (
    Ask,
    Bid,
    Condition,
    EndType,
    GradeSubstitution,
    ListingStatus,
    Location,
    Manufacture,
    Trade,
)
from pvf.pricing import estimate_freight
from pvf.reference import GRADE_SUBSTITUTIONS

GULF_COAST_LOCATIONS = [
    ("Houston Ship Channel Yard", "Houston", "TX", 29.7604, -95.3698),
    ("Beaumont Surplus Yard", "Beaumont", "TX", 30.0802, -94.1266),
    ("Corpus Christi Terminal", "Corpus Christi", "TX", 27.8006, -97.3964),
    ("Baytown Storage Yard", "Baytown", "TX", 29.7355, -94.9774),
    ("Texas City Lay-Down Yard", "Texas City", "TX", 29.3838, -94.9027),
    ("Port Arthur Yard", "Port Arthur", "TX", 29.8850, -93.9400),
    ("Pasadena Pipe Yard", "Pasadena", "TX", 29.6911, -95.2091),
]


def seed_reference(db: Session) -> None:
    existing_names = {loc.name for loc in db.execute(select(Location)).scalars()}
    for name, city, state, lat, lon in GULF_COAST_LOCATIONS:
        if name not in existing_names:
            db.add(Location(name=name, city=city, state=state, lat=lat, lon=lon))

    existing_pairs = {
        (s.base_grade, s.sub_grade) for s in db.execute(select(GradeSubstitution)).scalars()
    }
    for base, sub, bidirectional, discount, note in GRADE_SUBSTITUTIONS:
        if (base, sub) not in existing_pairs:
            db.add(
                GradeSubstitution(
                    base_grade=base, sub_grade=sub, bidirectional=bidirectional, discount_pct=discount, note=note
                )
            )
    db.commit()


def _location(db: Session, name: str) -> Location:
    loc = db.execute(select(Location).where(Location.name == name)).scalar_one()
    return loc


def seed_demo(db: Session) -> None:
    if db.execute(select(Ask)).first() is not None:
        return  # already seeded

    houston = _location(db, "Houston Ship Channel Yard")
    beaumont = _location(db, "Beaumont Surplus Yard")
    corpus = _location(db, "Corpus Christi Terminal")
    baytown = _location(db, "Baytown Storage Yard")
    texas_city = _location(db, "Texas City Lay-Down Yard")
    port_arthur = _location(db, "Port Arthur Yard")
    pasadena = _location(db, "Pasadena Pipe Yard")

    asks = [
        Ask(
            seller_name="Gulf Coast Pipe & Supply",
            location_id=houston.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A106-B",
            manufacture=Manufacture.seamless,
            end_type=EndType.plain_end,
            quantity=2000,
            condition=Condition.new_surplus,
            has_mtr=True,
            price_per_unit=14.50,
        ),
        Ask(
            seller_name="Beaumont Surplus Yard Co",
            location_id=beaumont.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A53-B",
            manufacture=Manufacture.erw,
            end_type=EndType.plain_end,
            quantity=1500,
            condition=Condition.new_surplus,
            has_mtr=True,
            price_per_unit=13.80,
        ),
        Ask(
            seller_name="Baytown Pipe Traders",
            location_id=baytown.id,
            product_type="pipe",
            nominal_size_in=8.0,
            schedule_class="Sch 40",
            grade="API 5L X52",
            manufacture=Manufacture.welded,
            end_type=EndType.beveled,
            quantity=3000,
            condition=Condition.new_surplus,
            has_mtr=True,
            price_per_unit=21.00,
        ),
        Ask(
            seller_name="Texas City Idle Inventory",
            location_id=texas_city.id,
            product_type="pipe",
            nominal_size_in=8.0,
            schedule_class="Sch 40",
            grade="API 5L X42",
            manufacture=Manufacture.erw,
            end_type=EndType.beveled,
            quantity=1800,
            condition=Condition.used_good,
            has_mtr=False,
            price_per_unit=16.25,
        ),
        Ask(
            seller_name="Port Arthur Reclaimed Steel",
            location_id=port_arthur.id,
            product_type="pipe",
            nominal_size_in=10.0,
            schedule_class="Sch 40",
            grade="A106-B",
            manufacture=Manufacture.seamless,
            end_type=EndType.plain_end,
            quantity=1200,
            condition=Condition.new_surplus,
            has_mtr=True,
            price_per_unit=26.00,
        ),
        Ask(
            seller_name="Pasadena Pipe Exchange",
            location_id=pasadena.id,
            product_type="pipe",
            nominal_size_in=12.0,
            schedule_class="Sch 40",
            grade="A53-B",
            manufacture=Manufacture.erw,
            end_type=EndType.beveled,
            quantity=900,
            condition=Condition.used_as_is,
            has_mtr=False,
            price_per_unit=29.50,
        ),
    ]
    db.add_all(asks)

    bids = [
        Bid(
            buyer_name="Corpus Christi Fabrication Co",
            destination_location_id=corpus.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A106-B",
            end_type=EndType.na,
            quantity=1000,
            min_condition=Condition.new_surplus,
            require_mtr=True,
            max_delivered_price_per_unit=17.00,
        ),
        Bid(
            buyer_name="Houston Midstream Contractors",
            destination_location_id=houston.id,
            product_type="pipe",
            nominal_size_in=8.0,
            schedule_class="Sch 40",
            grade="API 5L X42",
            end_type=EndType.na,
            quantity=2500,
            min_condition=Condition.used_good,
            require_mtr=False,
            max_delivered_price_per_unit=19.50,
        ),
        Bid(
            buyer_name="Beaumont Terminal Builders",
            destination_location_id=beaumont.id,
            product_type="pipe",
            nominal_size_in=10.0,
            schedule_class="Sch 40",
            grade="A106-B",
            end_type=EndType.na,
            quantity=1200,
            min_condition=Condition.new_surplus,
            require_mtr=True,
            max_delivered_price_per_unit=None,
        ),
        Bid(
            buyer_name="Pasadena Fabrication Partners",
            destination_location_id=pasadena.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A53-B",
            end_type=EndType.na,
            quantity=500,
            min_condition=Condition.new_surplus,
            require_mtr=True,
            max_delivered_price_per_unit=None,
        ),
    ]
    db.add_all(bids)
    db.flush()

    _seed_price_history(db, houston, beaumont, corpus, baytown, texas_city)
    db.commit()


def _seed_price_history(db: Session, houston, beaumont, corpus, baytown, texas_city) -> None:
    """Backdated, fully-filled ask/bid/trade triples so the price chart has
    history on day one instead of starting empty."""
    settings = get_settings()
    rng = random.Random(42)
    origins = [houston, beaumont, texas_city]
    destinations = [corpus, baytown, houston]
    now = datetime.now(UTC)

    for i in range(24):
        days_ago = 180 - i * 7
        traded_at = now - timedelta(days=days_ago)
        origin = origins[i % len(origins)]
        dest = destinations[(i + 1) % len(destinations)]
        trend = 12.50 + (180 - days_ago) * 0.012  # slow upward drift over the window
        fob = round(trend + rng.uniform(-0.6, 0.6), 2)
        quantity = rng.choice([400, 500, 600, 800])

        freight = estimate_freight(
            origin_lat=float(origin.lat),
            origin_lon=float(origin.lon),
            dest_lat=float(dest.lat),
            dest_lon=float(dest.lon),
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            quantity_ft=quantity,
            settings=settings,
        )
        freight_per_unit = freight.freight_per_unit if freight else 0.0
        delivered = round(fob + freight_per_unit, 2)

        hist_ask = Ask(
            seller_name="Historical seed",
            location_id=origin.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A106-B",
            manufacture=Manufacture.seamless,
            end_type=EndType.plain_end,
            quantity=quantity,
            quantity_filled=quantity,
            condition=Condition.new_surplus,
            has_mtr=True,
            price_per_unit=fob,
            status=ListingStatus.filled,
        )
        hist_bid = Bid(
            buyer_name="Historical seed",
            destination_location_id=dest.id,
            product_type="pipe",
            nominal_size_in=6.0,
            schedule_class="Sch 40",
            grade="A106-B",
            end_type=EndType.na,
            quantity=quantity,
            quantity_filled=quantity,
            min_condition=Condition.new_surplus,
            require_mtr=True,
            status=ListingStatus.filled,
        )
        db.add(hist_ask)
        db.add(hist_bid)
        db.flush()

        db.add(
            Trade(
                ask_id=hist_ask.id,
                bid_id=hist_bid.id,
                product_type="pipe",
                nominal_size_in=6.0,
                schedule_class="Sch 40",
                grade="A106-B",
                substitution_type="exact",
                quantity=quantity,
                price_per_unit_fob=fob,
                freight_per_unit=round(freight_per_unit, 2),
                delivered_price_per_unit=delivered,
                origin_location_id=origin.id,
                destination_location_id=dest.id,
                traded_at=traded_at,
            )
        )
