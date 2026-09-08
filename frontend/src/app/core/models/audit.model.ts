export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface AuditRequirement {
  rule_name: string;
  is_compliant: boolean;
  details?: string;
}

export interface LintIssue {
  file_path: string;
  line_number?: number;
  rule_id?: string;
  message?: string;
}

export interface TestFailure {
  test_name: string;
  error_message?: string;
  traceback?: string;
}

export interface AuditEvent {
  event_type: string;
  message: string;
  created_at: string;
}

export interface AuditSession {
  id: number;
  repo_source: string;
  compliance_score: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  created_at: string;
  requirements: AuditRequirement[];
  lint_issues: LintIssue[];
  test_failures: TestFailure[];
  events: AuditEvent[];
}

export interface CreateAuditRequest {
  repo_source: string;
  scope_content: string;
}