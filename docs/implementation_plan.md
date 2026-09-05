# Implementation note
1. Define validated schemas and controlled pairing, then prove one-scenario mock run → saved transcript → rubric-shaped test score → clustered summary.
2. Expand authored base cases and crossed variants; enforce split and evidence invariants.
3. Add interventions, Inspect provider adapter, blinded multi-judge scoring, annotation round-trip.
4. Add checkpoint resume, usage estimates, statistical and plotting/report exports.
5. Test failure paths, scientific invariants and offline integration; package docs and reproducible environment.

Portable Pydantic records, JSONL datasets and immutable run directories separate inference from grading. Inspect-specific imports live under inspect/. Standard-library argparse avoids an extra CLI framework. Consolidate small rubric definitions in a single registry rather than one near-empty file per dimension. Mock rubric values are explicit synthetic fixtures, never substantive measurements. No API credentials are needed for CI.

## Hardening milestone completed
The follow-up audit corrected model-pooled tradeoff decisions, uncounted absent artifacts, mock noninferiority flags, stale-score/report reuse, omitted judge retry costs, annotation linkage overwrite risk and insufficient experimental-control validation. Model/grader effect sensitivity, conditional recovery and a small calibration preparation workflow are now included. See `docs/completion_status.md` for executed checks and external research dependencies.
