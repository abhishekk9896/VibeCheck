import html
from pathlib import Path

from auditor.core.agent import AuditorState


class ReportGenerator:
    def __init__(self, state: AuditorState, output_dir: str = "."):
        self.state = state
        self.output_dir = Path(output_dir).resolve()

    @staticmethod
    def _criterion_icon(status: str) -> str:
        return {
            "SATISFIED": "PASS",
            "VIOLATED": "FAIL",
            "UNCERTAIN": "UNCERTAIN",
        }.get(status, status)

    def generate_markdown(self, filename: str = "audit_report.md") -> Path:
        """Generate a GitHub-flavored Markdown audit report."""
        passed = self.state["passed_tests"]
        total = self.state["total_tests"]
        lints = len(self.state["lint_issues"])
        reqs = len(self.state["requirements"])

        missing_reqs = (
            len(self.state["drift_report"].missing_requirements)
            if self.state.get("drift_report")
            else 0
        )

        status_badge = (
            "PASSED"
            if passed == total and lints == 0 and missing_reqs == 0
            else "FAILED"
        )

        md_content = f"""# Scope Auditor Report

**Overall Status:** {status_badge}  
**Project Root:** `{self.state["root_dir"]}`  
**Scope Spec:** `{self.state["scope_path"]}`  

---

## Summary Metrics

| Metric | Value |
| :--- | :---: |
| **Parsed Requirements** | `{reqs}` |
| **AST Mapped Files** | `{len(self.state["ast_maps"])}` |
| **Ruff Lint Issues** | `{lints}` |
| **Pytest Pass Rate** | `{passed}/{total}` |
| **Unimplemented Requirements** | `{missing_reqs}` |
| **Remediation Iterations** | `{self.state.get("iterations", 0)}` |

---

## Detailed Results

### 1. Requirements Compliance
"""

        if self.state.get("requirements"):
            for req in self.state["requirements"]:
                md_content += f"- **{req.title}**\n"

                for criterion in req.criteria:
                    md_content += f"  - {criterion}\n"
        else:
            md_content += "No requirements parsed.\n"

        # ---------------------------------------------------------
        # Criterion Verification
        # ---------------------------------------------------------
        md_content += "\n### 2. Criterion Verification\n"

        criterion_results = self.state.get("criterion_results", [])

        if criterion_results:
            for requirement in criterion_results:
                md_content += (
                    f"\n#### {requirement.title} "
                    f"(`{requirement.status}`)\n"
                )

                for result in requirement.criteria:
                    icon = self._criterion_icon(result.status)

                    md_content += (
                        f"\n- **{icon}** {result.criterion}\n"
                    )

                    if result.reason:
                        md_content += (
                            f"  - **Reason:** {result.reason}\n"
                        )

                    if result.evidence:
                        md_content += "  - **Evidence:**\n"

                        for evidence in result.evidence:
                            md_content += f"    - `{evidence}`\n"
        else:
            md_content += "No criterion verification results available.\n"

        # ---------------------------------------------------------
        # Linting
        # ---------------------------------------------------------
        md_content += "\n### 3. Linting Issues\n"

        if lints > 0:
            for lint in self.state["lint_issues"]:
                md_content += (
                    f"- `{lint.file_path}:{lint.line}`: "
                    f"**[{lint.code}]** {lint.message}\n"
                )
        else:
            md_content += "No lint issues found.\n"

        # ---------------------------------------------------------
        # Tests
        # ---------------------------------------------------------
        md_content += "\n### 4. Pytest Failures\n"

        if self.state["test_failures"]:
            for fail in self.state["test_failures"]:
                md_content += (
                    f"- **{fail.test_name}** "
                    f"(`{fail.file_path}`)\n"
                    f"```text\n{fail.message}\n```\n"
                )
        else:
            md_content += "All tests passed successfully.\n"

        output_path = self.output_dir / filename
        output_path.write_text(md_content, encoding="utf-8")

        return output_path

    def generate_html(self, filename: str = "audit_report.html") -> Path:
        """Generate a self-contained styled HTML audit report."""
        passed = self.state["passed_tests"]
        total = self.state["total_tests"]
        lints = len(self.state["lint_issues"])
        reqs = len(self.state["requirements"])

        missing_reqs = (
            len(self.state["drift_report"].missing_requirements)
            if self.state.get("drift_report")
            else 0
        )

        is_clean = (
            passed == total
            and lints == 0
            and missing_reqs == 0
            and all(
                result.status == "SATISFIED"
                for requirement in self.state.get("criterion_results", [])
                for result in requirement.criteria
            )
        )

        status_text = "PASSED" if is_clean else "FAILED"

        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Scope Auditor Report</title>

<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #1f2937;
    max-width: 1000px;
    margin: 40px auto;
    padding: 0 20px;
    background: #f9fafb;
}

.header,
.section {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    color: #ffffff;
    font-weight: bold;
    font-size: 0.875rem;
    background-color: #ef4444;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.card {
    background: #ffffff;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    text-align: center;
}

.card .val {
    font-size: 1.5rem;
    font-weight: bold;
    color: #111827;
}

.card .lbl {
    font-size: 0.875rem;
    color: #6b7280;
}

.criterion {
    border-left: 4px solid #d1d5db;
    padding: 12px 16px;
    margin: 12px 0;
    background: #f9fafb;
}

.criterion.pass {
    border-left-color: #10b981;
}

.criterion.fail {
    border-left-color: #ef4444;
}

.criterion.uncertain {
    border-left-color: #f59e0b;
}

.status {
    font-weight: bold;
}

.evidence {
    margin-top: 8px;
}

.evidence code {
    display: block;
    background: #f3f4f6;
    padding: 4px 8px;
    margin: 3px 0;
    border-radius: 4px;
}

pre {
    background: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
}
</style>
</head>

<body>
"""

        badge_text = html.escape(status_text)

        html_content += f"""
<div class="header">
    <span class="badge">{badge_text}</span>
    <h2>Scope Auditor Executive Report</h2>
    <p>
        Target Root:
        <code>{html.escape(str(self.state["root_dir"]))}</code>
        |
        Spec:
        <code>{html.escape(str(self.state["scope_path"]))}</code>
    </p>
</div>

<div class="grid">
    <div class="card">
        <div class="val">{reqs}</div>
        <div class="lbl">Requirements</div>
    </div>

    <div class="card">
        <div class="val">{len(self.state["ast_maps"])}</div>
        <div class="lbl">Files Mapped</div>
    </div>

    <div class="card">
        <div class="val">{lints}</div>
        <div class="lbl">Lint Issues</div>
    </div>

    <div class="card">
        <div class="val">{passed}/{total}</div>
        <div class="lbl">Pytest Pass Rate</div>
    </div>

    <div class="card">
        <div class="val">{missing_reqs}</div>
        <div class="lbl">Missing Reqs</div>
    </div>
</div>
"""

        # ---------------------------------------------------------
        # Requirements
        # ---------------------------------------------------------
        html_content += """
<div class="section">
<h3>Requirements Compliance</h3>
<ul>
"""

        for req in self.state.get("requirements", []):
            html_content += (
                f"<li><strong>{html.escape(req.title)}</strong>"
                f"<ul>"
            )

            for criterion in req.criteria:
                html_content += (
                    f"<li>{html.escape(criterion)}</li>"
                )

            html_content += "</ul></li>"

        html_content += """
</ul>
</div>
"""

        # ---------------------------------------------------------
        # Criterion Verification
        # ---------------------------------------------------------
        html_content += """
<div class="section">
<h3>Criterion Verification</h3>
"""

        criterion_results = self.state.get("criterion_results", [])

        if criterion_results:
            for requirement in criterion_results:
                html_content += (
                    f"<h4>{html.escape(requirement.title)} "
                    f"({html.escape(requirement.status)})</h4>"
                )

                for result in requirement.criteria:
                    status_class = {
                        "SATISFIED": "pass",
                        "VIOLATED": "fail",
                        "UNCERTAIN": "uncertain",
                    }.get(result.status, "uncertain")

                    html_content += f"""
<div class="criterion {status_class}">
    <div>
        <span class="status">
            {html.escape(self._criterion_icon(result.status))}
        </span>
        {html.escape(result.criterion)}
    </div>
"""

                    if result.reason:
                        html_content += (
                            f"<p><strong>Reason:</strong> "
                            f"{html.escape(result.reason)}</p>"
                        )

                    if result.evidence:
                        html_content += (
                            '<div class="evidence">'
                            "<strong>Evidence:</strong>"
                        )

                        for evidence in result.evidence:
                            html_content += (
                                f"<code>{html.escape(evidence)}</code>"
                            )

                        html_content += "</div>"

                    html_content += "</div>"
        else:
            html_content += (
                "<p>No criterion verification results available.</p>"
            )

        html_content += """
</div>
"""

        # ---------------------------------------------------------
        # Test failures
        # ---------------------------------------------------------
        html_content += """
<div class="section">
<h3>Test Failures</h3>
"""

        if self.state["test_failures"]:
            for fail in self.state["test_failures"]:
                html_content += (
                    f"<div>"
                    f"<strong>{html.escape(fail.test_name)}</strong> "
                    f"(<code>{html.escape(fail.file_path)}</code>)"
                    f"<pre>{html.escape(fail.message)}</pre>"
                    f"</div>"
                )
        else:
            html_content += "<p>All tests passed.</p>"

        html_content += """
</div>
</body>
</html>
"""

        output_path = self.output_dir / filename
        output_path.write_text(html_content, encoding="utf-8")

        return output_path
