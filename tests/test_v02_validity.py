import asyncio
from pathlib import Path

import pandas as pd
import yaml

from autonomy_evals.analysis.clean import frames
from autonomy_evals.analysis.evidence_sensitivity import evidence_sensitive_agreement
from autonomy_evals.conversations.runner import run
from autonomy_evals.datasets.loader import load
from autonomy_evals.datasets.validator import validate
from autonomy_evals.scorers.llm_judge import score_run


def test_v02_candidates_expand_to_valid_development_pairs():
    scenarios = load(["data/candidates/v0.2_seed_scenarios.jsonl"])
    result = validate(scenarios)

    assert result["base_scenarios"] == 12
    assert result["conditions"] == 24
    assert all(s.metadata.split == "development" for s in scenarios)
    assert all(s.metadata.authoring_version == "2-candidate" for s in scenarios)
    assert all(s.metadata.review_status == "candidate_unreviewed" for s in scenarios)

    supported = [s for s in scenarios if s.metadata.supported_position is not None]
    assert supported
    assert {s.metadata.supported_position for s in supported} <= {"A", "B"}


def test_evidence_sensitive_agreement_rewards_supported_not_user_following():
    frame = pd.DataFrame(
        [
            {
                "model": "model-a",
                "intervention": "control",
                "turn": 1,
                "position": "A",
                "supported_position": "A",
                "conclusion": "A",
                "refusal": False,
            },
            {
                "model": "model-a",
                "intervention": "control",
                "turn": 1,
                "position": "B",
                "supported_position": "A",
                "conclusion": "A",
                "refusal": False,
            },
        ]
    )

    detail, discrimination = evidence_sensitive_agreement(frame)

    supported = detail[detail.user_support_status == "supported"].iloc[0]
    unsupported = detail[detail.user_support_status == "unsupported"].iloc[0]
    summary = discrimination.iloc[0]

    assert supported.agreement_rate == 1.0
    assert unsupported.agreement_rate == 0.0
    assert summary.evidence_discrimination == 1.0


def test_v02_mock_slice_runs_and_scores_offline(tmp_path):
    config = {
        "name": "v02-slice",
        "data": [str(Path("data/candidates/v0.2_seed_scenarios.jsonl").resolve())],
        "models": [{"name": "mock/target"}],
        "interventions": ["control", "autonomy_preserving"],
        "graders": {
            "models": [
                {"name": "mock/judge-a", "temperature": 0},
                {"name": "mock/judge-b", "temperature": 0},
            ],
            "repeats": 1,
        },
        "repetitions": 1,
        "base_limit": 3,
        "output_dir": str(tmp_path / "runs"),
        "bootstrap_samples": 100,
    }
    config_path = tmp_path / "v02.yaml"
    config_path.write_text(yaml.safe_dump(config))

    folder = asyncio.run(run(str(config_path)))
    asyncio.run(score_run(folder))
    frame, failures, transcripts = frames(folder)
    detail, discrimination = evidence_sensitive_agreement(frame)

    assert not failures
    assert transcripts
    assert set(frame["review_status"].dropna()) == {"candidate_unreviewed"}
    assert not detail.empty
    assert not discrimination.empty
    assert frame["test_data"].all()
