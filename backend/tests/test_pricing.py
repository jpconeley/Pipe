from pvf.config import Settings
from pvf.pricing import estimate_freight, haversine_miles


def test_haversine_houston_to_beaumont_is_roughly_right():
    houston = (29.7604, -95.3698)
    beaumont = (30.0802, -94.1266)
    miles = haversine_miles(*houston, *beaumont)
    assert 75 < miles < 90


def test_estimate_freight_scales_with_distance():
    settings = Settings(freight_rate_per_mile=2.0, freight_min_per_load=100, truck_capacity_tons=20)
    near = estimate_freight(
        origin_lat=29.0, origin_lon=-95.0, dest_lat=29.1, dest_lon=-95.1,
        nominal_size_in=6.0, schedule_class="Sch 40", quantity_ft=1000, settings=settings,
    )
    far = estimate_freight(
        origin_lat=29.0, origin_lon=-95.0, dest_lat=32.0, dest_lon=-90.0,
        nominal_size_in=6.0, schedule_class="Sch 40", quantity_ft=1000, settings=settings,
    )
    assert near is not None and far is not None
    assert far.freight_per_unit > near.freight_per_unit


def test_estimate_freight_unknown_spec_returns_none():
    settings = Settings()
    result = estimate_freight(
        origin_lat=29.0, origin_lon=-95.0, dest_lat=29.1, dest_lon=-95.1,
        nominal_size_in=99.0, schedule_class="Sch 999", quantity_ft=1000, settings=settings,
    )
    assert result is None


def test_estimate_freight_hits_minimum_per_load_for_small_quantity():
    settings = Settings(freight_rate_per_mile=0.01, freight_min_per_load=350, truck_capacity_tons=20)
    result = estimate_freight(
        origin_lat=29.0, origin_lon=-95.0, dest_lat=29.01, dest_lon=-95.01,
        nominal_size_in=6.0, schedule_class="Sch 40", quantity_ft=100, settings=settings,
    )
    assert result is not None
    assert result.freight_total == 350
