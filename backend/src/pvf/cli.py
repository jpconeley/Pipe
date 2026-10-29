import sys

from pvf.db import get_sessionmaker
from pvf.seed import seed_demo, seed_reference

COMMANDS = {}


def command(name):
    def wrap(fn):
        COMMANDS[name] = fn
        return fn

    return wrap


@command("seed-reference")
def _seed_reference():
    with get_sessionmaker()() as db:
        seed_reference(db)
    print("Seeded reference data (locations, grade substitutions).")


@command("seed-demo")
def _seed_demo():
    with get_sessionmaker()() as db:
        seed_demo(db)
    print("Seeded demo asks, bids, and price history.")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: pvf <{'|'.join(COMMANDS)}>")
        raise SystemExit(1)
    COMMANDS[sys.argv[1]]()
