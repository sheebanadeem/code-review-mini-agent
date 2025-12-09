import ast
from typing import List, Tuple, Dict
from radon.complexity import cc_visit, cc_rank

class FunctionInfo:
    def __init__(self, name: str, lineno: int, end_lineno: int | None, complexity: int, length: int, rank: str | None = None):
        self.name = name
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.complexity = complexity
        self.length = length
        self.rank = rank

    def to_dict(self):
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "complexity": self.complexity,
            "length": self.length,
            "rank": self.rank,
        }


def extract_functions(source: str) -> List[FunctionInfo]:
    """Parse Python source and return function metadata (including radon complexity)."""
    tree = ast.parse(source)
    functions: List[FunctionInfo] = []

    # use ast to get positions and length
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            lineno = getattr(node, "lineno", 0)
            end_lineno = getattr(node, "end_lineno", None)
            length = (end_lineno - lineno + 1) if end_lineno else 0
            # placeholder complexity; we'll override with radon below if possible
            functions.append(FunctionInfo(name, lineno, end_lineno, complexity=1, length=length))

    # Use radon to compute complexity info for the whole source
    try:
        blocks = cc_visit(source)
        # blocks are Radon objects with .name and .complexity
        for b in blocks:
            # Radon names usually include the full path or module: try to match by name only
            short_name = b.name.split('.')[-1]
            for f in functions:
                if f.name == short_name:
                    f.complexity = b.complexity
                    f.rank = cc_rank(b.complexity)
    except Exception:
        # radon failed (unlikely if installed), fallback: keep basic complexity
        pass

    return functions


def find_todos_and_prints(source: str) -> List[Tuple[int, str]]:
    """Return list of (lineno, message) for TODO/FIXME and print statements."""
    results: List[Tuple[int, str]] = []
    tree = ast.parse(source)

    for node in ast.walk(tree):
        # detect print calls
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "print":
                results.append((getattr(node, "lineno", 0), "print statement"))

    # fallback: scan lines for TODO/FIXME
    for i, line in enumerate(source.splitlines(), start=1):
        if "TODO" in line or "FIXME" in line:
            results.append((i, line.strip()))

    return results


def compute_source_hash(source: str) -> str:
    import hashlib
    return hashlib.sha256(source.encode("utf-8")).hexdigest()
