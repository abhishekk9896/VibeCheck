# Evaluation

## Objective

Measure whether the improved VibeCheck provides more reliable requirement verification than the pre-hackathon baseline.

## Benchmark

The evaluation uses the same frozen cases E01–E12 for baseline and final evaluation.

## Ground Truth

Each case has a manually defined expected outcome based on the known implementation and specification.

## Primary Metric

### Requirement Verification Accuracy

Number of correctly classified requirements divided by the number of evaluable requirements.

## Secondary Metrics

### Criterion Verification Accuracy

Correct criterion-level classifications divided by total evaluable criteria.

### Behavioral Detection Rate

Number of intentionally introduced behavioral violations detected by the system divided by the number of behavioral violation cases.

### Remediation Success Rate

Number of remediation cases successfully repaired and verified divided by remediation cases attempted.

### Regression Rate

Number of previously passing cases broken by an attempted improvement divided by cases modified.

## Evaluation Rule

The baseline and improved system must receive the same evaluation cases and equivalent inputs.

## Evidence

Every reported result should be traceable to:

- source files
- tests
- tool output
- generated reports
- evaluation case ground truth

## Baseline

Cases E01–E12 were executed using the unchanged pre-hackathon VibeCheck.

## Final Evaluation

The same E01–E12 cases will be executed against the improved system.

## Reproducibility

Exact setup commands, dependency versions, execution commands and expected outputs will be documented in the reproduction guide.

## Important Limitation

A requirement must not be considered correctly verified merely because a related symbol exists. Criterion-level evidence and behavioral evidence must be considered where applicable.
