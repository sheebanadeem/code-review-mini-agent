# app/engine.py
from typing import Dict, Any, Callable, List, Optional
import time

class SimpleEngine:
    """
    Minimal synchronous graph engine.
    Graph format (example):
    {
      "nodes": {
        "extract": {"fn": "extract_functions"},
        "analyze": {"fn": "code_review"},
        "end": {"fn": null}
      },
      "edges": {
         "extract": "analyze",
         "analyze": "end"
      },
      "branches": {
         "analyze": [
             {"cond": "state.get('findings') and len(state.get('findings', []))>0", "next":"end"},
             {"cond": "else", "next":"end"}
         ]
      },
      "start": "extract",
      "max_iterations": 50
    }
    """

    def __init__(self, tools: Dict[str, Callable], max_iterations: int = 50):
        self.tools = tools
        self.default_max_iterations = max_iterations

    def run_graph(
        self,
        graph: Dict[str, Any],
        initial_state: Dict[str, Any],
        run_logger: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        state = dict(initial_state or {})
        logs: List[Dict[str, Any]] = []
        node_name = graph.get("start")
        edges = graph.get("edges", {})
        branches = graph.get("branches", {})
        nodes = graph.get("nodes", {})
        max_iter = graph.get("max_iterations", self.default_max_iterations)

        iterations = 0
        while node_name and iterations < max_iter:
            iterations += 1

            node_def = nodes.get(node_name)
            if node_def is None:
                logs.append({"node": node_name, "error": "node not found"})
                break

            fn_name = node_def.get("fn")
            # log start
            msg = f"node:{node_name} fn:{fn_name}"
            logs.append({"event": "start", "node": node_name, "fn": fn_name, "iteration": iterations})
            if run_logger:
                try:
                    run_logger(msg)
                except Exception:
                    pass

            result = None
            try:
                if fn_name:
                    tool = self.tools.get(fn_name)
                    if not tool:
                        raise RuntimeError(f"tool '{fn_name}' not found")
                    # tool can accept state dict and may return dict updates
                    res = tool(state)
                    # normalize result -> must be dict or None
                    if isinstance(res, dict):
                        state.update(res)
                        result = res
                else:
                    # fn_name is None → noop
                    result = None
                logs.append({"event": "end", "node": node_name, "result": result})
            except Exception as e:
                logs.append({"event": "error", "node": node_name, "error": str(e)})
                # stop on error
                break

            # Branch handling (branches[node_name] is a list of dicts with cond/next)
            taken_next = None
            if node_name in branches:
                for br in branches[node_name]:
                    cond = br.get("cond")
                    nxt = br.get("next")
                    if cond == "else":
                        taken_next = nxt
                        break
                    try:
                        # limited eval environment: only "state"
                        if eval(cond, {}, {"state": state}):
                            taken_next = nxt
                            break
                    except Exception:
                        # if condition fails to eval, skip
                        continue

            if taken_next is None:
                taken_next = edges.get(node_name)

            # stop if next is None or 'end'
            if not taken_next or taken_next == "end":
                break

            node_name = taken_next

        return {"state": state, "logs": logs, "iterations": iterations}
