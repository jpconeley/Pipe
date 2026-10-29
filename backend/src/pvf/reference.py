"""Standard spec vocabulary for carbon steel line pipe on the Gulf Coast.

Kept narrow on purpose: the marketplace launches with line pipe only, so the
dropdowns and substitution table below cover that slice, not the full PVF
catalog. Valve/fitting/flange rows can exist in the schema but there is no
seed data or substitution logic for them yet.
"""

NOMINAL_SIZES_IN = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0]

SCHEDULES = ["Sch 40", "Sch 80", "STD", "XS"]

GRADES = ["A106-B", "A53-B", "API 5L X42", "API 5L X52", "API 5L B"]

# Approximate plain-end weight (lb/ft), per ASME B36.10 nominal wall thickness.
# "STD" is treated as equal to Sch 40 and "XS" as equal to Sch 80, which is
# exact through 10" and a close approximation above that. This is only used
# to estimate truckload freight for ranking matches by delivered price, not
# as an engineering reference.
PIPE_WEIGHT_LB_PER_FT: dict[tuple[float, str], float] = {
    (2.0, "Sch 40"): 3.65,
    (2.0, "Sch 80"): 5.02,
    (3.0, "Sch 40"): 7.58,
    (3.0, "Sch 80"): 10.25,
    (4.0, "Sch 40"): 10.79,
    (4.0, "Sch 80"): 14.98,
    (6.0, "Sch 40"): 18.97,
    (6.0, "Sch 80"): 28.57,
    (8.0, "Sch 40"): 28.55,
    (8.0, "Sch 80"): 43.39,
    (10.0, "Sch 40"): 40.48,
    (10.0, "Sch 80"): 54.74,
    (12.0, "Sch 40"): 49.56,
    (12.0, "Sch 80"): 65.42,
    (14.0, "Sch 40"): 54.57,
    (14.0, "Sch 80"): 72.09,
    (16.0, "Sch 40"): 62.58,
    (16.0, "Sch 80"): 82.77,
    (18.0, "Sch 40"): 70.59,
    (18.0, "Sch 80"): 104.13,
    (20.0, "Sch 40"): 78.60,
    (20.0, "Sch 80"): 123.11,
    (24.0, "Sch 40"): 94.62,
    (24.0, "Sch 80"): 171.17,
}
_SCH40 = list(PIPE_WEIGHT_LB_PER_FT.items())
PIPE_WEIGHT_LB_PER_FT.update({(size, "STD"): wt for (size, sch), wt in _SCH40 if sch == "Sch 40"})
PIPE_WEIGHT_LB_PER_FT.update({(size, "XS"): wt for (size, sch), wt in _SCH40 if sch == "Sch 80"})


def weight_lb_per_ft(nominal_size_in: float, schedule: str) -> float | None:
    return PIPE_WEIGHT_LB_PER_FT.get((nominal_size_in, schedule))


# (base_grade, sub_grade, bidirectional, discount_pct, note)
# discount_pct is applied to the ask's FOB price when it's used to fill a bid
# of a *different* grade, modeling the haircut a buyer expects for accepting
# a substitute instead of the exact grade they asked for.
GRADE_SUBSTITUTIONS: list[tuple[str, str, bool, float, str]] = [
    ("A106-B", "A53-B", True, 0.0, "Dual-certified A106-B/A53-B seamless is routinely sold as either."),
    ("API 5L X42", "API 5L X52", False, 0.0, "X52 exceeds X42 minimum yield strength, so it satisfies an X42 request."),
    ("API 5L B", "API 5L X42", False, 0.02, "X42 exceeds Grade B minimum yield; small discount since it's over-spec."),
]
