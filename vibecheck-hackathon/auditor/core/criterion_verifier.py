from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from auditor.core.scope_parser import Requirement
from auditor.core.codebase_mapper import FileASTMap, FunctionMap


CriterionStatus = Literal["SATISFIED", "VIOLATED", "UNCERTAIN"]


class CriterionResult(BaseModel):
    criterion: str
    status: CriterionStatus
    evidence: list[str] = Field(default_factory=list)
    reason: str = ""


class RequirementResult(BaseModel):
    requirement_id: str
    title: str
    status: Literal["SATISFIED", "PARTIAL", "VIOLATED", "UNCERTAIN"]
    criteria: list[CriterionResult] = Field(default_factory=list)


class CriterionVerifier:
    """Evidence-oriented criterion verifier for the Scope Auditor."""

    def __init__(
        self,
        requirements: list[Requirement],
        ast_maps: list[FileASTMap],
        root_dir: str | Path,
    ):
        self.requirements = requirements
        self.ast_maps = ast_maps
        self.root_dir = Path(root_dir)

    def verify(self) -> list[RequirementResult]:
        results = []

        for requirement in self.requirements:
            criteria = [
                self._verify_criterion(criterion)
                for criterion in requirement.criteria
            ]

            statuses = {result.status for result in criteria}

            if not criteria:
                overall = "UNCERTAIN"
            elif statuses == {"SATISFIED"}:
                overall = "SATISFIED"
            elif statuses == {"VIOLATED"}:
                overall = "VIOLATED"
            elif "SATISFIED" in statuses and "VIOLATED" in statuses:
                overall = "PARTIAL"
            else:
                overall = "UNCERTAIN"

            results.append(
                RequirementResult(
                    requirement_id=requirement.id,
                    title=requirement.title,
                    status=overall,
                    criteria=criteria,
                )
            )

        return results

    def _verify_criterion(self, criterion: str) -> CriterionResult:
        text = criterion.lower()

        matches: list[tuple[FileASTMap, FunctionMap]] = []

        for file_map in self.ast_maps:
            for function in file_map.functions:
                if self._function_matches_criterion(function.name, text):
                    matches.append((file_map, function))

        if not matches:
            # Before declaring uncertainty, check whether a test directly
            # demonstrates the criterion.
            test_evidence = self._find_test_evidence(text)

            if test_evidence:
                return CriterionResult(
                    criterion=criterion,
                    status=test_evidence["status"],
                    evidence=test_evidence["evidence"],
                    reason=test_evidence["reason"],
                )

            return CriterionResult(
                criterion=criterion,
                status="UNCERTAIN",
                reason="No relevant implementation function was found.",
            )

        evidence = self._implementation_evidence(matches)

        # Numeric behavioral requirements.
        expected_percent = self._extract_percent(text)

        if expected_percent is not None:
            expected_multiplier = round(1 - expected_percent / 100, 6)

            for _, function in matches:
                multiplier = self._extract_multiplier(function)

                if multiplier is not None:
                    if abs(multiplier - expected_multiplier) < 1e-6:
                        return CriterionResult(
                            criterion=criterion,
                            status="SATISFIED",
                            evidence=evidence,
                            reason=(
                                f"Implementation uses the expected "
                                f"{expected_percent:g}% discount."
                            ),
                        )

                    return CriterionResult(
                        criterion=criterion,
                        status="VIOLATED",
                        evidence=evidence,
                        reason=(
                            f"Expected multiplier "
                            f"{expected_multiplier:g}, "
                            f"but implementation uses {multiplier:g}."
                        ),
                    )

        # Correlate explicit expected-result criteria with tests.
        test_evidence = self._find_test_evidence(
            text,
            candidate_functions=[function.name for _, function in matches],
        )

        if test_evidence:
            return CriterionResult(
                criterion=criterion,
                status=test_evidence["status"],
                evidence=evidence + test_evidence["evidence"],
                reason=test_evidence["reason"],
            )

        if self._looks_like_rejection_requirement(text):
            return CriterionResult(
                criterion=criterion,
                status="UNCERTAIN",
                evidence=evidence,
                reason=(
                    "A relevant function exists, but static evidence alone "
                    "cannot prove rejection behavior."
                ),
            )

        return CriterionResult(
            criterion=criterion,
            status="SATISFIED",
            evidence=evidence,
            reason="Relevant implementation evidence was found.",
        )

    def _implementation_evidence(
        self,
        matches: list[tuple[FileASTMap, FunctionMap]],
    ) -> list[str]:
        evidence: list[str] = []

        for file_map, function in matches:
            evidence.append(
                f"implementation: {file_map.file_path}:{function.line_no} "
                f"function {function.name}"
            )

            evidence.extend(
                f"return: {value}"
                for value in function.returns
            )

            evidence.extend(
                f"constant: {value}"
                for value in function.constants
            )

            evidence.extend(
                f"calls: {value}"
                for value in function.calls
            )

            evidence.extend(
                f"operator: {value}"
                for value in function.operators
            )

        return evidence

    def _find_test_evidence(
        self,
        criterion: str,
        candidate_functions: list[str] | None = None,
    ) -> dict | None:
        expected_result = self._extract_expected_result(criterion)

        expected_input = self._extract_expected_input(criterion)

        if expected_result is None:
            return None

        candidate_set = set(candidate_functions or [])

        for file_map in self.ast_maps:
            if "test" not in str(file_map.file_path).lower():
                continue

            for function in file_map.functions:
                calls = set(function.calls)

                if candidate_set and not calls.intersection(candidate_set):
                    continue

                # Look for an explicit expected output in the test.
                if not self._contains_number(function, expected_result):
                    continue

                evidence = [
                    f"test: {file_map.file_path}:{function.line_no} "
                    f"function {function.name}"
                ]

                evidence.extend(
                    f"test constant: {value}"
                    for value in function.constants
                )

                evidence.extend(
                    f"test calls: {value}"
                    for value in function.calls
                )

                if expected_input is not None:
                    evidence.append(
                        f"expected input: {expected_input:g}"
                    )

                evidence.append(
                    f"expected result: {expected_result:g}"
                )

                # If we can evaluate the simple multiplier pattern from the
                # implementation, compare expected and predicted output.
                for production_map in self.ast_maps:
                    for production_function in production_map.functions:
                        if production_function.name not in calls:
                            continue

                        multiplier = self._extract_multiplier(
                            production_function
                        )

                        if (
                            multiplier is not None
                            and expected_input is not None
                        ):
                            actual = expected_input * multiplier

                            if abs(actual - expected_result) > 1e-6:
                                evidence.append(
                                    f"predicted result: {actual:g}"
                                )

                                return {
                                    "status": "VIOLATED",
                                    "evidence": evidence,
                                    "reason": (
                                        f"Test expects {expected_result:g}, "
                                        f"but static execution predicts "
                                        f"{actual:g}."
                                    ),
                                }

                            evidence.append(
                                f"predicted result: {actual:g}"
                            )

                            return {
                                "status": "SATISFIED",
                                "evidence": evidence,
                                "reason": (
                                    f"Static execution matches the "
                                    f"expected result {expected_result:g}."
                                ),
                            }

                return {
                    "status": "SATISFIED",
                    "evidence": evidence,
                    "reason": (
                        "A test explicitly asserts the expected result."
                    ),
                }

        return None

    @staticmethod
    def _function_matches_criterion(
        function_name: str,
        criterion: str,
    ) -> bool:
        function_tokens = set(
            re.findall(r"[a-zA-Z]+", function_name.lower())
        )

        criterion_tokens = set(
            re.findall(r"[a-zA-Z]+", criterion.lower())
        )

        stopwords = {
            "implement",
            "must",
            "should",
            "the",
            "and",
            "with",
            "before",
            "during",
            "after",
            "using",
            "return",
            "successful",
            "function",
            "percent",
            "purchase",
            "final",
            "price",
        }

        criterion_tokens -= stopwords

        return bool(function_tokens & criterion_tokens)

    @staticmethod
    def _extract_percent(text: str) -> float | None:
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:%|percent)",
            text,
        )

        return float(match.group(1)) if match else None

    @staticmethod
    def _extract_expected_result(text: str) -> float | None:
        patterns = (
            r"(?:result|results|equal|equals|final price)"
            r"\s*(?:of|to|=)?\s*(\d+(?:\.\d+)?)",
            r"must\s+be\s+(\d+(?:\.\d+)?)",
        )

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return float(match.group(1))

        return None

    @staticmethod
    def _extract_expected_input(text: str) -> float | None:
        match = re.search(
            r"(?:purchase|input|price|value|amount)"
            r"\s*(?:of|=)?\s*(\d+(?:\.\d+)?)",
            text,
        )

        return float(match.group(1)) if match else None

    @staticmethod
    def _extract_multiplier(function: FunctionMap) -> float | None:
        for value in function.constants:
            try:
                number = float(value.strip("'\""))
            except ValueError:
                continue

            if 0 < number < 1:
                return number

        for expression in function.returns:
            match = re.search(
                r"\*\s*(0?\.\d+)",
                expression,
            )

            if match:
                return float(match.group(1))

        return None

    @staticmethod
    def _contains_number(
        function: FunctionMap,
        expected: float,
    ) -> bool:
        for value in function.constants:
            cleaned = value.strip("'\"")

            try:
                if abs(float(cleaned) - expected) < 1e-6:
                    return True
            except ValueError:
                continue

        return False

    @staticmethod
    def _looks_like_rejection_requirement(text: str) -> bool:
        return any(
            word in text
            for word in (
                "reject",
                "invalid",
                "deny",
                "unauthorized",
                "unauthenticated",
                "must not",
                "never",
            )
        )
