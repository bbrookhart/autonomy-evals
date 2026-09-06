"""Fail-closed budget authorization for paid model and grader calls."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from autonomy_evals.io import atomic_json, read_json


class BudgetExceededError(ValueError):
    """Raised before a paid call would exceed the authorized budget."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def conservative_call_cost_usd(
    contents: Iterable[str],
    *,
    max_output_tokens: int,
    input_per_million: float | None,
    output_per_million: float | None,
) -> float:
    """Return a deliberately conservative reservation for one remote call.

    Input is bounded using UTF-8 byte length plus protocol overhead rather than the
    repository's four-characters-per-token planning heuristic. For text tokenizers,
    byte length is intentionally much more conservative than ordinary token counts.
    The extra 4096-token allowance covers provider message framing and metadata that
    are not represented in the visible message strings.

    This is an authorization reservation, not a prediction of the eventual invoice.
    A successful call releases the unused reservation when provider usage is known.
    Failed or usage-unknown calls retain the full reservation.
    """

    if input_per_million is None or output_per_million is None:
        raise ValueError("paid call requires frozen input and output pricing")
    if input_per_million < 0 or output_per_million < 0:
        raise ValueError("model pricing cannot be negative")
    if max_output_tokens < 0:
        raise ValueError("max output tokens cannot be negative")
    input_token_reservation = sum(len(text.encode("utf-8")) for text in contents) + 4096
    return (
        input_token_reservation * input_per_million
        + max_output_tokens * output_per_million
    ) / 1_000_000


class BudgetLedger:
    """Persistent authorization ledger shared by target inference and grading."""

    schema_version = "autonomy-evals.budget/v1"

    def __init__(self, path: Path, data: dict):
        self.path = path
        self.data = data

    @classmethod
    def open(
        cls,
        folder: Path,
        *,
        authorized_cap_usd: float,
        estimated_total_usd: float | None,
    ) -> "BudgetLedger":
        if authorized_cap_usd <= 0:
            raise ValueError("max cost must be greater than zero")
        if estimated_total_usd is None:
            raise ValueError("paid run requires known frozen pricing for every remote model")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "budget.json"
        if path.exists():
            data = read_json(path)
            if data.get("schema_version") != cls.schema_version:
                raise ValueError("unsupported budget ledger schema")
            current = float(data["authorized_cap_usd"])
            if authorized_cap_usd < current:
                raise ValueError(
                    "resume cannot reduce the recorded authorized cap; use the existing cap"
                )
            if authorized_cap_usd > current:
                data["authorized_cap_usd"] = authorized_cap_usd
                data.setdefault("authorizations", []).append(
                    {
                        "cap_usd": authorized_cap_usd,
                        "at": _now(),
                        "reason": "explicit resume authorization increase",
                    }
                )
                atomic_json(path, data)
            ledger = cls(path, data)
        else:
            data = {
                "schema_version": cls.schema_version,
                "authorized_cap_usd": authorized_cap_usd,
                "initial_authorized_cap_usd": authorized_cap_usd,
                "authorizations": [
                    {
                        "cap_usd": authorized_cap_usd,
                        "at": _now(),
                        "reason": "initial explicit run authorization",
                    }
                ],
                "estimated_total_usd": estimated_total_usd,
                "committed_usd": 0.0,
                "known_cost_usd": 0.0,
                "unknown_reserved_usd": 0.0,
                "remote_call_attempts": 0,
                "reservations": [],
                "stopped": False,
                "stop_reason": None,
                "created_at": _now(),
                "updated_at": _now(),
                "note": (
                    "Committed spend is an authorization accounting bound, not a provider invoice. "
                    "Unknown/failed calls retain their full pre-call reservation."
                ),
            }
            atomic_json(path, data)
            ledger = cls(path, data)
        if estimated_total_usd > authorized_cap_usd:
            ledger.stop(
                f"planned estimate ${estimated_total_usd:.6f} exceeds authorized cap "
                f"${authorized_cap_usd:.6f}"
            )
            raise BudgetExceededError(ledger.data["stop_reason"])
        return ledger

    @property
    def authorized_cap_usd(self) -> float:
        return float(self.data["authorized_cap_usd"])

    @property
    def committed_usd(self) -> float:
        return float(self.data["committed_usd"])

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.authorized_cap_usd - self.committed_usd)

    def stop(self, reason: str) -> None:
        self.data["stopped"] = True
        self.data["stop_reason"] = reason
        self.data["updated_at"] = _now()
        atomic_json(self.path, self.data)

    def reserve(self, call_id: str, *, kind: str, maximum_cost_usd: float) -> str:
        if maximum_cost_usd < 0:
            raise ValueError("call reservation cannot be negative")
        if any(item["call_id"] == call_id for item in self.data["reservations"]):
            raise ValueError(f"budget call id already exists: {call_id}")
        projected = self.committed_usd + maximum_cost_usd
        if projected > self.authorized_cap_usd + 1e-12:
            self.stop(
                f"budget exhausted before {kind} call {call_id}: reserving "
                f"${maximum_cost_usd:.6f} would raise committed authorization to "
                f"${projected:.6f} above cap ${self.authorized_cap_usd:.6f}"
            )
            raise BudgetExceededError(self.data["stop_reason"])
        reservation = {
            "call_id": call_id,
            "kind": kind,
            "maximum_cost_usd": maximum_cost_usd,
            "actual_cost_usd": None,
            "status": "reserved",
            "reserved_at": _now(),
            "settled_at": None,
        }
        self.data["reservations"].append(reservation)
        self.data["committed_usd"] = projected
        self.data["unknown_reserved_usd"] = (
            float(self.data["unknown_reserved_usd"]) + maximum_cost_usd
        )
        self.data["remote_call_attempts"] = int(self.data["remote_call_attempts"]) + 1
        self.data["updated_at"] = _now()
        atomic_json(self.path, self.data)
        return call_id

    def settle(self, call_id: str, actual_cost_usd: float | None) -> None:
        matches = [item for item in self.data["reservations"] if item["call_id"] == call_id]
        if len(matches) != 1:
            raise ValueError(f"unknown or ambiguous budget call id: {call_id}")
        reservation = matches[0]
        if reservation["status"] != "reserved":
            raise ValueError(f"budget call already settled: {call_id}")
        reserved = float(reservation["maximum_cost_usd"])
        reservation["settled_at"] = _now()
        if actual_cost_usd is None:
            reservation["status"] = "usage_unknown"
            self.data["updated_at"] = _now()
            atomic_json(self.path, self.data)
            return
        if actual_cost_usd < 0:
            raise ValueError("actual call cost cannot be negative")
        reservation["actual_cost_usd"] = actual_cost_usd
        self.data["unknown_reserved_usd"] = max(
            0.0, float(self.data["unknown_reserved_usd"]) - reserved
        )
        self.data["known_cost_usd"] = float(self.data["known_cost_usd"]) + actual_cost_usd
        if actual_cost_usd <= reserved + 1e-12:
            self.data["committed_usd"] = max(
                0.0, self.committed_usd - (reserved - actual_cost_usd)
            )
            reservation["status"] = "settled"
        else:
            # The paid call already occurred, so preserve the over-bound result and fail closed
            # for every subsequent call instead of hiding the reservation-model defect.
            self.data["committed_usd"] = self.committed_usd + (actual_cost_usd - reserved)
            reservation["status"] = "reservation_bound_exceeded"
            self.data["stopped"] = True
            self.data["stop_reason"] = (
                f"actual cost ${actual_cost_usd:.6f} exceeded pre-call reservation "
                f"${reserved:.6f} for {call_id}; no further paid calls are authorized"
            )
        self.data["updated_at"] = _now()
        atomic_json(self.path, self.data)
        if reservation["status"] == "reservation_bound_exceeded":
            raise BudgetExceededError(self.data["stop_reason"])
