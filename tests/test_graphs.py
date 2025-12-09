# tests/test_graphs.py
import time
import json
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path

client = TestClient(app)

def test_create_and_run_graph():
    # sample graph: extract functions then run full code_review
    sample_graph = {
        "nodes": {
            "extract": {"fn": "extract_functions"},
            "review": {"fn": "code_review"},
            "end": {"fn": None}
        },
        "edges": {"extract": "review", "review": "end"},
        "start": "extract",
        "max_iterations": 10
    }

    # create
    res = client.post("/graph/create", json={"graph": sample_graph})
    assert res.status_code == 200
    data = res.json()
    graph_id = data["graph_id"]

    # run with initial state containing sample code
    body = {
        "graph_id": graph_id,
        "initial_state": {"source": "def add(a,b):\\n    return a+b\\n# TODO: types"}
    }
    run_res = client.post("/graph/run", json=body)
    assert run_res.status_code == 200
    run_id = run_res.json()["run_id"]

    # poll for completion (small loop)
    for _ in range(20):
        r = client.get(f"/graph/state/{run_id}")
        assert r.status_code == 200
        st = r.json()
        if st["status"] == "done":
            assert "state" in st
            assert "log" in st
            return
        time.sleep(0.2)

    # final assert: should be done
    final = client.get(f"/graph/state/{run_id}").json()
    assert final["status"] == "done"
