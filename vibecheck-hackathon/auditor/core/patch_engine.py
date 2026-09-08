import ast
import os
import re
from pathlib import Path

from auditor.runners.tool_runners import TestFailure, LintIssue
from auditor.core.scope_parser import Requirement


class PatchEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.target_file: Path | None = None

        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI

                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    temperature=0,
                )
            except ImportError:
                self.llm = None
        else:
            self.llm = None

    def generate_remediation_patch(
        self,
        failures: list[TestFailure],
        lint_issues: list[LintIssue],
        requirements: list[Requirement],
    ) -> str:
        target_file = self._find_target_file(failures)

        if target_file is None:
            return ""

        self.target_file = target_file

        file_content = target_file.read_text(encoding="utf-8")

        if self.llm:
            return self._generate_llm_patch(
                target_file=target_file,
                file_content=file_content,
                failures=failures,
                lint_issues=lint_issues,
                requirements=requirements,
            )

        return self._fallback_rule_based_fix(
            current_code=file_content,
            requirements=requirements,
        )

    def _find_target_file(
        self,
        failures: list[TestFailure],
    ) -> Path | None:
        """
        Resolve the implementation file associated with a failing test.

        Supports:
        - absolute test paths
        - paths relative to the audited project
        - paths relative to the repository root
        - paths containing a repository/project prefix
        """

        for failure in failures:
            raw_path = Path(failure.file_path)

            candidates: list[Path] = []

            if raw_path.is_absolute():
                candidates.append(raw_path)
            else:
                # Path relative to audited project.
                candidates.append(self.root_dir / raw_path)

                # Path relative to current working directory.
                candidates.append(Path.cwd() / raw_path)

                # If pytest supplied something such as:
                # vibecheck-hackathon\evaluation\cases\E07\tests\test_discount.py
                # extract everything beginning at "tests".
                if "tests" in raw_path.parts:
                    tests_index = raw_path.parts.index("tests")
                    relative_test_path = Path(
                        *raw_path.parts[tests_index:]
                    )

                    candidates.append(
                        self.root_dir / relative_test_path
                    )

            test_path: Path | None = None

            for candidate in candidates:
                candidate = candidate.resolve()

                if candidate.exists() and candidate.is_file():
                    test_path = candidate
                    break

            if test_path is None:
                continue

            try:
                tree = ast.parse(
                    test_path.read_text(encoding="utf-8"),
                    filename=str(test_path),
                )
            except (SyntaxError, OSError):
                continue

            imported_modules: list[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_modules.append(node.module)

                elif isinstance(node, ast.Import):
                    imported_modules.extend(
                        alias.name
                        for alias in node.names
                    )

            # Prefer modules imported by the failing test.
            for module in imported_modules:
                module_path = self.root_dir / (
                    module.replace(".", os.sep) + ".py"
                )

                if module_path.exists():
                    return module_path.resolve()

            # Fallback to app.py.
            fallback_candidates = [
                test_path.parent.parent / "app.py",
                self.root_dir / "app.py",
            ]

            for candidate in fallback_candidates:
                candidate = candidate.resolve()

                if candidate.exists():
                    return candidate

        return None

    def _generate_llm_patch(
        self,
        target_file: Path,
        file_content: str,
        failures: list[TestFailure],
        lint_issues: list[LintIssue],
        requirements: list[Requirement],
    ) -> str:
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are an expert Python software engineer "
                        "fixing a failing project. "
                        "Return ONLY the complete updated Python file. "
                        "Do not return markdown fences or explanations. "
                        "Preserve existing behavior unless the requirement "
                        "or failing test requires a change."
                    ),
                ),
                (
                    "user",
                    (
                        "Requirement Context:\n{scope}\n\n"
                        "Test Failures:\n{failures}\n\n"
                        "Lint Issues:\n{lints}\n\n"
                        "Current File: {file_path}\n"
                        "```python\n{code}\n```\n\n"
                        "Return the corrected complete Python file."
                    ),
                ),
            ]
        )

        scope_summary = "\n".join(
            f"- {req.title}: {', '.join(req.criteria)}"
            for req in requirements
        )

        failure_summary = "\n".join(
            f"- {failure.test_name}: {failure.message}"
            for failure in failures
        )

        lint_summary = "\n".join(
            f"- Line {lint.line}: [{lint.code}] {lint.message}"
            for lint in lint_issues
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "scope": scope_summary or "General software requirements",
                "failures": failure_summary or "None",
                "lints": lint_summary or "None",
                "file_path": str(target_file),
                "code": file_content,
            }
        )

        content = response.content.strip()

        content = re.sub(
            r"^```python\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

        return content.strip() + "\n"

    def _fallback_rule_based_fix(
        self,
        current_code: str,
        requirements: list[Requirement],
    ) -> str:
        updated = current_code

        requirement_text = " ".join(
            [
                req.title
                for req in requirements
            ]
            + [
                criterion
                for req in requirements
                for criterion in req.criteria
            ]
        ).lower()

        discount_match = re.search(
            r"(\d+(?:\.\d+)?)\s*percent\s+discount",
            requirement_text,
        )

        if discount_match:
            percentage = float(discount_match.group(1))
            expected_multiplier = 1 - (percentage / 100)

            multiplier_pattern = re.compile(
                r"(\bprice\s*\*\s*)(0\.\d+)"
            )

            if multiplier_pattern.search(updated):
                replacement = rf"\g<1>{expected_multiplier:g}"

                updated = multiplier_pattern.sub(
                    replacement,
                    updated,
                    count=1,
                )
        # Minimum password length requirements.
        length_match = re.search(
            r"(?:at least|minimum of)\s+(\d+)\s+characters",
            requirement_text,
        )

        if length_match:
            minimum_length = int(length_match.group(1))

            updated = re.sub(
                r"len\(\s*password\s*\)\s*>=\s*\d+",
                f"len(password) >= {minimum_length}",
                updated,
                count=1,
            )

        return updated

    def apply_fix(
        self,
        new_content: str,
        target_relative_path: str | None = None,
    ) -> bool:
        if target_relative_path:
            target_file = self.root_dir / target_relative_path
        else:
            target_file = self.target_file

        if target_file is None:
            return False

        target_file = target_file.resolve()

        try:
            target_file.relative_to(self.root_dir)
        except ValueError:
            return False

        if not target_file.exists():
            return False

        target_file.write_text(
            new_content,
            encoding="utf-8",
        )

        return True
