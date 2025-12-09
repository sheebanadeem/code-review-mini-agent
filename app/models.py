# app/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db import Base
from typing import Dict, Any
import json

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    source_hash = Column(String(64), nullable=False)
    summary = Column(String(1024), nullable=False)
    findings = Column(JSON, nullable=False)
    suggestions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        return cls(
            source_hash=d.get("source_hash", ""),
            summary=d.get("summary", ""),
            findings=d.get("findings", []),
            suggestions=d.get("suggestions", []),
        )

    def to_schema(self):
        return {
            "id": self.id,
            "source_hash": self.source_hash,
            "summary": self.summary,
            "findings": self.findings,
            "suggestions": self.suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Graph(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True, index=True)
    definition = Column(String, nullable=False)  # JSON text of graph
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"), nullable=False)
    state = Column(String, nullable=True)   # JSON text
    log = Column(String, nullable=True)     # JSON text (list)
    status = Column(String, nullable=False, default="created")  # created | running | done | failed
    iterations = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
