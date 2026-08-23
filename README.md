Set-Content -Path "README.md" -Value @'
# 🛡️ VibeCheck (`scope-auditor`)

> **LangGraph-powered Scope & Quality Auditor Agent for Vibe-Coded Python Projects.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Linter](https://img.shields.io/badge/linter-Ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Testing](https://img.shields.io/badge/testing-Pytest-yellow.svg)](https://docs.pytest.org/)

**VibeCheck** is an autonomous developer agent built on **LangGraph**. It bridges the gap between rapid LLM prototyping ("vibe-coding") and production quality standards by auditing codebase feature alignment against `SCOPE.md`, enforcing linting rules via `ruff`, running test suites via `pytest`, and executing a self-healing remediation loop to fix breaking changes automatically.

---

## 🌟 Key Features

* **📜 Deterministic Scope Parser:** Converts human-readable `SCOPE.md` specifications into target verification constraints.
* **🔍 AST Symbol Indexer:** Statically analyzes codebase classes, functions, and import paths without code execution.
* **⚡ Subprocess Tool Runners:** Aggregates structured outputs from `ruff` for code quality and `pytest` for test suites.
* **🔁 Autonomous Self-Healing Loop:** Automatically fixes breaking tests and lint errors using OpenAI or offline rule-based patch generation, looping until tests pass.
* **📊 Rich CLI & Executive Reports:** Terminal interface powered by `rich`, with one-click export to `audit_report.md` and `audit_report.html`.

---

## 🏗️ Agent Architecture

[ Ingest SCOPE.md & Map AST ] ──> [ Subprocess Lint & Test Audit ]│▼[ Clean Execution / Target Met ] <── [ Analyze Scope Drift ]│                                 ││                                 ▼│                     [ Needs Remediation? ]│                                 ││                                 ▼( END / Output ) <──────── [ Patch Engine (Self-Healing) ]
---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the project in editable mode:

```bash
git clone [https://github.com/abhishekk9896/VibeCheck.git](https://github.com/abhishekk9896/VibeCheck.git)
cd VibeCheck
pip install -e .
2. Environment Setup (Optional)VibeCheck supports OpenAI models for LLM remediation, but gracefully falls back to deterministic local rule patching if no key is present:Bash# Optional: Set OpenAI key for full LLM self-healing capability
export OPENAI_API_KEY="your-openai-api-key"
3. Running an AuditAudit the current workspace against SCOPE.md:Bashscope-auditor audit --root .
Export detailed Markdown and HTML executive reports:Bashscope-auditor audit --root . --export
📋 CLI Usage SummaryFlagShortDefaultDescription--root-r.Target project root directory to audit--scope-sSCOPE.mdPath to the spec file--export-eFalseGenerate audit_report.md and audit_report.html📂 Project StructureVibeCheck/
├── auditor/
│   ├── cli/             # Typer CLI entrypoints & Rich console interface
│   ├── core/            # LangGraph state graph, AST mappers, & patch engine
│   └── runners/         # Subprocess runners for Ruff and Pytest
├── sample_app/          # Target module for validation tests
├── tests/               # Test suites executed by the agent
├── pyproject.toml       # Package definition & CLI scripts
└── SCOPE.md             # Project scope specification
📄 LicenseDistributed under the MIT License. See LICENSE for more information.'@ -Encoding UTF8