from app.agent import CodeReviewAgent
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

def test_review_basic_utils():
    src = Path("app/sample_code/example.py").read_text()
    agent = CodeReviewAgent()
    result = agent.review_code(src)
    assert "source_hash" in result
    assert "summary" in result
    assert isinstance(result["findings"], list)
    assert isinstance(result["suggestions"], list)

def test_api_integration_post_get(tmp_path):
    client = TestClient(app)
    body = {"source": "def add(a,b):\n    return a+b\n# TODO: types"}
    post = client.post("/review", json=body)
    assert post.status_code == 200
    data = post.json()
    assert "id" in data
    rid = data["id"]
    get = client.get(f"/review/{rid}")
    assert get.status_code == 200
    getdata = get.json()
    assert getdata["id"] == rid
