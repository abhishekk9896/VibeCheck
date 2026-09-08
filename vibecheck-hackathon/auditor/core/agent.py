from typing import TypedDict

from langgraph.graph import END, StateGraph

from auditor.core.codebase_mapper import CodebaseMapper, FileASTMap
from auditor.core.criterion_verifier import CriterionVerifier, RequirementResult
from auditor.core.drift_analyzer import DriftAnalyzer, ScopeDriftReport
from auditor.core.patch_engine import PatchEngine
from auditor.core.scope_parser import Requirement, ScopeParser
from auditor.runners.tool_runners import (
    LintIssue,
    SubprocessRunner,
    TestFailure,
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
    criterion_results: list[RequirementResult]


def ingest_and_map_node(state: AuditorState) -> dict:
    parser = ScopeParser(state["scope_path"])
    requirements = parser.parse()

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
    analyzer = DriftAnalyzer(
        state["requirements"],
        state["ast_maps"],
    )

    report = analyzer.analyze()

    return {
        "drift_report": report,
        "status": "drift_analyzed",
    }


def verify_criteria_node(state: AuditorState) -> dict:
    verifier = CriterionVerifier(
        requirements=state["requirements"],
        ast_maps=state["ast_maps"],
        root_dir=state["root_dir"],
    )

    results = verifier.verify()

    return {
        "criterion_results": results,
        "status": "criteria_verified",
    }


def remediation_node(state: AuditorState) -> dict:
    """Generate and apply fixes for failing tests and lint issues."""

    patcher = PatchEngine(state["root_dir"])

    fixed_code = patcher.generate_remediation_patch(
        failures=state["test_failures"],
        lint_issues=state["lint_issues"],
        requirements=state["requirements"],
    )

    if fixed_code:
        patcher.apply_fix(fixed_code)

    return {
        "iterations": state.get("iterations", 0) + 1,
        "status": "remediated",
    }


def check_audit_health(state: AuditorState) -> str:
    failures = len(state["test_failures"])
    lints = len(state["lint_issues"])
    iterations = state.get("iterations", 0)

    if (failures > 0 or lints > 0) and iterations < 3:
        return "needs_remediation"

    return "clean"


def build_auditor_graph():
    workflow = StateGraph(AuditorState)

    workflow.add_node("ingest_and_map", ingest_and_map_node)
    workflow.add_node("run_audits", run_audits_node)
    workflow.add_node("analyze_drift", analyze_drift_node)
    workflow.add_node("verify_criteria", verify_criteria_node)
    workflow.add_node("remediate", remediation_node)

    workflow.set_entry_point("ingest_and_map")

    workflow.add_edge("ingest_and_map", "run_audits")
    workflow.add_edge("run_audits", "analyze_drift")
    workflow.add_edge("analyze_drift", "verify_criteria")

    workflow.add_conditional_edges(
        "verify_criteria",
        check_audit_health,
        {
            "needs_remediation": "remediate",
            "clean": END,
        },
    )

    workflow.add_edge("remediate", "ingest_and_map")

    return workflow.compile()