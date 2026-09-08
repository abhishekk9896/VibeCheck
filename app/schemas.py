from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Audit Detail Schemas ---
class AuditRequirementSchema(BaseModel):
    rule_name: str
    is_compliant: bool
    details: Optional[str] = None

    class Config:
        from_attributes = True

class LintIssueSchema(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    rule_id: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True

class TestFailureSchema(BaseModel):
    test_name: str
    error_message: Optional[str] = None
    traceback: Optional[str] = None

    class Config:
        from_attributes = True

class AuditEventSchema(BaseModel):
    event_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Session Schemas ---
class AuditSessionCreate(BaseModel):
    repo_source: str
    scope_content: str  # Content of SCOPE.md provided by user

class AuditSessionResponse(BaseModel):
    id: int
    repo_source: str
    compliance_score: int
    status: str
    created_at: datetime
    requirements: List[AuditRequirementSchema] = []
    lint_issues: List[LintIssueSchema] = []
    test_failures: List[TestFailureSchema] = []
    events: List[AuditEventSchema] = []

    class Config:
        from_attributes = True