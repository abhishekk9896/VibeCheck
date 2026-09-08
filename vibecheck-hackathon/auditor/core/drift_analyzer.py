import re
from pydantic import BaseModel, Field
from auditor.core.scope_parser import Requirement
from auditor.core.codebase_mapper import FileASTMap


class ScopeDriftReport(BaseModel):
    matched_requirements: list[str] = Field(default_factory=list)
    missing_requirements: list[Requirement] = Field(default_factory=list)
    unmapped_symbols: list[str] = Field(default_factory=list)


class DriftAnalyzer:
    def __init__(self, requirements: list[Requirement], ast_maps: list[FileASTMap]):
        self.requirements = requirements
        self.ast_maps = ast_maps

    def analyze(self) -> ScopeDriftReport:
        """Compares codebase AST symbols against requirement titles and criteria."""
        report = ScopeDriftReport()

        # Collect all public function and class names in the codebase
        all_symbols: set[str] = set()
        for file_map in self.ast_maps:
            # Skip checking internal CLI/Auditor code itself if running on self
            if "auditor" in file_map.file_path.parts:
                continue

            for func in file_map.functions:
                if not func.name.startswith("_"):
                    all_symbols.add(func.name.lower())
            for cls in file_map.classes:
                if not cls.name.startswith("_"):
                    all_symbols.add(cls.name.lower())
                    for method in cls.methods:
                        if not method.name.startswith("_"):
                            all_symbols.add(method.name.lower())

        # Match requirements against discovered symbols using keyword overlap
        mapped_symbols: set[str] = set()

        for req in self.requirements:
            # Extract key terms from title and criteria
            req_keywords = self._extract_keywords(f"{req.title} {' '.join(req.criteria)}")
            
            matched = False
            for sym in all_symbols:
                if any(kw in sym for kw in req_keywords):
                    matched = True
                    mapped_symbols.add(sym)

            if matched:
                report.matched_requirements.append(req.id)
            else:
                report.missing_requirements.append(req)

        # Identify unmapped symbols (potential scope drift)
        for sym in all_symbols:
            if sym not in mapped_symbols:
                report.unmapped_symbols.append(sym)

        return report

    def _extract_keywords(self, text: str) -> set[str]:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        stopwords = {"implement", "with", "and", "the", "for", "function", "logic", "utility"}
        return {w for w in words if w not in stopwords}