from typing import TypedDict
from langgraph.graph import StateGraph, END

from auditor.core.scope_parser import ScopeParser, Requirement
from auditor.core.codebase_mapper import CodebaseMapper, FileASTMap
from auditor.core.drift_analyzer import DriftAnalyzer, ScopeDriftReport
from auditor.runners.tool_runners import SubprocessRunner, LintIssue, TestFailure
from auditor.core.patch_engine import PatchEngine
from auditor.security import (
    ScopeAuditBudget,
    sanitize_diff_for_auditing,
    log_audit_event,
)




class AuditorState(TypedDict):
    root_dir: str
    scope_path: str
    requirements: list[Requirement]
    ast_maps: list[FileASTMap]
    lint_issues: list[LintIssue]
    test_failures: list[TestFailure]
    total_tests: int
    passed_tests: int
    drift_report: ScopeDriftReport | None
    iterations: int
    status: str


def ingest_and_map_node(state: AuditorState) -> dict:
    parser = ScopeParser(state["scope_path"])
    requirements = parser.parse()

    # SCOPE.md is untrusted input in principle (e.g. shared/reviewed specs) —
    # screen it for prompt-injection style directives before it ever reaches
    # the remediation LLM prompt (ASI01 / LLM01 mitigation).
    from pathlib import Path
    scope_text = Path(state["scope_path"]).read_text(encoding="utf-8") if Path(state["scope_path"]).exists() else ""
    cleaned = sanitize_diff_for_auditing(state["scope_path"], scope_text)
    if cleaned.is_suspicious:
        log_audit_event(
            "prompt_injection_flagged_in_scope",
            {"scope_path": state["scope_path"], "reasons": cleaned.flagged_reasons},
        )

    mapper = CodebaseMapper(state["root_dir"])
    ast_maps = mapper.scan()

    return {
        "requirements": requirements,
        "ast_maps": ast_maps,
        "status": "ingested",
    }


def run_audits_node(state: AuditorState) -> dict:
    runner = SubprocessRunner(state["root_dir"])
    lint_issues = runner.run_ruff()
    test_failures, total_tests, passed_tests = runner.run_pytest()

    return {
        "lint_issues": lint_issues,
        "test_failures": test_failures,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "status": "audited",
    }


def analyze_drift_node(state: AuditorState) -> dict:
    analyzer = DriftAnalyzer(state["requirements"], state["ast_maps"])
    report = analyzer.analyze()

    return {
        "drift_report": report,
        "status": "drift_analyzed",
    }


def make_remediation_node(budget: ScopeAuditBudget):
    def remediation_node(state: AuditorState) -> dict:
        """Generates and applies LLM code patches to fix failing tests and lint
        errors, targeting whichever files the audit actually flagged rather
        than a single hardcoded path."""
        patcher = PatchEngine(state["root_dir"], budget=budget)

        target_files = patcher.determine_target_files(
            failures=state["test_failures"],
            lint_issues=state["lint_issues"],
        )

        patched_any = False
        for target_file in target_files:
            fixed_code = patcher.generate_remediation_patch(
                target_file=target_file,
                failures=state["test_failures"],
                lint_issues=state["lint_issues"],
                requirements=state["requirements"],
            )
            if fixed_code and patcher.apply_fix(fixed_code, target_file):
                patched_any = True

        return {
            "iterations": state.get("iterations", 0) + 1,
            "status": "remediated" if patched_any else "remediation_skipped",
        }

    return remediation_node


def make_check_audit_health(budget: ScopeAuditBudget):
    def check_audit_health(state: AuditorState) -> str:
        failures = len(state["test_failures"])
        lints = len(state["lint_issues"])
        iterations = state.get("iterations", 0)

        if (failures > 0 or lints > 0) and iterations < budget.max_graph_iterations:
            return "needs_remediation"
        return "clean"

    return check_audit_health


def build_auditor_graph():
    # Fresh budget guard per graph build: caps both the number of files
    # patched and the number of self-healing iterations for this audit run
    # (ASI02 / LLM06 mitigation), replacing the previous hardcoded "3".
    budget = ScopeAuditBudget(max_files_to_audit=20, max_graph_iterations=3)

    workflow = StateGraph(AuditorState)

    workflow.add_node("ingest_and_map", ingest_and_map_node)
    workflow.add_node("run_audits", run_audits_node)
    workflow.add_node("analyze_drift", analyze_drift_node)
    workflow.add_node("remediate", make_remediation_node(budget))

    workflow.set_entry_point("ingest_and_map")
    workflow.add_edge("ingest_and_map", "run_audits")
    workflow.add_edge("run_audits", "analyze_drift")

    workflow.add_conditional_edges(
        "analyze_drift",
        make_check_audit_health(budget),
        {
            "needs_remediation": "remediate",
            "clean": END,
        },
    )

    workflow.add_edge("remediate", "ingest_and_map")

    return workflow.compile()