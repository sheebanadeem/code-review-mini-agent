# app/graphs.py
import json
import threading
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import SessionLocal
from app.models import Graph, Run
from app.engine import SimpleEngine
from app.agent import CodeReviewAgent
from app.utils import extract_functions, find_todos_and_prints, compute_source_hash
from app.schemas import GraphCreate, GraphOut, GraphRunRequest, RunStateOut

router = APIRouter(prefix="/graph", tags=["graph"])

# Tool registry: wrap existing functions to accept/return state dicts
agent = CodeReviewAgent()

def _tool_code_review(state: dict):
    # expects state["source"]
    source = state.get("source", "")
    return {"review": agent.review_code(source)}

def _tool_extract(state: dict):
    source = state.get("source", "")
    funcs = extract_functions(source)
    # convert to list of dicts
    return {"functions": [f.to_dict() for f in funcs]}

def _tool_find_todos(state: dict):
    source = state.get("source", "")
    todos = find_todos_and_prints(source)
    return {"todos": todos}

# register tools
TOOLS = {
    "code_review": _tool_code_review,
    "extract_functions": _tool_extract,
    "find_todos": _tool_find_todos,
}

engine = SimpleEngine(TOOLS)

# helper DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=GraphOut)
def create_graph(payload: GraphCreate, db: Session = Depends(get_db)):
    graph_json = json.dumps(payload.graph)
    g = Graph(definition=graph_json, created_at=datetime.utcnow())
    db.add(g)
    db.commit()
    db.refresh(g)
    return GraphOut(graph_id=g.id, graph=payload.graph, created_at=g.created_at)

def _run_and_persist(run_id: int):
    # runs in background thread: load run and graph, execute, persist updates
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            return
        # load graph
        graph = db.get(Graph, run.graph_id)
        if not graph:
            run.status = "failed"
            run.updated_at = datetime.utcnow()
            db.commit()
            return

        graph_def = json.loads(graph.definition)
        initial_state = json.loads(run.state or "{}")

        def logger(msg):
            # append to run.log (list)
            logs = json.loads(run.log or "[]")
            logs.append({"ts": datetime.utcnow().isoformat(), "msg": msg})
            run.log = json.dumps(logs)
            run.updated_at = datetime.utcnow()
            db.commit()

        run.status = "running"
        run.updated_at = datetime.utcnow()
        db.commit()

        # Execute
        result = engine.run_graph(graph_def, initial_state, run_logger=logger)

        # persist final
        run.state = json.dumps(result.get("state", {}))
        run.log = json.dumps(result.get("logs", []))
        run.iterations = result.get("iterations", 0)
        run.status = "done"
        run.updated_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        try:
            run.status = "failed"
            run.log = json.dumps([{"error": str(e)}])
            run.updated_at = datetime.utcnow()
            db.commit()
        except Exception:
            pass
    finally:
        db.close()

@router.post("/run")
def run_graph(payload: GraphRunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # verify graph exists
    graph = db.get(Graph, payload.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    run = Run(
        graph_id=payload.graph_id,
        state=json.dumps(payload.initial_state or {}),
        status="created",
        log=json.dumps([]),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # background execution using FastAPI BackgroundTasks
    # but to ensure long running runs continue, start a thread
    background_tasks.add_task(_run_and_persist, run.id)

    return {"run_id": run.id, "status": run.status}

@router.get("/state/{run_id}", response_model=RunStateOut)
def get_run_state(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    state = json.loads(run.state or "{}")
    log = json.loads(run.log or "[]")
    return RunStateOut(
        run_id=run.id,
        graph_id=run.graph_id,
        status=run.status,
        state=state,
        log=log,
        iterations=run.iterations,
        created_at=run.created_at,
        updated_at=run.updated_at
    )
