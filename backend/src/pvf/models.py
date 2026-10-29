import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pvf.db import Base


class ProductType(enum.StrEnum):
    pipe = "pipe"
    valve = "valve"
    fitting = "fitting"
    flange = "flange"


class Manufacture(enum.StrEnum):
    seamless = "seamless"
    welded = "welded"
    erw = "erw"
    na = "na"


class EndType(enum.StrEnum):
    plain_end = "plain_end"
    beveled = "beveled"
    threaded = "threaded"
    flanged = "flanged"
    socket_weld = "socket_weld"
    na = "na"


class Condition(enum.StrEnum):
    """Ordered worst-to-best is NOT the order here; `rank` below defines quality order."""

    new_surplus = "new_surplus"
    used_good = "used_good"
    used_as_is = "used_as_is"


CONDITION_RANK = {Condition.new_surplus: 0, Condition.used_good: 1, Condition.used_as_is: 2}


class ListingStatus(enum.StrEnum):
    open = "open"
    partially_filled = "partially_filled"
    filled = "filled"
    cancelled = "cancelled"


class SubstitutionType(enum.StrEnum):
    exact = "exact"
    substitute = "substitute"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(2))
    lat: Mapped[float] = mapped_column(Numeric(9, 6))
    lon: Mapped[float] = mapped_column(Numeric(9, 6))


class GradeSubstitution(Base):
    __tablename__ = "grade_substitutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_grade: Mapped[str] = mapped_column(String(40))
    sub_grade: Mapped[str] = mapped_column(String(40))
    bidirectional: Mapped[bool] = mapped_column(default=False)
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    note: Mapped[str] = mapped_column(String(255), default="")


class SpecMixin:
    """Columns shared by asks and bids: the standard spec format for a listing."""

    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType, name="product_type"))
    nominal_size_in: Mapped[float] = mapped_column(Numeric(5, 2))
    schedule_class: Mapped[str] = mapped_column(String(20))
    grade: Mapped[str] = mapped_column(String(40))
    manufacture: Mapped[Manufacture] = mapped_column(Enum(Manufacture, name="manufacture"), default=Manufacture.na)
    end_type: Mapped[EndType] = mapped_column(Enum(EndType, name="end_type"), default=EndType.na)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2))
    unit: Mapped[str] = mapped_column(String(10), default="ft")


class Ask(Base, SpecMixin):
    __tablename__ = "asks"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_name: Mapped[str] = mapped_column(String(120))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    location: Mapped[Location] = relationship()
    condition: Mapped[Condition] = mapped_column(Enum(Condition, name="condition"), default=Condition.new_surplus)
    has_mtr: Mapped[bool] = mapped_column(default=False)
    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2))
    quantity_filled: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status"), default=ListingStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def quantity_available(self) -> float:
        return float(self.quantity) - float(self.quantity_filled)


class Bid(Base, SpecMixin):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_name: Mapped[str] = mapped_column(String(120))
    destination_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    destination: Mapped[Location] = relationship()
    min_condition: Mapped[Condition] = mapped_column(Enum(Condition, name="condition"), default=Condition.used_as_is)
    require_mtr: Mapped[bool] = mapped_column(default=False)
    max_delivered_price_per_unit: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    quantity_filled: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status"), default=ListingStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def quantity_remaining(self) -> float:
        return float(self.quantity) - float(self.quantity_filled)


class Trade(Base):
    """A completed deal. Spec fields are denormalized so the price index is
    stable even if the ask/bid rows it came from change later."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    ask_id: Mapped[int] = mapped_column(ForeignKey("asks.id"))
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"))
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType, name="product_type"))
    nominal_size_in: Mapped[float] = mapped_column(Numeric(5, 2))
    schedule_class: Mapped[str] = mapped_column(String(20))
    grade: Mapped[str] = mapped_column(String(40))
    substitution_type: Mapped[SubstitutionType] = mapped_column(Enum(SubstitutionType, name="substitution_type"))
    quantity: Mapped[float] = mapped_column(Numeric(10, 2))
    unit: Mapped[str] = mapped_column(String(10), default="ft")
    price_per_unit_fob: Mapped[float] = mapped_column(Numeric(10, 2))
    freight_per_unit: Mapped[float] = mapped_column(Numeric(10, 2))
    delivered_price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2))
    origin_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    destination_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    traded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
