import json
import os
import re
import subprocess
from pathlib import Path

from pydantic import BaseModel


class LintIssue(BaseModel):
    file_path: str
    line: int
    code: str
    message: str


class TestFailure(BaseModel):
    test_name: str
    file_path: str
    message: str


class SubprocessRunner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()

    def run_ruff(self) -> list[LintIssue]:
        """Run Ruff against the audited project."""
        cmd = [
            "ruff",
            "check",
            "--output-format=json",
            str(self.root_dir),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        issues = []

        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)

                for item in data:
                    filename = item.get("filename", "")

                    # Ignore the auditor's own implementation.
                    if "auditor" in filename or "site-packages" in filename:
                        continue

                    issues.append(
                        LintIssue(
                            file_path=filename,
                            line=item.get("location", {}).get("row", 0),
                            code=item.get("code", ""),
                            message=item.get("message", ""),
                        )
                    )

            except json.JSONDecodeError:
                pass

        return issues

    def run_pytest(self) -> tuple[list[TestFailure], int, int]:
        """Run pytest inside the audited project."""

        test_dir = self.root_dir / "tests"

        target_path = (
            str(test_dir)
            if test_dir.exists()
            else str(self.root_dir)
        )

        # Make the audited project's root importable.
        env = os.environ.copy()
        env["PYTHONPATH"] = (
            str(self.root_dir)
            + os.pathsep
            + env.get("PYTHONPATH", "")
        )

        cmd = [
            "pytest",
            target_path,
            "-v",
            "--tb=short",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
        )

        stdout = result.stdout

        failures = []
        passed_tests = 0
        failed_tests = 0

        # Extract passed count.
        passed_match = re.search(
            r"(\d+)\s+passed",
            stdout,
        )

        if passed_match:
            passed_tests = int(passed_match.group(1))

        # Extract failed count.
        failed_match = re.search(
            r"(\d+)\s+failed",
            stdout,
        )

        if failed_match:
            failed_tests = int(failed_match.group(1))

        total_tests = passed_tests + failed_tests

        # Extract individual failed tests.
        for line in stdout.splitlines():
            line_str = line.strip()

            if not line_str.startswith("FAILED "):
                continue

            parts = line_str.replace(
                "FAILED ",
                "",
                1,
            ).split(" - ")

            raw_test_info = parts[0]

            test_parts = raw_test_info.split("::")

            file_p = test_parts[0]

            # Convert pytest's path into a path relative
            # to the audited project root.
            try:
                file_path = (
                    Path(file_p)
                    .resolve()
                    .relative_to(self.root_dir)
                )
                file_p = str(file_path)
            except ValueError:
                file_p = str(Path(file_p))

            test_name = (
                test_parts[1]
                if len(test_parts) > 1
                else raw_test_info
            )

            failures.append(
                TestFailure(
                    file_path=file_p,
                    test_name=test_name,
                    message="Test assertion failed",
                )
            )

        return failures, total_tests, passed_tests