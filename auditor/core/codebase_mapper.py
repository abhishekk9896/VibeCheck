import ast
from pathlib import Path
from pydantic import BaseModel, Field


class FunctionSymbol(BaseModel):
    name: str
    line_no: int
    args: list[str]
    docstring: str | None = None


class ClassSymbol(BaseModel):
    name: str
    line_no: int
    methods: list[FunctionSymbol] = Field(default_factory=list)


class FileASTMap(BaseModel):
    file_path: Path
    classes: list[ClassSymbol] = Field(default_factory=list)
    functions: list[FunctionSymbol] = Field(default_factory=list)


class CodebaseMapper:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def scan(self, ignore_dirs: set[str] | None = None) -> list[FileASTMap]:
        """Scans directory for .py files and extracts AST function/class signatures."""
        ignore = ignore_dirs or {".venv", "venv", "__pycache__", ".git", ".pytest_cache", "build", "dist"}
        maps = []

        for path in self.root_dir.rglob("*.py"):
            if any(part in ignore for part in path.parts):
                continue

            ast_map = self._parse_file(path)
            if ast_map:
                maps.append(ast_map)

        return maps

    def _parse_file(self, file_path: Path) -> FileASTMap | None:
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError:
            return None

        file_map = FileASTMap(file_path=file_path.relative_to(self.root_dir))

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                file_map.functions.append(self._extract_function(node))
            elif isinstance(node, ast.ClassDef):
                class_sym = ClassSymbol(
                    name=node.name,
                    line_no=node.lineno,
                    methods=[
                        self._extract_function(n)
                        for n in node.body
                        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
                    ],
                )
                file_map.classes.append(class_sym)

        return file_map

    def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionSymbol:
        args = [a.arg for a in node.args.args]
        docstring = ast.get_docstring(node)
        return FunctionSymbol(name=node.name, line_no=node.lineno, args=args, docstring=docstring)