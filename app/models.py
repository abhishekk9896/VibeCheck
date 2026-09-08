from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("AuditSession", back_populates="owner", cascade="all, delete-orphan")

class AuditSession(Base):
    __tablename__ = "audit_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    repo_source = Column(String, nullable=False)
    compliance_score = Column(Integer, default=0)
    status = Column(String, default="IN_PROGRESS")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="sessions")
    requirements = relationship("AuditRequirement", back_populates="session", cascade="all, delete-orphan")
    lint_issues = relationship("LintIssue", back_populates="session", cascade="all, delete-orphan")
    test_failures = relationship("TestFailure", back_populates="session", cascade="all, delete-orphan")
    events = relationship("AuditEvent", back_populates="session", cascade="all, delete-orphan")

class AuditRequirement(Base):
    __tablename__ = "audit_requirements"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audit_sessions.id", ondelete="CASCADE"), nullable=False)
    rule_name = Column(String, nullable=False)
    is_compliant = Column(Boolean, default=False)
    details = Column(Text, nullable=True)

    session = relationship("AuditSession", back_populates="requirements")

class LintIssue(Base):
    __tablename__ = "lint_issues"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audit_sessions.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    rule_id = Column(String, nullable=True)
    message = Column(Text, nullable=True)

    session = relationship("AuditSession", back_populates="lint_issues")

class TestFailure(Base):
    __tablename__ = "test_failures"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audit_sessions.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)

    session = relationship("AuditSession", back_populates="test_failures")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audit_sessions.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("AuditSession", back_populates="events")