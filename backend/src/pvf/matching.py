from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from pvf.config import Settings, get_settings
from pvf.models import CONDITION_RANK, Ask, Bid, EndType, GradeSubstitution, ListingStatus, SubstitutionType
from pvf.pricing import estimate_freight


@dataclass
class GradeMatch:
    substitution_type: SubstitutionType
    discount_pct: float
    note: str


def grade_match(db: Session, bid_grade: str, ask_grade: str) -> GradeMatch | None:
    if bid_grade == ask_grade:
        return GradeMatch(SubstitutionType.exact, 0.0, "")

    rows = db.execute(
        select(GradeSubstitution).where(
            GradeSubstitution.base_grade == bid_grade, GradeSubstitution.sub_grade == ask_grade
        )
    ).scalars().all()
    if not rows:
        rows = db.execute(
            select(GradeSubstitution).where(
                GradeSubstitution.base_grade == ask_grade,
                GradeSubstitution.sub_grade == bid_grade,
                GradeSubstitution.bidirectional.is_(True),
            )
        ).scalars().all()
    if not rows:
        return None
    row = rows[0]
    return GradeMatch(SubstitutionType.substitute, float(row.discount_pct), row.note)


@dataclass
class MatchCandidate:
    ask: Ask
    matched_quantity: float
    substitution_type: SubstitutionType
    discount_pct: float
    substitution_note: str
    distance_miles: float | None
    freight_per_unit: float
    price_per_unit_fob: float
    delivered_price_per_unit: float


def find_matches(db: Session, bid: Bid, settings: Settings | None = None) -> list[MatchCandidate]:
    settings = settings or get_settings()
    if bid.status not in (ListingStatus.open, ListingStatus.partially_filled) or bid.quantity_remaining <= 0:
        return []

    candidates = (
        db.execute(
            select(Ask).where(
                Ask.product_type == bid.product_type,
                Ask.nominal_size_in == bid.nominal_size_in,
                Ask.schedule_class == bid.schedule_class,
                Ask.status.in_([ListingStatus.open, ListingStatus.partially_filled]),
            )
        )
        .scalars()
        .all()
    )

    results: list[MatchCandidate] = []
    for ask in candidates:
        if ask.quantity_available <= 0:
            continue
        if bid.end_type != EndType.na and ask.end_type != bid.end_type:
            continue
        if CONDITION_RANK[ask.condition] > CONDITION_RANK[bid.min_condition]:
            continue
        if bid.require_mtr and not ask.has_mtr:
            continue

        gm = grade_match(db, bid.grade, ask.grade)
        if gm is None:
            continue

        fob = float(ask.price_per_unit) * (1 - gm.discount_pct)
        freight = estimate_freight(
            origin_lat=float(ask.location.lat),
            origin_lon=float(ask.location.lon),
            dest_lat=float(bid.destination.lat),
            dest_lon=float(bid.destination.lon),
            nominal_size_in=float(ask.nominal_size_in),
            schedule_class=ask.schedule_class,
            quantity_ft=min(ask.quantity_available, bid.quantity_remaining),
            settings=settings,
        )
        freight_per_unit = freight.freight_per_unit if freight else 0.0
        distance_miles = freight.distance_miles if freight else None
        delivered = fob + freight_per_unit

        if bid.max_delivered_price_per_unit is not None and delivered > float(bid.max_delivered_price_per_unit):
            continue

        results.append(
            MatchCandidate(
                ask=ask,
                matched_quantity=min(ask.quantity_available, bid.quantity_remaining),
                substitution_type=gm.substitution_type,
                discount_pct=gm.discount_pct,
                substitution_note=gm.note,
                distance_miles=distance_miles,
                freight_per_unit=freight_per_unit,
                price_per_unit_fob=fob,
                delivered_price_per_unit=delivered,
            )
        )

    results.sort(key=lambda c: c.delivered_price_per_unit)
    return results
