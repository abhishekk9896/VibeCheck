class ScopeAuditBudget:
    def __init__(self, max_files_to_audit: int = 20, max_graph_iterations: int = 3):
        self.max_files = max_files_to_audit
        self.max_graph_iterations = max_graph_iterations
        self.files_audited = 0
        self.iterations_run = 0

    def check_file_limit(self):
        if self.files_audited >= self.max_files:
            raise RuntimeError("Audit file limit reached: Terminating analysis to prevent excessive processing.")
        self.files_audited += 1

    def check_iteration_limit(self):
        """Prevents infinite agent self-healing loops (ASI08/LLM06 mitigation)."""
        if self.iterations_run >= self.max_graph_iterations:
            raise RuntimeError("Agent iteration limit reached: Self-healing loop terminated by circuit breaker.")
        self.iterations_run += 1