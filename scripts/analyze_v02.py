"""Run canonical analysis and append v0.2 evidence-sensitive agreement diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from autonomy_evals.analysis.evidence_sensitivity import evidence_sensitive_agreement
from autonomy_evals.analysis.pipeline import analyze


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="Run directory, e.g. runs/v02-mock")
    args = parser.parse_args()

    folder = Path(args.run)
    output = analyze(folder)
    frame = pd.read_csv(output / "scores_long.csv")
    detail, discrimination = evidence_sensitive_agreement(frame)
    detail.to_csv(output / "evidence_sensitive_agreement.csv", index=False)
    discrimination.to_csv(output / "evidence_discrimination.csv", index=False)
    print(output / "evidence_sensitive_agreement.csv")
    print(output / "evidence_discrimination.csv")


if __name__ == "__main__":
    main()
