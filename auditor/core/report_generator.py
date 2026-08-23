import html
from pathlib import Path
from auditor.core.agent import AuditorState


class ReportGenerator:
    def __init__(self, state: AuditorState, output_dir: str = "."):
        self.state = state
        self.output_dir = Path(output_dir).resolve()

    def generate_markdown(self, filename: str = "audit_report.md") -> Path:
        """Generates a GitHub-flavored Markdown report."""
        passed = self.state["passed_tests"]
        total = self.state["total_tests"]
        lints = len(self.state["lint_issues"])
        reqs = len(self.state["requirements"])
        missing_reqs = len(self.state["drift_report"].missing_requirements) if self.state.get("drift_report") else 0

        status_badge = "✅ PASSED" if (passed == total and lints == 0 and missing_reqs == 0) else "⚠️ FAILED"

        md_content = f"""# 🛡️ Scope Auditor Report

**Overall Status:** {status_badge}  
**Project Root:** `{self.state['root_dir']}`  
**Scope Spec:** `{self.state['scope_path']}`  

---

## 📊 Summary Metrics

| Metric | Value |
| :--- | :---: |
| **Parsed Requirements** | `{reqs}` |
| **AST Mapped Files** | `{len(self.state['ast_maps'])}` |
| **Ruff Lint Issues** | `{lints}` |
| **Pytest Pass Rate** | `{passed}/{total}` |
| **Unimplemented Requirements** | `{missing_reqs}` |
| **Remediation Iterations** | `{self.state.get('iterations', 0)}` |

---

## 🔍 Detailed Results

### 1. Requirements Compliance
"""
        if self.state.get("requirements"):
            for req in self.state["requirements"]:
                md_content += f"- **{req.title}**\n"
                for c in req.criteria:
                    md_content += f"  - Criteria: {c}\n"
        else:
            md_content += "No requirements parsed.\n"

        md_content += "\n### 2. Linting Issues\n"
        if lints > 0:
            for lint in self.state["lint_issues"]:
                md_content += f"- `{lint.file_path}:{lint.line}`: **[{lint.code}]** {lint.message}\n"
        else:
            md_content += "✓ No lint issues found.\n"

        md_content += "\n### 3. Pytest Failures\n"
        if self.state["test_failures"]:
            for fail in self.state["test_failures"]:
                md_content += f"- **{fail.test_name}** (`{fail.file_path}`)\n```\n{fail.message}\n```\n"
        else:
            md_content += "✓ All tests passed successfully.\n"

        output_path = self.output_dir / filename
        output_path.write_text(md_content, encoding="utf-8")
        return output_path

    def generate_html(self, filename: str = "audit_report.html") -> Path:
        """Generates a self-contained, styled HTML report."""
        passed = self.state["passed_tests"]
        total = self.state["total_tests"]
        lints = len(self.state["lint_issues"])
        reqs = len(self.state["requirements"])
        missing_reqs = len(self.state["drift_report"].missing_requirements) if self.state.get("drift_report") else 0

        is_clean = (passed == total and lints == 0 and missing_reqs == 0)
        status_text = "PASSED" if is_clean else "FAILED"
        badge_color = "#10b981" if is_clean else "#ef4444"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Scope Auditor Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f9fafb; }}
    .header {{ background: #ffffff; padding: 24px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 24px; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; color: #ffffff; font-weight: bold; font-size: 0.875rem; background-color: {badge_color}; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb; text-align: center; }}
    .card .val {{ font-size: 1.5rem; font-weight: bold; color: #111827; }}
    .card .lbl {{ font-size: 0.875rem; color: #6b7280; }}
    .section {{ background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 16px; }}
    pre {{ background: #f3f4f6; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.875rem; }}
  </style>
</head>
<body>
  <div class="header">
    <span class="badge">{status_text}</span>
    <h2>Scope Auditor Executive Report</h2>
    <p>Target Root: <code>{html.escape(str(self.state['root_dir']))}</code> | Spec: <code>{html.escape(str(self.state['scope_path']))}</code></p>
  </div>

  <div class="grid">
    <div class="card"><div class="val">{reqs}</div><div class="lbl">Requirements</div></div>
    <div class="card"><div class="val">{len(self.state['ast_maps'])}</div><div class="lbl">Files Mapped</div></div>
    <div class="card"><div class="val">{lints}</div><div class="lbl">Lint Issues</div></div>
    <div class="card"><div class="val">{passed}/{total}</div><div class="lbl">Pytest Pass Rate</div></div>
    <div class="card"><div class="val">{missing_reqs}</div><div class="lbl">Missing Reqs</div></div>
  </div>

  <div class="section">
    <h3>Requirements Compliance</h3>
    <ul>
"""
        for req in self.state.get("requirements", []):
            html_content += f"      <li><strong>{html.escape(req.title)}</strong></li>\n"

        html_content += """    </ul>
  </div>

  <div class="section">
    <h3>Test Failures</h3>
"""
        if self.state["test_failures"]:
            for fail in self.state["test_failures"]:
                html_content += f"    <div><strong>{html.escape(fail.test_name)}</strong> (<code>{html.escape(fail.file_path)}</code>)<pre>{html.escape(fail.message)}</pre></div>\n"
        else:
            html_content += "    <p style='color: #10b981;'>✓ All tests passed!</p>\n"

        html_content += """  </div>
</body>
</html>
"""
        output_path = self.output_dir / filename
        output_path.write_text(html_content, encoding="utf-8")
        return output_path