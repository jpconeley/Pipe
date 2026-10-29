from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pvf.models import Condition, EndType, ListingStatus, Manufacture, ProductType, SubstitutionType


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str
    state: str
    lat: float
    lon: float


class SpecIn(BaseModel):
    product_type: ProductType
    nominal_size_in: float
    schedule_class: str
    grade: str
    manufacture: Manufacture = Manufacture.na
    end_type: EndType = EndType.na
    quantity: float
    unit: str = "ft"


class AskCreate(SpecIn):
    seller_name: str
    location_id: int
    condition: Condition = Condition.new_surplus
    has_mtr: bool = False
    price_per_unit: float


class AskOut(AskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantity_filled: float
    quantity_available: float
    status: ListingStatus
    created_at: datetime
    location: LocationOut


class BidCreate(SpecIn):
    buyer_name: str
    destination_location_id: int
    min_condition: Condition = Condition.used_as_is
    require_mtr: bool = False
    max_delivered_price_per_unit: float | None = None


class BidOut(BidCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantity_filled: float
    quantity_remaining: float
    status: ListingStatus
    created_at: datetime
    destination: LocationOut


class MatchOut(BaseModel):
    ask: AskOut
    matched_quantity: float
    substitution_type: SubstitutionType
    discount_pct: float
    substitution_note: str
    distance_miles: float | None
    freight_per_unit: float
    price_per_unit_fob: float
    delivered_price_per_unit: float


class TradeExecuteIn(BaseModel):
    ask_id: int
    bid_id: int
    quantity: float | None = None


class TradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ask_id: int
    bid_id: int
    product_type: ProductType
    nominal_size_in: float
    schedule_class: str
    grade: str
    substitution_type: SubstitutionType
    quantity: float
    unit: str
    price_per_unit_fob: float
    freight_per_unit: float
    delivered_price_per_unit: float
    origin_location_id: int
    destination_location_id: int
    traded_at: datetime


class ReferenceOut(BaseModel):
    product_types: list[str]
    nominal_sizes_in: list[float]
    schedules: list[str]
    grades: list[str]
    manufactures: list[str]
    end_types: list[str]
    conditions: list[str]
    grade_substitutions: list[dict]


class DashboardOut(BaseModel):
    open_asks: int
    open_bids: int
    trades_30d: int
    volume_30d_units: float
    recent_trades: list[TradeOut]
