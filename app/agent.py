from typing import Dict, Any, List
from app.utils import extract_functions, find_todos_and_prints, compute_source_hash
import subprocess
import json
import tempfile
import os

class CodeReviewAgent:
    """Performs a lightweight code review and returns structured results.
       Also runs ruff (if available) and collects its results.
    """

    def review_code(self, source: str) -> Dict[str, Any]:
        source_hash = compute_source_hash(source)
        functions = extract_functions(source)
        todos = find_todos_and_prints(source)

        findings: List[Dict[str, Any]] = []
        suggestions: List[str] = []

        # Add function-level findings (include radon rank if present)
        for f in functions:
            findings.append(f.to_dict())
            if f.length and f.length > 80:
                suggestions.append(
                    f"Consider splitting function '{f.name}' (length {f.length} lines) into smaller, testable functions."
                )
            if f.complexity and f.complexity > 10:
                suggestions.append(
                    f"Reduce cyclomatic complexity in '{f.name}' (complexity {f.complexity}, rank {f.rank}). Extract helpers or simplify logic."
                )

        # File-level findings for TODO/prints
        for lineno, msg in todos:
            findings.append({"lineno": lineno, "message": msg})
            suggestions.append(f"Address at line {lineno}: '{msg}'. Consider creating a tracked issue instead of leaving TODOs.")

        # Run ruff (if installed) and include lint findings
        lint_findings = self._run_ruff_on_source(source)
        if lint_findings:
            findings.append({"linter": "ruff", "issues": lint_findings})
            suggestions.append("Fix the reported linting issues (ruff) to improve code quality.")

        if not functions:
            suggestions.append("No functions detected — consider modularizing code into functions for testability and reuse.")

        summary = self._build_summary(functions, todos, lint_findings)
        return {
            "source_hash": source_hash,
            "summary": summary,
            "findings": findings,
            "suggestions": suggestions,
        }

    def _build_summary(self, functions, todos, lint_findings):
        n_funcs = len(functions)
        avg_complexity = sum((f.complexity for f in functions), 0) / n_funcs if n_funcs else 0
        n_issues = len(todos) + (len(lint_findings) if lint_findings else 0)
        return f"Analyzed {n_funcs} functions, avg complexity {avg_complexity:.2f}, {n_issues} TODO/print/lint findings."

    def _run_ruff_on_source(self, source: str) -> List[Dict[str, Any]]:
        """Run ruff programmatically by writing to a temp file and calling ruff check --format json.
           If ruff isn't available, return [].
        """
        try:
            # Ensure ruff is installed on PATH
            res = subprocess.run(["ruff", "--version"], capture_output=True, text=True)
            if res.returncode != 0:
                return []
        except FileNotFoundError:
            return []

        # write source to a tempfile and call ruff
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as tf:
            tf.write(source)
            tf.flush()
            tmp_path = tf.name

        try:
            proc = subprocess.run(["ruff", "check", tmp_path, "--format", "json"], capture_output=True, text=True)
            if proc.returncode in (0, 1):  # 0 = no issues, 1 = issues found
                try:
                    parsed = json.loads(proc.stdout)
                    # parsed is a dict keyed by filename
                    issues = []
                    for filename, items in parsed.items():
                        for it in items:
                            issues.append({
                                "code": it.get("code"),
                                "message": it.get("message"),
                                "line": it.get("location", {}).get("row"),
                                "column": it.get("location", {}).get("col"),
                            })
                    return issues
                except Exception:
                    return []
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        return []
