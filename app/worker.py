import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Existing imports follow below:
from auditor.graph import create_auditor_graph
import os
import shutil
import tempfile
import git
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

# Import your existing LangGraph pipeline components
from auditor.graph import create_auditor_graph

def run_audit_task(session_id: int, repo_source: str, scope_content: str):
    db: Session = SessionLocal()
    temp_dir = None
    
    try:
        session = db.query(models.AuditSession).filter(models.AuditSession.id == session_id).first()
        if not session:
            return

        # 1. Determine target directory (Git URL vs Local Path)
        if repo_source.startswith("http://") or repo_source.startswith("https://") or repo_source.endswith(".git"):
            temp_dir = tempfile.mkdtemp(prefix="vibecheck_repo_")
            db.add(models.AuditEvent(
                session_id=session_id,
                event_type="GIT_CLONE",
                message=f"Cloning remote repository {repo_source}..."
            ))
            db.commit()
            git.Repo.clone_from(repo_source, temp_dir)
            target_path = temp_dir
        else:
            target_path = repo_source

        # 2. Write custom SCOPE.md into target workspace
        scope_filepath = os.path.join(target_path, "SCOPE.md")
        with open(scope_filepath, "w", encoding="utf-8") as f:
            f.write(scope_content)

        # 3. Log AST/Graph Execution start
        db.add(models.AuditEvent(
            session_id=session_id,
            event_type="AUDIT_START",
            message="Initializing LangGraph execution loop..."
        ))
        db.commit()

        # 4. Invoke LangGraph pipeline
        app_graph = create_auditor_graph()
        initial_state = {
            "target_dir": target_path,
            "scope_file": scope_filepath,
            "requirements": [],
            "lint_issues": [],
            "test_failures": [],
            "compliance_score": 0
        }
        
        final_state = app_graph.invoke(initial_state)

        # 5. Persist Results to PostgreSQL
        session.compliance_score = final_state.get("compliance_score", 0)
        session.status = "COMPLETED"

        for req in final_state.get("requirements", []):
            db.add(models.AuditRequirement(
                session_id=session_id,
                rule_name=req.get("rule_name", "Unknown"),
                is_compliant=req.get("is_compliant", False),
                details=req.get("details", "")
            ))

        for lint in final_state.get("lint_issues", []):
            db.add(models.LintIssue(
                session_id=session_id,
                file_path=lint.get("file", ""),
                line_number=lint.get("line", 0),
                rule_id=lint.get("code", ""),
                message=lint.get("message", "")
            ))

        for test in final_state.get("test_failures", []):
            db.add(models.TestFailure(
                session_id=session_id,
                test_name=test.get("nodeid", ""),
                error_message=test.get("message", ""),
                traceback=test.get("traceback", "")
            ))

        db.add(models.AuditEvent(
            session_id=session_id,
            event_type="AUDIT_COMPLETE",
            message="Audit successfully completed."
        ))
        db.commit()

    except Exception as e:
        db.rollback()
        session = db.query(models.AuditSession).filter(models.AuditSession.id == session_id).first()
        if session:
            session.status = "FAILED"
            db.add(models.AuditEvent(
                session_id=session_id,
                event_type="AUDIT_ERROR",
                message=f"Audit execution failed: {str(e)}"
            ))
            db.commit()
    finally:
        db.close()
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)