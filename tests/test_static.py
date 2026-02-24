from fastapi.testclient import TestClient

from src import app as fastapi_app_module

client = TestClient(fastapi_app_module.app)


def test_root_redirects_to_static():
    # requesting the root path should return the contents of index.html
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mergington High School" in resp.text


def test_static_file_served():
    # the index page is also directly accessible under /static
    resp = client.get("/static/index.html")
    assert resp.status_code == 200
    assert "Extracurricular Activities" in resp.text
