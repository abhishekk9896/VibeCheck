import re
from pathlib import Path
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str = Field(description="Unique identifier for requirement, e.g., REQ-01")
    title: str = Field(description="High level title of feature or requirement")
    description: str = Field(default="", description="Detailed summary body text")
    criteria: list[str] = Field(default_factory=list, description="Extracted bullet points")


class ScopeParser:
    def __init__(self, scope_path: str | Path):
        self.scope_path = Path(scope_path)

    def parse(self) -> list[Requirement]:
        """Parses SCOPE.md / PRD.md into structured Requirement objects."""
        if not self.scope_path.exists():
            raise FileNotFoundError(f"Scope file not found at {self.scope_path.resolve()}")

        content = self.scope_path.read_text(encoding="utf-8")
        requirements: list[Requirement] = []

        # Matches Markdown headings formatted like: ## [REQ-01] Title
        req_blocks = re.split(r"(?m)^##\s+\[(.*?)\]\s+(.*)$", content)

        if len(req_blocks) < 3:
            return self._parse_generic_bullets(content)

        for i in range(1, len(req_blocks), 3):
            req_id = req_blocks[i].strip()
            title = req_blocks[i + 1].strip()
            body = req_blocks[i + 2]

            criteria = [
                line.lstrip("- *").strip()
                for line in body.splitlines()
                if line.strip().startswith(("-", "*"))
            ]

            requirements.append(
                Requirement(
                    id=req_id,
                    title=title,
                    description=body.strip(),
                    criteria=criteria,
                )
            )

        return requirements

    def _parse_generic_bullets(self, content: str) -> list[Requirement]:
        """Fallback parser for unstructured bullet list specs."""
        requirements = []
        for idx, line in enumerate(content.splitlines()):
            line = line.strip()
            if line.startswith(("-", "*")) and len(line) > 3:
                clean_text = line.lstrip("- *").strip()
                title = clean_text.split(":")[0] if ":" in clean_text else clean_text
                requirements.append(
                    Requirement(
                        id=f"FEAT-{idx + 1:02d}",
                        title=title,
                        description=clean_text,
                        criteria=[clean_text],
                    )
                )
        return requirements