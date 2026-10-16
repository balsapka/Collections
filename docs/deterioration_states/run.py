"""Run the package's tools from ANY folder (repo root, a notebook folder, anywhere):

    python docs/deterioration_states/run.py selftest [n_accounts]    # real-data path on synthetic data
    python docs/deterioration_states/run.py synthetic [n_accounts]   # method validation report
    python docs/deterioration_states/run.py bundle                   # rebuild BUNDLE.md

Equivalent to `python -m dpd_states.<tool>` run from inside docs/deterioration_states/.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # makes dpd_states importable

TOOLS = ("selftest", "synthetic", "bundle")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20_000
    if cmd == "selftest":
        from dpd_states.selftest import main as run
        return run(n)
    if cmd == "synthetic":
        from dpd_states.run_synthetic import main as run
        run(n)
        return 0
    if cmd == "bundle":
        from dpd_states.bundle import build
        print(build())
        return 0
    print(__doc__)
    print(f"unknown or missing tool {cmd!r}; choose one of {TOOLS}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
