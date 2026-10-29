import math
from dataclasses import dataclass

from pvf.config import Settings
from pvf.reference import weight_lb_per_ft


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_miles = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r_miles * math.asin(math.sqrt(a))

ROAD_DISTANCE_FACTOR = 1.15


@dataclass
class FreightEstimate:
    distance_miles: float
    total_weight_tons: float
    loads: int
    freight_total: float
    freight_per_unit: float


def estimate_freight(
    *,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    nominal_size_in: float,
    schedule_class: str,
    quantity_ft: float,
    settings: Settings,
) -> FreightEstimate | None:
    """Estimate truckload freight cost for a quantity of pipe, in linear feet.

    Freight is priced by weight (truckloads), not distance alone, so this
    converts quantity to tons via the standard pipe weight table before
    pricing loads at a flat $/mile lane rate. Returns None if the spec isn't
    in the weight table (freight can't be estimated for it yet).
    """
    lb_per_ft = weight_lb_per_ft(nominal_size_in, schedule_class)
    if lb_per_ft is None or quantity_ft <= 0:
        return None

    distance = haversine_miles(origin_lat, origin_lon, dest_lat, dest_lon) * ROAD_DISTANCE_FACTOR
    total_weight_tons = (lb_per_ft * quantity_ft) / 2000
    loads = max(1, math.ceil(total_weight_tons / settings.truck_capacity_tons))
    freight_total = loads * max(settings.freight_min_per_load, distance * settings.freight_rate_per_mile)
    freight_per_unit = freight_total / quantity_ft

    return FreightEstimate(
        distance_miles=distance,
        total_weight_tons=total_weight_tons,
        loads=loads,
        freight_total=freight_total,
        freight_per_unit=freight_per_unit,
    )
