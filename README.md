Code Review Mini-Agent

This project is a small FastAPI-based service that performs automated code review on Python source files.
It includes static analysis (cyclomatic complexity, function extraction, TODO/print detection), optional linting with Ruff, and a simple workflow engine for defining and executing multi-step review graphs.
All review results are stored in a SQLite database using SQLAlchemy.

Features
Code Review

Extracts function definitions and basic metadata using Python’s AST module.

Computes cyclomatic complexity scores using Radon.

Detects TODO comments, print statements, and other simple code smells.

Generates a summary and structured findings.

Optional linting step with Ruff when installed locally.

File Uploads

Supports uploading .py files for review through a multipart endpoint.

Persistence

Every review is stored in a SQLite database with ID, hash, summary, findings, suggestions, and timestamp.

Workflow / Graph Engine

Allows defining a small directed graph of “steps” (nodes).

Each node corresponds to a tool function (e.g., extract → review → end).

The engine runs the graph step by step and returns execution logs and the final state.

API Documentation

The service exposes an OpenAPI specification and interactive documentation at:

http://127.0.0.1:8000/docs

Project Structure
app/
 ├── main.py           # FastAPI entrypoint  
 ├── agent.py          # CodeReviewAgent logic  
 ├── utils.py          # AST helpers, radon utilities  
 ├── engine.py         # Graph runner implementation  
 ├── graphs.py         # Graph create/run/state endpoints  
 ├── models.py         # SQLAlchemy model definitions  
 ├── schemas.py        # Pydantic schemas  
 └── db.py             # Database session + initialization

tests/
 └── test_graphs.py    # Basic tests for graph engine

requirements.txt
README.md
.gitignore

Getting Started
Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt


(Optional)

pip install ruff

Running the Application

To run the FastAPI service:

# Disable auto-opening browser tabs when using --reload, if needed
$env:OPEN_BROWSER = "0"

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


Open the API docs at:

http://127.0.0.1:8000/docs

API Overview
POST /review

Submit Python source code in JSON format.

Example body:

{
  "source": "def add(a, b):\n    return a + b\n# TODO: improve types"
}

POST /review/file

Upload a .py file using multipart form-data.

Field: file

GET /review/{id}

Fetch a previously stored review by its ID.

Graph Endpoints

POST /graph/create – Define a graph.

POST /graph/run – Start execution of a graph using an initial state.

GET /graph/state/{run_id} – Poll graph execution progress.

Running Tests
pytest -q

Notes

The service automatically handles cases where Ruff is not installed.

Radon is required for complexity analysis and included in requirements.txt.

File uploads are decoded as UTF-8 with a safe fallback to avoid crashes.

All timestamps returned to the client are normalized to ISO-8601 strings.

The workflow engine limits iterations to prevent infinite loops.