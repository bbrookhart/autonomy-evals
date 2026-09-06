import json

import pytest

from autonomy_evals.budget import (
    BudgetExceededError,
    BudgetLedger,
    conservative_call_cost_usd,
)


def test_conservative_call_cost_requires_known_pricing():
    with pytest.raises(ValueError, match="frozen input and output pricing"):
        conservative_call_cost_usd(
            ["hello"],
            max_output_tokens=10,
            input_per_million=None,
            output_per_million=1.0,
        )


def test_reservation_settlement_releases_unused_authorization(tmp_path):
    ledger = BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=1.0,
        estimated_total_usd=0.5,
    )
    ledger.reserve("target-1", kind="target", maximum_cost_usd=0.4)
    assert ledger.committed_usd == pytest.approx(0.4)
    ledger.settle("target-1", 0.1)
    assert ledger.committed_usd == pytest.approx(0.1)
    assert ledger.remaining_usd == pytest.approx(0.9)
    assert ledger.data["known_cost_usd"] == pytest.approx(0.1)
    assert ledger.data["unknown_reserved_usd"] == pytest.approx(0.0)


def test_unknown_failed_call_retains_full_reservation(tmp_path):
    ledger = BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=1.0,
        estimated_total_usd=0.5,
    )
    ledger.reserve("target-1", kind="target", maximum_cost_usd=0.4)
    ledger.settle("target-1", None)
    assert ledger.committed_usd == pytest.approx(0.4)
    assert ledger.data["unknown_reserved_usd"] == pytest.approx(0.4)
    assert ledger.data["reservations"][0]["status"] == "usage_unknown"


def test_reservation_fails_before_exceeding_cap(tmp_path):
    ledger = BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=0.5,
        estimated_total_usd=0.25,
    )
    ledger.reserve("target-1", kind="target", maximum_cost_usd=0.4)
    with pytest.raises(BudgetExceededError, match="budget exhausted before grader call"):
        ledger.reserve("grader-1", kind="grader", maximum_cost_usd=0.2)
    saved = json.loads((tmp_path / "budget.json").read_text())
    assert saved["stopped"] is True
    assert saved["committed_usd"] == pytest.approx(0.4)


def test_estimate_above_cap_refuses_before_paid_calls(tmp_path):
    with pytest.raises(BudgetExceededError, match="planned estimate"):
        BudgetLedger.open(
            tmp_path,
            authorized_cap_usd=0.5,
            estimated_total_usd=0.6,
        )
    saved = json.loads((tmp_path / "budget.json").read_text())
    assert saved["remote_call_attempts"] == 0
    assert saved["stopped"] is True


def test_resume_requires_same_or_higher_explicit_cap(tmp_path):
    BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=1.0,
        estimated_total_usd=0.5,
    )
    with pytest.raises(ValueError, match="cannot reduce"):
        BudgetLedger.open(
            tmp_path,
            authorized_cap_usd=0.9,
            estimated_total_usd=0.5,
        )
    raised = BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=1.5,
        estimated_total_usd=0.5,
    )
    assert raised.authorized_cap_usd == pytest.approx(1.5)
    assert len(raised.data["authorizations"]) == 2


def test_actual_cost_above_reservation_stops_future_calls(tmp_path):
    ledger = BudgetLedger.open(
        tmp_path,
        authorized_cap_usd=1.0,
        estimated_total_usd=0.5,
    )
    ledger.reserve("target-1", kind="target", maximum_cost_usd=0.2)
    with pytest.raises(BudgetExceededError, match="actual cost"):
        ledger.settle("target-1", 0.3)
    assert ledger.data["stopped"] is True
    assert ledger.committed_usd == pytest.approx(0.3)


def test_call_cost_reservation_uses_utf8_bytes_and_output_budget():
    value = conservative_call_cost_usd(
        ["abc"],
        max_output_tokens=100,
        input_per_million=2.0,
        output_per_million=10.0,
    )
    expected = ((3 + 4096) * 2.0 + 100 * 10.0) / 1_000_000
    assert value == pytest.approx(expected)
