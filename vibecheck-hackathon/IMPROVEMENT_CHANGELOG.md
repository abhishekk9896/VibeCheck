# Improvement Changelog

## Baseline — Pre-Hackathon VibeCheck

### What existed
The original VibeCheck / Scope Auditor system was used unchanged.

### Why
Establish a reproducible starting point before making improvements.

### Evaluation
12 controlled evaluation cases: E01–E12.

### Key observations

- E01: Correctly identified a compliant repository.
- E02: Missed partially implemented requirement.
- E03: Missed multiple missing behavioral criteria.
- E04: Did not provide an explicit out-of-scope functionality result.
- E05: Treated relevant symbol presence as sufficient despite incorrect behavior.
- E06: Correctly handled a positive cross-file case.
- E07: Detected a failing behavioral test but remediation did not resolve it.
- E08: Detected a failing behavioral test but remediation did not resolve it.
- E09: Missed plaintext password storage violation without tests.
- E10: Flagged an ambiguous requirement as unresolved but did not explicitly represent uncertainty.
- E11: Detected an unresolved requirement but did not localize the failure to individual criteria.
- E12: Missed an authentication enforcement violation despite authentication-related symbols being present.

### Decision
Improve the existing system rather than replace it. Prioritize evidence-driven, criterion-level verification and subsequently improve remediation reliability.

---

## Iteration 1

Status: Planned

### Problem addressed
Criterion-level and evidence-based verification.

### Evidence
E02, E03, E05, E09, E11, E12.

### Decision
[To be completed after implementation and evaluation]

---

## Iteration 2

Status: Planned

### Problem addressed
Behavioral verification and security evidence.

### Evidence
E05, E09, E12.

### Decision
[To be completed after implementation and evaluation]

---

## Iteration 3

Status: Planned

### Problem addressed
Remediation reliability.

### Evidence
E07, E08.

### Decision
[To be completed after implementation and evaluation]

---

## Final

Status: Planned

### Combined changes
[To be completed]

### Final evaluation
[To be completed]

### Main contribution
[To be completed]

### Hot Take
[To be completed]
