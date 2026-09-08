# 🛡️ VibeCheck (`scope-auditor`)

> **LangGraph-powered Scope, Quality & Security Auditor Agent for Vibe-Coded Python Projects.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Linter](https://img.shields.io/badge/linter-Ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Testing](https://img.shields.io/badge/testing-Pytest-yellow.svg)](https://docs.pytest.org/)
[![Security](https://img.shields.io/badge/security-OWASP_ASI_Top_10-green.svg)](#-security--owasp-alignment)

**VibeCheck** is an autonomous developer agent built on **LangGraph**. It bridges the gap between rapid LLM prototyping ("vibe-coding") and production quality standards by auditing codebase feature alignment against `SCOPE.md`, enforcing linting rules via `ruff`, running test suites via `pytest`, and executing a self-healing remediation loop to fix breaking changes automatically.

---

## 🌟 Key Features

* **📜 Deterministic Scope Parser:** Converts human-readable `SCOPE.md` specifications into target verification constraints.
* **🔍 AST Symbol Indexer:** Statically analyzes codebase classes, functions, and import paths without code execution.
* **⚡ Subprocess Tool Runners:** Aggregates structured outputs from `ruff` for code quality and `pytest` for test suites.
* **🔁 Autonomous Self-Healing Loop:** Automatically fixes breaking tests and lint errors using OpenAI or offline rule-based patch generation, looping until tests pass.
* **🛡️ OWASP ASI Guardrails:** Built-in security suite enforcing prompt injection checks, system prompt leak protection, path safety, and iteration budgets.
* **📊 Rich CLI & Executive Reports:** Terminal interface powered by `rich`, with one-click export to `audit_report.md` and `audit_report.html`.

---

## 🏗️ Agent Architecture

```text
[ Ingest SCOPE.md & Map AST ] ──> [ Subprocess Lint & Test Audit ]
                                                │
                                                ▼
[ Clean Execution / Target Met ] <── [ Analyze Scope Drift & Security ]
              │                                 │
              │                                 ▼
              │                     [ Needs Remediation? ]
              │                                 │
              │                                 ▼
        ( END / Output ) <──────── [ Patch Engine (Self-Healing) ]
```

---

## 🛡️ Security & OWASP Alignment

VibeCheck incorporates a dedicated security layer (`auditor/security/`), wired directly into the ingest and remediation nodes of the LangGraph agent, addressing key OWASP Agentic Security (ASI) & LLM Top 10 vulnerabilities:

* **`prompt_injection_guard.py` (ASI01 / LLM01):** `SCOPE.md` is screened for indirect prompt-injection directives before ingestion, and any match is redacted and logged.
* **`system_prompt_protector.py` (LLM07):** Wraps context in strict boundaries and blocks prompt leakage attempts.
* **`output_sanitizer.py` (ASI03 / ASI05):** Every remediation target path is checked with `is_safe_path` before writing, and every LLM-generated patch is validated with `validate_python_patch` (AST syntax check) before it's ever written to disk.
* **`scope_budget_guard.py` (ASI02 / LLM06):** A `ScopeAuditBudget` instance is created per audit run and enforces both the max files patched and the max self-healing graph iterations — replacing what used to be a hardcoded loop limit.
* **`audit_logger.py`:** Every blocked path traversal, rejected patch, budget breach, and applied fix is written as a structured JSON event to `scope_auditor_security.log` for auditability.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the project in editable mode:

```bash
git clone https://github.com/abhishekk9896/VibeCheck.git
cd VibeCheck
pip install -e .
```

### 2. Environment Setup (Optional)

VibeCheck supports OpenAI models for LLM remediation, but gracefully falls back to deterministic local rule patching if no key is present:

```bash
# Optional: Set OpenAI key for full LLM self-healing capability
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Running an Audit

Audit the current workspace against `SCOPE.md`:

```bash
scope-auditor audit --root .
```

Export detailed Markdown and HTML executive reports:

```bash
scope-auditor audit --root . --export
```

---

## 📋 CLI Usage Summary

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--root` | `-r` | `.` | Target project root directory to audit |
| `--scope` | `-s` | `SCOPE.md` | Path to the specification file |
| `--export` | `-e` | `False` | Generate `audit_report.md` and `audit_report.html` |

---

## 📂 Project Structure

```text
VibeCheck/
├── auditor/
│   ├── cli/             # Typer CLI entrypoints & Rich console interface
│   ├── core/            # LangGraph state graph, AST mappers, & patch engine
│   ├── runners/         # Subprocess runners for Ruff and Pytest
│   └── security/        # OWASP ASI & LLM Top 10 security guards
├── sample_app/          # Target module for validation tests
├── tests/               # Test suites executed by the agent
├── pyproject.toml       # Package definition & CLI scripts
└── SCOPE.md             # Project scope specification
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.