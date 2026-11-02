import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    app.config.update(TESTING=True, DATABASE=str(tmp_path / "test.db"))
    with app.test_client() as client:
        yield client


def test_index_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No books found" in resp.data


def test_add_issue_return_delete(client):
    client.post("/add", data={"title": "Dune", "author": "Frank Herbert"}, follow_redirects=True)
    resp = client.get("/")
    assert b"Dune" in resp.data and b"Available" in resp.data

    client.post("/issue/1", data={"borrower": "Alice"})
    assert b"Issued to Alice" in client.get("/").data

    client.post("/return/1")
    assert b"Available" in client.get("/").data

    client.post("/delete/1")
    assert b"No books found" in client.get("/").data


def test_add_requires_fields(client):
    resp = client.post("/add", data={"title": "", "author": ""})
    assert resp.status_code == 400


def test_search(client):
    client.post("/add", data={"title": "Dune", "author": "Frank Herbert"}, follow_redirects=True)
    client.post("/add", data={"title": "Emma", "author": "Jane Austen"}, follow_redirects=True)
    resp = client.get("/?q=austen")
    assert b"Emma" in resp.data and b"Dune" not in resp.data
