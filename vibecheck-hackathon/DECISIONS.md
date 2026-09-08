# Engineering Decisions

## Decision 1 — Preserve the Existing System

### Decision
Extend the existing VibeCheck system instead of replacing it.

### Reason
The hackathon asks participants to make the improvement from what existed before the competition clear. The existing Scope Auditor provides a useful baseline with scope parsing, code analysis, linting, testing, remediation and reporting.

---

## Decision 2 — Preserve the Frozen Benchmark

### Decision
Do not modify E01–E12.

### Reason
The same evaluation cases must be used for the baseline and final solution to make the measured comparison meaningful.

---

## Decision 3 — Criterion-Level Verification

### Decision
Introduce verification at the individual acceptance-criterion level.

### Reason
E02, E03 and E11 demonstrated that requirement-level matching can hide partially implemented requirements.

---

## Decision 4 — Evidence Before Verdict

### Decision
A final verdict should be supported by concrete evidence rather than symbol presence alone.

### Reason
E05 and E12 demonstrated that relevant function names can exist while the required behavior is absent.

---

## Decision 5 — Tests Are Evidence, Not the Entire Verification System

### Decision
Use tests when available, but do not treat the absence of tests as proof of compliance.

### Reason
E07 and E08 demonstrated that failing tests can expose behavioral violations, while E05 and E09 demonstrated cases where no tests existed and important violations were missed.

---

## Decision 6 — Explicit Uncertainty

### Decision
Allow the improved verifier to represent insufficient evidence or ambiguity explicitly.

### Reason
E10 showed that an ambiguous requirement does not necessarily justify a binary compliant/non-compliant decision.

---

## Decision 7 — Remediation Must Be Verified

### Decision
A patch should only be considered successful after verification passes.

### Reason
E07 and E08 exhausted remediation iterations without resolving the failing tests.

---

## Decision 8 — Deterministic Checks Remain Authoritative

### Decision
LLM reasoning may assist with interpretation and evidence gathering, but deterministic evidence such as test results should remain authoritative where available.

### Reason
The hackathon guidance emphasizes purposeful agent design and verification rather than adding components without demonstrated benefit.
