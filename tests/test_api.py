"""HTTP contract tests for the task API."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import get_db
from app.database_models import Base

API_KEY = "test-api-key-that-is-at-least-32-characters"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Provide an API client connected to an isolated in-memory database."""
    monkeypatch.setenv("API_KEY", API_KEY)
    monkeypatch.setattr(main, "verify_database_schema", lambda: None)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_task_endpoints_require_api_key(client: TestClient) -> None:
    """Requests without a valid key cannot read or mutate tasks."""
    assert client.get("/tasks").status_code == 401
    assert client.get("/tasks", headers={"X-API-Key": "wrong"}).status_code == 401
    assert (
        client.post("/tasks", json={"title": "Unauthorized"}).status_code == 401
    )


def test_create_read_update_and_delete_task(client: TestClient) -> None:
    """The task CRUD endpoints return the documented success statuses."""
    headers = {"X-API-Key": API_KEY}
    created = client.post(
        "/tasks",
        headers=headers,
        json={"title": "  Test API task  "},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Test API task"
    assert task["id"]
    assert task["created_at"].endswith(("Z", "+00:00"))

    fetched = client.get(f"/tasks/{task['id']}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Test API task"

    updated = client.put(
        f"/tasks/{task['id']}",
        headers=headers,
        json={"title": "Updated API task", "status": True},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] is True
    assert updated.json()["created_at"] == task["created_at"]

    deleted = client.delete(f"/tasks/{task['id']}", headers=headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/tasks/{task['id']}", headers=headers).status_code == 404


def test_list_tasks_filters_and_paginates(client: TestClient) -> None:
    """Filtering is applied before the bounded page is returned."""
    headers = {"X-API-Key": API_KEY}
    for title, completed in (
        ("Pending one", False),
        ("Completed", True),
        ("Pending two", False),
    ):
        response = client.post(
            "/tasks",
            headers=headers,
            json={"title": title, "status": completed},
        )
        assert response.status_code == 201

    matching_tasks = client.get(
        "/tasks",
        headers=headers,
        params={"status": "false"},
    )
    assert matching_tasks.status_code == 200
    response = client.get(
        "/tasks",
        headers=headers,
        params={"status": "false", "limit": 1, "offset": 1},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == matching_tasks.json()[1]["title"]


def test_invalid_task_and_pagination_inputs_return_unprocessable(
    client: TestClient,
) -> None:
    """Invalid payloads and out-of-range pagination parameters are rejected."""
    headers = {"X-API-Key": API_KEY}
    assert (
        client.post("/tasks", headers=headers, json={"title": "ab"}).status_code
        == 422
    )
    assert (
        client.get("/tasks", headers=headers, params={"limit": 101}).status_code
        == 422
    )
    assert (
        client.get("/tasks", headers=headers, params={"offset": -1}).status_code
        == 422
    )


def test_create_rejects_invalid_fields_and_server_managed_metadata(
    client: TestClient,
) -> None:
    """The API rejects blank/oversized values and client-owned metadata."""
    headers = {"X-API-Key": API_KEY}
    invalid_payloads = (
        {"title": "   "},
        {"title": "Valid title", "description": "x" * 2001},
        {"title": "Valid title", "id": "5f61408d-cc22-4f51-9864-e6243df6241b"},
        {"title": "Valid title", "created_at": "2026-10-16T12:00:00Z"},
        {"title": "Valid title", "status": "false"},
    )
    for payload in invalid_payloads:
        assert client.post("/tasks", headers=headers, json=payload).status_code == 422


def test_update_rejects_server_managed_metadata(client: TestClient) -> None:
    """Clients cannot change task identity or creation time through PUT."""
    headers = {"X-API-Key": API_KEY}
    created = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Update metadata test"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        headers=headers,
        json={
            "title": "Changed title",
            "id": task_id,
            "created_at": "2020-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 422


def test_frontend_file_is_served(client: TestClient) -> None:
    """The deployed application root serves the packaged web UI."""
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="api-key-form"' in response.text


def test_startup_fails_when_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The app does not start with an unprotected task API."""
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="API_KEY"):
        with TestClient(main.app):
            pass


def test_startup_fails_when_api_key_is_too_short(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The app refuses weak keys before serving requests."""
    monkeypatch.setenv("API_KEY", "too-short")
    with pytest.raises(RuntimeError, match="API_KEY"):
        with TestClient(main.app):
            pass
