import ast
import html
from pathlib import Path


def sanitize_audit_report(report_text: str) -> str:
    """Escapes HTML/XSS payloads before writing to executive HTML reports or PR descriptions."""
    return html.escape(report_text)


def validate_python_patch(code_patch: str) -> tuple[bool, str]:
    """Validates that LLM-generated code patches are syntactically sound before writing to disk (ASI05 mitigation)."""
    try:
        ast.parse(code_patch)
        return True, "Valid Python code syntax."
    except SyntaxError as e:
        return False, f"Syntax error detected in generated code patch: {e}"


def is_safe_path(base_dir: str | Path, target_path: str | Path) -> bool:
    """Prevents path traversal attacks by checking if target path is strictly within base directory (ASI03 mitigation)."""
    base = Path(base_dir).resolve()
    target = Path(target_path).resolve()
    return base in target.parents or base == target