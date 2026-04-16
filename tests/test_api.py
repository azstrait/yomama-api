# tests/test_api.py
import os
import shutil
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, joke_store
from app.config import get_settings
from app.version import __version__


@contextmanager
def override_env(**env_vars):
    """
    Temporarily set environment variables for the duration of a context,
    and clear get_settings cache so new env values are used.
    """
    old_env = {}
    try:
        for k, v in env_vars.items():
            old_env[k] = os.environ.get(k)
            os.environ[k] = str(v)
        get_settings.cache_clear()
        yield
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        get_settings.cache_clear()


def reload_jokes_for_tests():
    """
    Explicitly reload jokes after changing DATA_DIR in tests.
    """
    joke_store.load_from_file()


@contextmanager
def use_test_jokes_file():
    """
    Ensure DATA_DIR points to tests/data and that there is a jokes.csv there
    (as a symlink or copy of test_jokes.csv). Reloads jokes for the block.
    """
    tests_dir = Path(__file__).resolve().parent
    test_data_dir = tests_dir / "data"
    test_jokes = test_data_dir / "test_jokes.csv"
    temp_jokes = test_data_dir / "jokes.csv"

    if not test_jokes.is_file():
        raise RuntimeError(f"Expected test jokes file at {test_jokes}")

    created_temp = False

    try:
        # If jokes.csv doesn't exist, create it (symlink if possible, else copy)
        if not temp_jokes.exists():
            try:
                temp_jokes.symlink_to(test_jokes)
            except OSError:
                shutil.copyfile(test_jokes, temp_jokes)
            created_temp = True

        with override_env(DATA_DIR=str(test_data_dir)):
            reload_jokes_for_tests()
            yield
    finally:
        # Clean up the temporary jokes.csv if we created it
        if created_temp and temp_jokes.exists():
            try:
                if temp_jokes.is_symlink():
                    temp_jokes.unlink()
                else:
                    temp_jokes.unlink()
            except OSError:
                pass


def test_get_categories_and_category_count_with_test_data():
    """
    Use tests/data/test_jokes.csv (via jokes.csv symlink/copy) as the data source and
    assert that categories and category_count match its content.
    """
    tests_dir = Path(__file__).resolve().parent
    test_data_dir = tests_dir / "data"
    test_jokes = test_data_dir / "test_jokes.csv"

    # Compute expected category set from the CSV itself
    import csv

    expected_categories = set()
    with test_jokes.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = str(row["category"]).strip()
            if cat:
                expected_categories.add(cat)

    with use_test_jokes_file():
        client = TestClient(app)

        resp = client.get("/api/categories")
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "success"
        assert "categories" in data
        assert "category_count" in data
        categories = data["categories"]
        category_count = data["category_count"]

        assert isinstance(categories, list)
        assert isinstance(category_count, int)
        assert len(categories) == category_count

        assert set(categories) == expected_categories
        assert category_count == len(expected_categories)


def test_get_random_joke_success():
    # Use whatever main DATA_DIR is configured with (production/data)
    client = TestClient(app)
    response = client.get("/api/random")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data
    assert "joke" in data
    assert "category" in data
    assert isinstance(data["id"], int)
    assert isinstance(data["joke"], str)
    assert isinstance(data["category"], str)


def test_get_random_joke_by_valid_category():
    client = TestClient(app)
    categories_resp = client.get("/api/categories")
    assert categories_resp.status_code == 200
    categories_data = categories_resp.json()
    assert categories_data["status"] == "success"
    categories = categories_data["categories"]
    assert len(categories) > 0

    valid_category = categories[0]

    response = client.get(f"/api/random/{valid_category}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["category"] == valid_category
    assert isinstance(data["joke"], str)
    assert isinstance(data["id"], int)


def test_get_random_joke_by_invalid_category():
    client = TestClient(app)
    response = client.get("/api/random/__nonexistent_category__")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert "Category not found" in data["message"]


def test_health_endpoint_includes_category_count():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert data["app_name"] == "Yo Mama Jokes API"
    assert data["version"] == __version__
    assert isinstance(data["jokes_loaded"], bool)
    assert isinstance(data["joke_count"], int)
    assert isinstance(data["category_count"], int)


def test_root_serves_html():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_data_jokes_404_when_download_disabled():
    client = TestClient(app)
    response = client.get("/data/jokes")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    # Could be "Not found" or "No jokes file found on server"
    assert (
        "not" in data["message"].lower() or "no jokes file" in data["message"].lower()
    )


def test_data_jokes_accessible_when_enabled_and_test_data():
    with use_test_jokes_file(), override_env(DOWNLOADABLE_JOKES="true"):
        client = TestClient(app)
        response = client.get("/data/jokes")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/")
        # Ensure it contains at least the header line
        assert (
            "id" in response.text
            and "joke" in response.text
            and "category" in response.text
        )
