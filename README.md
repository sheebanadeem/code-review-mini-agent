<h1>Code Review Mini-Agent</h1>

This project implements a lightweight Code Review Agent built with FastAPI.  
It analyzes Python source code, extracts functions, detects issues (TODOs, prints), and stores structured review results in a SQLite database.  
An additional experimental graph execution engine allows chaining multiple analysis tools together.

<h2>Features</h2>

- Submit raw Python code and receive an automated review.
- Upload `.py` files using multipart form.
- Extract function metadata.
- Detect TODO comments and print statements.
- Compute complexity metrics.
- Persist reviews in SQLite.
- Background execution engine for multi-step graph workflows.
- Auto-open documentation UI when the server starts.
- Clean API structure with Pydantic v2 and SQLAlchemy 2.0.

---

<h2>Project Structure</h2>

app/
│
├── agent.py # Code review logic using radon and custom rules
├── main.py # FastAPI initialization and routing
├── models.py # SQLAlchemy ORM models
├── schemas.py # Pydantic schemas (v2)
├── db.py # Database session and initialization
├── graphs.py # Graph execution engine endpoints
├── engine.py # Simple execution engine for graph nodes
├── utils.py # Helper utilities for parsing code
│
images/ # Screenshots for documentation
README.md
requirements.txt
.gitignore

yaml


---

<h2>Installation</h2>

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
.\.venv\Scripts\activate
```
</div>
<h3>3. Install dependencies</h3>
<div>
```bash
pip install -r requirements.txt
```
</div>
---

<h2>Running the Application</h2>

<h3>Start the FastAPI server</h3>
<div>
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
</div>
The server will start and automatically open:

http://127.0.0.1:8000/docs

Here you can test all endpoints interactively.

---

<h2>API Usage</h2>

<h3>1. Submit Code for Review</h3>

Endpoint: POST /review

Example request body:

{
"source": "def add(a, b):\n return a + b\n# TODO: improve validation"
}

yaml
Copy code

Expected output fields:
- id
- source_hash
- summary
- findings
- suggestions
- created_at

---

<h3>2. Upload a Python File</h3>

Endpoint: POST /review/file  
Use multipart form with key: file

---

<h3>3. Retrieve a Review</h3>

GET /review/{id}

---

<h2>Graph Execution Engine (Optional Feature)</h2>

You can define a workflow (graph) consisting of multiple tools:

- code_review  
- extract_functions  
- find_todos  

<h3>Create Example Graph</h3>

Graph structure:

{
"graph": {
"start_node": "n1",
"nodes": [
{ "id": "n1", "tool": "code_review", "inputs": { "source": "{{source}}" }, "next": ["n2"] },
{ "id": "n2", "tool": "extract_functions", "inputs": { "source": "{{source}}" }, "next": ["n3"] },
{ "id": "n3", "tool": "find_todos", "inputs": { "source": "{{source}}" }, "next": [] }
]
}
}

css
Copy code

<h3>Run Graph</h3>

Send:

{
"graph_id": <id>,
"initial_state": {
"source": "def greet(name):\n print('Hello', name)\n# TODO: add tests\n"
}
}

php-template
Copy code

<h3>Check Graph State</h3>

GET /graph/state/{run_id}

The state will update until status becomes `done`.

---

<h2>Screenshots</h2>

Below are example screenshots from the API documentation.

```html
<img src="images/Screenshot 2025-12-11 062529.png" width="700">
<img src="images/Screenshot 2025-12-11 062548.png" width="700">
<img src="images/Screenshot 2025-12-11 064508.png" width="700">
<img src="images/Screenshot 2025-12-11 064533.png" width="700">
<img src="images/Screenshot 2025-12-11 065550.png" width="700">
<img src="images/Screenshot 2025-12-11 065710.png" width="700">
<img src="images/Screenshot 2025-12-11 065722.png" width="700">
<h2>Database</h2>
A SQLite file (reviews.db) is created automatically on first run.
It is ignored using .gitignore and should not be committed to Git.

<h2>Testing</h2>
pytest

<h2>License</h2>
This project is provided for educational and assessment purposes.

yaml
Copy code

---

If you want:

- a shorter version  
- a version with a TOC  
- or a version that removes the graph engine section entirely  

I can generate those too.





