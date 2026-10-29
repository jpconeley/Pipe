from fastapi import APIRouter
from sqlalchemy import select

from pvf.api.deps import SessionDep
from pvf.api.schemas import ReferenceOut
from pvf.models import Condition, EndType, GradeSubstitution, Manufacture, ProductType
from pvf.reference import GRADES, NOMINAL_SIZES_IN, SCHEDULES

router = APIRouter(prefix="/specs", tags=["specs"])


@router.get("/reference", response_model=ReferenceOut)
def reference(db: SessionDep):
    subs = db.execute(select(GradeSubstitution)).scalars().all()
    return ReferenceOut(
        product_types=[p.value for p in ProductType],
        nominal_sizes_in=NOMINAL_SIZES_IN,
        schedules=SCHEDULES,
        grades=GRADES,
        manufactures=[m.value for m in Manufacture],
        end_types=[e.value for e in EndType],
        conditions=[c.value for c in Condition],
        grade_substitutions=[
            {
                "base_grade": s.base_grade,
                "sub_grade": s.sub_grade,
                "bidirectional": s.bidirectional,
                "discount_pct": float(s.discount_pct),
                "note": s.note,
            }
            for s in subs
        ],
    )
