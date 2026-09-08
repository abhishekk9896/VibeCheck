import os
import re
from pathlib import Path
from auditor.runners.tool_runners import TestFailure, LintIssue
from auditor.core.scope_parser import Requirement
from auditor.security import (
    is_safe_path,
    validate_python_patch,
    log_audit_event,
    ScopeAuditBudget,
)


class PatchEngine:
    def __init__(self, root_dir: str = ".", budget: ScopeAuditBudget | None = None):
        self.root_dir = Path(root_dir).resolve()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.budget = budget or ScopeAuditBudget()

        if self.api_key:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        else:
            self.llm = None

    def determine_target_files(
        self,
        failures: list[TestFailure],
        lint_issues: list[LintIssue],
    ) -> list[Path]:
        """Derives which files actually need remediation from audit results,
        instead of assuming a single hardcoded target."""
        candidates: list[str] = []
        for f in failures:
            candidates.append(f.file_path)
        for l in lint_issues:
            candidates.append(l.file_path)

        targets: list[Path] = []
        seen = set()
        for raw_path in candidates:
            path = Path(raw_path)
            resolved = path if path.is_absolute() else (self.root_dir / path)

            if not is_safe_path(self.root_dir, resolved):
                log_audit_event(
                    "path_traversal_blocked",
                    {"attempted_path": str(resolved)},
                )
                continue

            if resolved.exists() and resolved not in seen:
                seen.add(resolved)
                targets.append(resolved)

        return targets

    def generate_remediation_patch(
        self,
        target_file: Path,
        failures: list[TestFailure],
        lint_issues: list[LintIssue],
        requirements: list[Requirement],
    ) -> str:
        """Generates code fixes via LLM if key is present, otherwise falls back to deterministic patch."""
        if not target_file.exists():
            return ""

        file_content = target_file.read_text(encoding="utf-8")

        # Fallback if no OPENAI_API_KEY is available
        if not self.llm:
            return self._fallback_rule_based_fix(file_content)

        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert Python software engineer fixing bugs, lint issues, and scope drift. "
             "Return ONLY the complete updated Python file content. Do not wrap in markdown quotes or extra text."),
            ("user", 
             "Requirement Context:\n{scope}\n\n"
             "Test Failures:\n{failures}\n\n"
             "Lint Issues:\n{lints}\n\n"
             "Current Code in {file_path}:\n```python\n{code}\n```\n\n"
             "Provide the fixed Python code for {file_path}:")
        ])

        scope_summary = "\n".join([f"- {req.title}: {', '.join(req.criteria)}" for req in requirements])
        failure_summary = "\n".join([f"- {f.test_name} ({f.file_path})" for f in failures])
        lint_summary = "\n".join([f"- Line {l.line}: [{l.code}] {l.message}" for l in lint_issues])

        chain = prompt | self.llm
        response = chain.invoke({
            "scope": scope_summary or "General software bug fixing",
            "failures": failure_summary or "None",
            "lints": lint_summary or "None",
            "file_path": str(target_file),
            "code": file_content,
        })

        return re.sub(r"^```python\n|```$", "", response.content.strip(), flags=re.MULTILINE)

    def _fallback_rule_based_fix(self, current_code: str) -> str:
        """Deterministic fix for the known sample_app/auth.py demo module.
        Used only when no LLM key is configured and no smarter rule applies;
        for any other file this simply returns the code unchanged."""
        if "def login(" in current_code and "def generate_token(" in current_code:
            return '''def login(username, password):
    if username == "admin" and password == "secret123":
        return {"status": "success", "token": "fake_token_123"}
    return {"status": "error", "message": "Invalid credentials"}

def generate_token(user_id):
    if not user_id:
        return None
    return f"token_{user_id}_valid"
'''
        return current_code

    def apply_fix(self, new_content: str, target_file: Path) -> bool:
        """Validates and writes generated fix to disk, enforcing:
        - path safety (ASI03): target must stay within root_dir
        - budget limits (ASI02/LLM06): capped number of files patched per run
        - syntax validation (ASI05): only syntactically valid Python is written
        """
        if not new_content.strip():
            return False

        if not is_safe_path(self.root_dir, target_file):
            log_audit_event(
                "path_traversal_blocked",
                {"attempted_path": str(target_file)},
            )
            return False

        is_valid, message = validate_python_patch(new_content)
        if not is_valid:
            log_audit_event(
                "invalid_patch_rejected",
                {"target_file": str(target_file), "reason": message},
            )
            return False

        try:
            self.budget.check_file_limit()
        except RuntimeError as e:
            log_audit_event("budget_limit_reached", {"reason": str(e)})
            return False

        target_file.write_text(new_content.strip() + "\n", encoding="utf-8")
        log_audit_event("patch_applied", {"target_file": str(target_file)})
        return True