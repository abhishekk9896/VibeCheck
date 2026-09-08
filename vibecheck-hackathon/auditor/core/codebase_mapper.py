from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionMap:
    name: str
    line_no: int
    end_line: int
    args: list[str] = field(default_factory=list)
    docstring: str | None = None
    calls: list[str] = field(default_factory=list)
    returns: list[str] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    source: str = ""


@dataclass
class FileASTMap:
    file_path: str
    functions: list[FunctionMap] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)


class CodebaseMapper:
    """Builds an AST-based evidence map of a Python codebase."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def scan(self) -> list[FileASTMap]:
        results: list[FileASTMap] = []

        for path in self.root_dir.rglob("*.py"):
            if self._should_skip(path):
                continue

            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue

            file_map = FileASTMap(
                file_path=path.relative_to(self.root_dir)
            )

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    file_map.classes.append(node.name)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    file_map.functions.append(
                        self._map_function(node, source)
                    )

            results.append(file_map)

        return results

    def _map_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source: str,
    ) -> FunctionMap:
        calls: list[str] = []
        returns: list[str] = []
        constants: list[str] = []
        operators: list[str] = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                calls.append(self._call_name(child))

            elif isinstance(child, ast.Return):
                returns.append(self._source_segment(child.value, source))

            elif isinstance(child, ast.Constant):
                if isinstance(child.value, (str, int, float, bool)):
                    constants.append(repr(child.value))

            elif isinstance(child, ast.BinOp):
                operators.append(type(child.op).__name__)

            elif isinstance(child, ast.Compare):
                for op in child.ops:
                    operators.append(type(op).__name__)

            elif isinstance(child, ast.BoolOp):
                operators.append(type(child.op).__name__)

        function_source = ast.get_source_segment(source, node) or ""

        return FunctionMap(
            name=node.name,
            line_no=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            args=[
                arg.arg
                for arg in (
                    list(node.args.posonlyargs)
                    + list(node.args.args)
                    + list(node.args.kwonlyargs)
                )
            ],
            docstring=ast.get_docstring(node),
            calls=sorted(set(filter(None, calls))),
            returns=[item for item in returns if item],
            constants=sorted(set(constants)),
            operators=sorted(set(operators)),
            source=function_source,
        )

    @staticmethod
    def _call_name(node: ast.Call) -> str:
        target = node.func

        if isinstance(target, ast.Name):
            return target.id

        if isinstance(target, ast.Attribute):
            parts: list[str] = []
            current: ast.AST | None = target

            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value

            if isinstance(current, ast.Name):
                parts.append(current.id)

            return ".".join(reversed(parts))

        return ""

    @staticmethod
    def _source_segment(
        node: ast.AST | None,
        source: str,
    ) -> str:
        if node is None:
            return ""

        return ast.get_source_segment(source, node) or ""

    def _should_skip(self, path: Path) -> bool:
        parts = set(path.parts)

        return bool(
            {
                ".venv",
                "__pycache__",
                ".git",
                "node_modules",
            }
            & parts
        )
