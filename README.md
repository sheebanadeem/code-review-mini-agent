<h1>Code Review Mini-Agent</h1>

A lightweight FastAPI service for automated static analysis of Python code.  
It computes cyclomatic complexity, detects TODOs and print statements, stores results in SQLite, and includes a simple workflow/graph execution engine.

---

<h2>Features</h2>

- Submit Python source code via POST /review  
- Upload .py files via POST /review/file  
- Retrieve reviews by ID  
- Cyclomatic complexity (Radon)  
- TODO and print detection  
- Optional Ruff linting  
- SQLite persistence  
- Graph/workflow engine  
- Auto documentation at /docs  

---

<h2>Tech Stack</h2>

- Python 3.11+  
- FastAPI  
- SQLAlchemy  
- Pydantic v2  
- Radon  
- Uvicorn  
- SQLite  

---

<h2>Project Structure</h2>

app/  
 ├── agent.py        (core analysis logic)  
 ├── main.py         (API entrypoint)  
 ├── models.py       (database models)  
 ├── schemas.py      (Pydantic schemas)  
 ├── db.py           (database setup)  
 ├── engine.py       (graph engine)  
 └── graphs.py       (graph endpoints)  

tests/  
 └── test_graphs.py

requirements.txt  
README.md  
.gitignore  

---

<h1>Installation</h1>

<h3>1. Clone the repository</h3>
<div>

```bash
git clone https://github.com/sheebanadeem/code-review-mini-agent.git
cd code-review-mini-agent

```
</div>
<h3>2. Create a virtual environment</h3>
<div>

```bash
python -m venv .venv
```
</div>
<h3>3. Activate the virtual environment</h3>

Windows PowerShell:  
<div>

```bash
.\.venv\Scripts\Activate.ps1
```
</div>
<h3>4. Install dependencies</h3>
<div>

```bash
python -m pip install --upgrade pip  
pip install -r requirements.txt  
```
</div>
(Optional) Install Ruff:  
<div>

```bash
pip install ruff  
```
</div>
---

<h1>Running the Application</h1>

Start the FastAPI server:
<div>

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
</div>
Open the interactive API docs in your browser:

http://127.0.0.1:8000/docs

---

<h1>API Usage</h1>

<h3>POST /review</h3>

Send a JSON body with a "source" field containing Python code.

Example JSON:

{  
  "source": "def add(a, b):\n    return a + b\n# TODO improve types"  
}

<h3>POST /review/file</h3>

Upload a .py file using form-data with the field name:  
file

<h3>GET /review/{id}</h3>

Retrieve a previously saved code review.

---

<h1>Example Review Output</h1>

{  
  "id": 1,  
  "source_hash": "9bae4f1cf83a...",  
  "summary": "Analyzed 1 functions, avg complexity 1.00, 1 TODO/print findings.",  
  "findings": [  
    { "name": "add", "lineno": 1, "end_lineno": 2, "complexity": 1, "length": 2 },  
    { "lineno": 3, "message": "# TODO improve types" }  
  ],  
  "suggestions": [  
    "Address TODO on line 3 by converting it into a tracked issue instead of inline comments."  
  ],  
  "created_at": "2025-01-01T12:00:00"  
}

---

<h1>Graph / Workflow Engine</h1>

Available endpoints:

POST /graph/create  
POST /graph/run  
GET /graph/state/{run_id}  

---

<h1>Testing</h1>

Run tests:

pytest -q

---
<h1>Outputs</h1>
<p align="center">
  <img src="images\Screenshot 2025-12-11 062529.png"" width="700">
</p>
---
<h1>Notes</h1>

- All timestamps are ISO-8601 strings.  
- UTF-8 fallback decoding for file uploads.  
- Graph engine prevents infinite loops using max_iterations.  
- Branch conditions use a restricted eval environment.  

---

<h1>Maintainer</h1>

Sheeba Nadeem  

---









