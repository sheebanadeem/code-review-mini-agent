# app/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Any
from pydantic import ConfigDict
from datetime import datetime

class ReviewCreate(BaseModel):
    source: str

class ReviewOut(BaseModel):
    id: int | None = None
    source_hash: str
    summary: str
    findings: List[Dict[str, Any]]
    suggestions: List[str]
    created_at: str | None = None

    model_config = ConfigDict(from_attributes=True)

# Graph schemas
class GraphCreate(BaseModel):
    graph: Dict[str, Any]

class GraphOut(BaseModel):
    graph_id: int
    graph: Dict[str, Any]
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class GraphRunRequest(BaseModel):
    graph_id: int
    initial_state: Dict[str, Any] | None = None

class RunStateOut(BaseModel):
    run_id: int
    graph_id: int
    status: str
    state: Dict[str, Any]
    log: List[Dict[str, Any]]
    iterations: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
