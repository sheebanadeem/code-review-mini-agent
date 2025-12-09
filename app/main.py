import os
import hashlib
import json
import threading
import webbrowser
import logging
from datetime import datetime
from typing import Generator

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session

# project modules (existing in your repo)
from app.schemas import ReviewCreate, ReviewOut
from app.agent import CodeReviewAgent
from app.db import SessionLocal, init_db
from app.models import Review as ReviewModel

# Ensure DB tables exist
init_db()

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Review Mini-Agent",
    version="1.1",
    description="Code review service (radon + ruff optional)."
)

# include graph router if present (safe to import; graphs.py should NOT import app.main)
try:
    from app.graphs import router as graphs_router  # type: ignore
    app.include_router(graphs_router)
except Exception as e:
    logger.info("Graphs router not included: %s", e)


agent = CodeReviewAgent()


# --- Auto-open browser on startup (opens the docs) ---
def _open_docs():
    try:
        webbrowser.open_new("http://127.0.0.1:8000/docs")
    except Exception as e:
        logger.debug("Could not open browser automatically: %s", e)


@app.on_event("startup")
def _startup_event():
    """
    Auto-open docs after startup, controlled by OPEN_BROWSER env var.
    Set OPEN_BROWSER=0 to disable (recommended in CI or when using --reload).
    """
    if os.getenv("OPEN_BROWSER", "1") == "1":
        # slight delay to let server finish booting
        threading.Timer(1.0, _open_docs).start()


# --- Dependency for DB session ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Helper to convert datetime to iso string safely ---
def _iso(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)


# --- POST /review (JSON body) ---
@app.post("/review", response_model=ReviewOut)
def submit_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    """Submit raw Python source for review and return the persisted review result."""
    source = payload.source
    if not source or not source.strip():
        raise HTTPException(status_code=400, detail="Empty source provided")

    try:
        review_data = agent.review_code(source)
    except Exception as exc:
        logger.exception("Code review failed for POST /review")
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(exc)}")

    # persist
    try:
        db_review = ReviewModel.from_dict(review_data)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
    except Exception as exc:
        logger.exception("Failed to persist review to DB")
        raise HTTPException(status_code=500, detail=f"Persistence error: {str(exc)}")

    # return as schema, ensure created_at is a string
    return ReviewOut(
        id=db_review.id,
        source_hash=db_review.source_hash,
        summary=db_review.summary,
        findings=db_review.findings,
        suggestions=db_review.suggestions,
        created_at=_iso(db_review.created_at),
    )


# --- POST /review/file (upload a .py file) ---
@app.post("/review/file", response_model=ReviewOut)
async def submit_review_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a .py file for code review. Use key 'file' in multipart form."""
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted")
    content_bytes = await file.read()
    # Decode more leniently to avoid hard errors from odd encodings
    source = content_bytes.decode("utf-8", errors="replace")

    try:
        review_data = agent.review_code(source)
    except Exception as exc:
        logger.exception("Code review failed for uploaded file")
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(exc)}")

    # persist
    try:
        db_review = ReviewModel.from_dict(review_data)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
    except Exception as exc:
        logger.exception("Failed to persist uploaded-file review to DB")
        raise HTTPException(status_code=500, detail=f"Persistence error: {str(exc)}")

    return ReviewOut(
        id=db_review.id,
        source_hash=db_review.source_hash,
        summary=db_review.summary,
        findings=db_review.findings,
        suggestions=db_review.suggestions,
        created_at=_iso(db_review.created_at),
    )


# --- GET /review/{review_id} ---
@app.get("/review/{review_id}", response_model=ReviewOut)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """Retrieve a previously stored review by ID."""
    r = db.get(ReviewModel, review_id)
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")

    return ReviewOut(
        id=r.id,
        source_hash=r.source_hash,
        summary=r.summary,
        findings=r.findings,
        suggestions=r.suggestions,
        created_at=_iso(r.created_at),
    )

