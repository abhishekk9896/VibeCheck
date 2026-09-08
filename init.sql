CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    repo_source VARCHAR(255) NOT NULL, -- Git URL or local path
    compliance_score INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS', -- IN_PROGRESS, COMPLETED, FAILED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_requirements (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
    rule_name VARCHAR(255) NOT NULL,
    is_compliant BOOLEAN DEFAULT FALSE,
    details TEXT
);

CREATE TABLE IF NOT EXISTS lint_issues (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
    file_path VARCHAR(550) NOT NULL,
    line_number INTEGER,
    rule_id VARCHAR(100),
    message TEXT
);

CREATE TABLE IF NOT EXISTS test_failures (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    error_message TEXT,
    traceback TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- e.g., 'AST_PARSED', 'RUFF_EXEC', 'SCOPE_VIOLATION'
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);