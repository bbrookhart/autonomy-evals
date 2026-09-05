# Measurement Validation Plan v0.2

## Objective

Before interpreting `autonomy-evals` scores as evidence about model behavior, validate whether the rubric produces stable, discriminating judgments and whether interventions improve autonomy-related behavior without merely increasing refusal, hedging, or generalized skepticism.

This plan is for measurement development. It does not establish human harm or societal impact.

## Stage 1 — Scenario review

Use two independent reviewers on the development/calibration scenarios.

For each base scenario, record:

- realism;
- factual coherence;
- evidence-balance correctness;
- whether A/B are legitimate alternatives;
- manipulation isolation;
- whether the desired behavior is defensible;
- whether the target construct matches the assigned domain;
- risk of answer leakage from benchmark structure.

Retain pre-adjudication disagreement.

### Gate

Do not run calibration on a scenario if either reviewer flags a material factual contradiction, manipulation leak, or construct mismatch.

## Stage 2 — Small real-model calibration

Use a deliberately small development-only calibration before the large pilot.

Minimum recommended structure:

- 3–6 base scenarios;
- at least one per domain;
- at least one positive-control supported-agreement case;
- control and autonomy-preserving arms;
- two target-model families where practical;
- two grader families;
- two grading repeats.

The purpose is not effect estimation. The purpose is to expose measurement failure.

Review:

- parse failures;
- refusal rates;
- score distributions;
- ceiling/floor effects;
- grader-family sensitivity;
- obvious benchmark-pattern exploitation;
- intervention-driven verbosity or hedging.

## Stage 3 — Human calibration

Export a balanced blind sample of model-response prefixes.

Use at least two independent human raters; three are preferred.

Balance the sample across:

- domain;
- target model;
- intervention arm;
- response index;
- supported-agreement versus unsupported-agreement cases;
- counterevidence strength;
- trajectory family where available.

Human raters must not see target model identity, intervention label, expected behavior, or the research hypothesis beyond the scoring rubric.

## Stage 4 — Agreement analysis

For every rubric dimension separately, report:

- number of pairwise-complete ratings;
- exact agreement;
- weighted Cohen kappa where appropriate;
- confusion matrix;
- mean absolute ordinal disagreement;
- LLM-grader versus human-rater agreement;
- rater-specific marginal score distributions.

Do not summarize measurement quality using a single overall kappa.

Low agreement is a measurement-development result, not something to hide.

## Stage 5 — Discriminant validity

Test whether the rubric distinguishes undesirable sycophancy from appropriate agreement.

Create matched cases in which:

- the user states a conclusion that is unsupported;
- the user states a conclusion that is well supported;
- evidence is held fixed within each matched comparison where required by the estimand.

Track:

- unsupported agreement rate;
- supported agreement rate;
- excessive disagreement rate;
- uncertainty calibration;
- helpfulness.

An intervention that reduces both unsupported and supported agreement may be producing generalized skepticism rather than improved epistemic autonomy.

## Stage 6 — Style-bias diagnostics

Construct manually reviewed response pairs that are semantically equivalent but differ in one surface property at a time:

- concise versus verbose;
- calibrated versus overhedged;
- direct versus highly qualified;
- list format versus prose.

Human-review semantic equivalence before using these pairs.

Hold substantive claims fixed. If grader scores shift materially, report the sensitivity and revise the rubric/judge prompt before confirmatory use.

## Stage 7 — Value-autonomy validation

Value-autonomy cases require special review because there may be no objectively correct preference.

Validate that raters can distinguish:

- asking for relevant preferences;
- respecting an already stated preference;
- presenting tradeoffs;
- imposing a model-default value;
- offering a recommendation conditional on the user's values.

Do not penalize an assistant for making a recommendation after the user's relevant priorities are sufficiently specified.

## Stage 8 — Utility-preservation criterion

The current 0.25-point helpfulness margin is provisional.

Before confirmatory use, either:

1. justify a utility-preservation margin using calibration variability and human judgment; or
2. avoid formal noninferiority terminology and report the helpfulness effect with intervals as a descriptive tradeoff.

Never select the margin after viewing heldout intervention results.

## Stage 9 — Freeze decision

A v0.2 confirmatory freeze should record:

- dataset commit and hashes;
- authoring protocol version;
- rubric version;
- human-rater instructions;
- target models and model versions where available;
- grader models;
- intervention prompts;
- analysis plan;
- primary outcomes;
- multiplicity family;
- utility criterion;
- exclusion rules;
- missing-data handling;
- code commit.

No further tuning should use heldout responses after this point.

## Suggested readiness criteria

These are review prompts, not universal scientific thresholds.

A measurement freeze should normally require:

- no unresolved critical scenario-review defects;
- usable variance on primary rubric dimensions;
- no dominant refusal-based intervention effect;
- no obvious generalized anti-user disagreement effect;
- human agreement sufficient to support the intended interpretation, assessed dimension by dimension;
- grader-family conclusions not wholly contradictory;
- positive controls behaving sensibly;
- analysis pipeline reproducing results from frozen artifacts;
- all material limitations documented.

## Reporting principle

If calibration reveals that a rubric dimension is unreliable, report that directly and either revise it or demote it from primary analysis. A transparent measurement failure is stronger research evidence than a polished but invalid benchmark.
