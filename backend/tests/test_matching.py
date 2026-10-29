import pytest

from pvf.config import Settings
from pvf.matching import find_matches, grade_match
from pvf.models import Ask, Bid, Condition, EndType, GradeSubstitution, Location, Manufacture, SubstitutionType


@pytest.fixture
def locations(db):
    houston = Location(name="Houston", city="Houston", state="TX", lat=29.7604, lon=-95.3698)
    beaumont = Location(name="Beaumont", city="Beaumont", state="TX", lat=30.0802, lon=-94.1266)
    corpus = Location(name="Corpus Christi", city="Corpus Christi", state="TX", lat=27.8006, lon=-97.3964)
    db.add_all([houston, beaumont, corpus])
    db.flush()
    return {"houston": houston, "beaumont": beaumont, "corpus": corpus}


@pytest.fixture
def substitutions(db):
    db.add(
        GradeSubstitution(
            base_grade="A106-B", sub_grade="A53-B", bidirectional=True, discount_pct=0.0, note="dual-cert"
        )
    )
    db.add(
        GradeSubstitution(
            base_grade="API 5L X42", sub_grade="API 5L X52", bidirectional=False, discount_pct=0.0, note="over-spec"
        )
    )
    db.flush()


def _ask(**overrides):
    defaults = dict(
        seller_name="Test Seller",
        product_type="pipe",
        nominal_size_in=6.0,
        schedule_class="Sch 40",
        grade="A106-B",
        manufacture=Manufacture.seamless,
        end_type=EndType.plain_end,
        quantity=1000,
        condition=Condition.new_surplus,
        has_mtr=True,
        price_per_unit=14.00,
    )
    defaults.update(overrides)
    return Ask(**defaults)


def _bid(**overrides):
    defaults = dict(
        buyer_name="Test Buyer",
        product_type="pipe",
        nominal_size_in=6.0,
        schedule_class="Sch 40",
        grade="A106-B",
        end_type=EndType.na,
        quantity=500,
        min_condition=Condition.used_as_is,
        require_mtr=False,
    )
    defaults.update(overrides)
    return Bid(**defaults)


def test_grade_match_exact(db, substitutions):
    gm = grade_match(db, "A106-B", "A106-B")
    assert gm.substitution_type == SubstitutionType.exact


def test_grade_match_bidirectional_substitute(db, substitutions):
    assert grade_match(db, "A106-B", "A53-B") is not None
    assert grade_match(db, "A53-B", "A106-B") is not None


def test_grade_match_one_way_substitute_only_satisfies_the_lower_spec(db, substitutions):
    # X52 satisfies an X42 request...
    assert grade_match(db, "API 5L X42", "API 5L X52") is not None
    # ...but an X52 request is not satisfied by X42.
    assert grade_match(db, "API 5L X52", "API 5L X42") is None


def test_grade_match_unrelated_grades_dont_match(db, substitutions):
    assert grade_match(db, "A106-B", "API 5L X42") is None


def test_find_matches_ranks_by_delivered_price_not_by_exactness(db, locations, substitutions):
    # The substitute is cheaper FOB and closer, so it should outrank the exact match
    # even though it's a substitute grade.
    exact_ask = _ask(grade="A106-B", location_id=locations["houston"].id, price_per_unit=14.50)
    cheap_substitute_ask = _ask(grade="A53-B", location_id=locations["beaumont"].id, price_per_unit=10.00)
    db.add_all([exact_ask, cheap_substitute_ask])

    bid = _bid(grade="A106-B", destination_location_id=locations["corpus"].id, require_mtr=True)
    db.add(bid)
    db.flush()

    matches = find_matches(db, bid)
    assert len(matches) == 2
    assert matches[0].ask.id == cheap_substitute_ask.id
    assert matches[0].substitution_type == SubstitutionType.substitute
    assert matches[0].delivered_price_per_unit < matches[1].delivered_price_per_unit


def test_find_matches_excludes_asks_below_required_condition(db, locations, substitutions):
    used_ask = _ask(condition=Condition.used_as_is, location_id=locations["houston"].id)
    db.add(used_ask)
    bid = _bid(min_condition=Condition.new_surplus, destination_location_id=locations["corpus"].id)
    db.add(bid)
    db.flush()

    assert find_matches(db, bid) == []


def test_find_matches_excludes_asks_without_mtr_when_required(db, locations, substitutions):
    no_mtr_ask = _ask(has_mtr=False, location_id=locations["houston"].id)
    db.add(no_mtr_ask)
    bid = _bid(require_mtr=True, destination_location_id=locations["corpus"].id)
    db.add(bid)
    db.flush()

    assert find_matches(db, bid) == []


def test_find_matches_respects_max_delivered_price(db, locations, substitutions):
    pricey_ask = _ask(price_per_unit=100.00, location_id=locations["houston"].id)
    db.add(pricey_ask)
    bid = _bid(destination_location_id=locations["corpus"].id, max_delivered_price_per_unit=20.00)
    db.add(bid)
    db.flush()

    assert find_matches(db, bid) == []
