"""Create a blinded-by-results scenario-quality review packet for v0.2 candidates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

FIELDS = [
    "base_id",
    "domain",
    "topic",
    "scenario_family",
    "trajectory_family",
    "context",
    "option_a",
    "option_b",
    "initial_evidence",
    "evidence_balance_initial",
    "later_information",
    "later_information_reliability",
    "user_value_revealed",
    "reviewer_id",
    "factual_coherence_0_2",
    "realism_0_2",
    "options_are_genuine_0_2",
    "evidence_balance_correct_0_2",
    "manipulation_isolated_0_2",
    "later_information_reliability_correct_0_2",
    "domain_fit_0_2",
    "repetition_pattern_risk_0_2",
    "irrelevant_normative_assumptions_0_2",
    "critical_issue",
    "review_notes",
    "recommendation",
]


def build_packet(source: Path, output: Path) -> Path:
    rows = []
    for line in source.read_text().splitlines():
        if not line.strip():
            continue
        candidate = json.loads(line)
        rows.append(
            {
                **{field: candidate.get(field, "") for field in FIELDS},
                "reviewer_id": "",
                "factual_coherence_0_2": "",
                "realism_0_2": "",
                "options_are_genuine_0_2": "",
                "evidence_balance_correct_0_2": "",
                "manipulation_isolated_0_2": "",
                "later_information_reliability_correct_0_2": "",
                "domain_fit_0_2": "",
                "repetition_pattern_risk_0_2": "",
                "irrelevant_normative_assumptions_0_2": "",
                "critical_issue": "",
                "review_notes": "",
                "recommendation": "",
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="data/candidates/v0.2_seed_scenarios.jsonl",
    )
    parser.add_argument(
        "--output",
        default="data/human_annotations/v0.2_scenario_review.csv",
    )
    args = parser.parse_args()
    print(build_packet(Path(args.source), Path(args.output)))


if __name__ == "__main__":
    main()
