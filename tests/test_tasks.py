# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task_success(client: AsyncClient, auth_headers: dict[str, str]):
    payload = {
        "title": "Setup Docker Compose",
        "description": "Configure PostgreSQL container and health checks",
        "status": "in_progress",
        "priority": "high"
    }
    response = await client.post("/api/v1/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "in_progress"
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_create_task_unauthorized(client: AsyncClient):
    payload = {
        "title": "Unauthorized Task",
        "status": "pending",
        "priority": "medium"
    }
    response = await client.post("/api/v1/tasks/", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tasks_list(client: AsyncClient, auth_headers: dict[str, str]):
    # Create two tasks
    await client.post("/api/v1/tasks/", json={"title": "Task 1", "status": "pending"}, headers=auth_headers)
    await client.post("/api/v1/tasks/", json={"title": "Task 2", "status": "completed"}, headers=auth_headers)

    # Fetch all tasks
    response = await client.get("/api/v1/tasks/", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2

    # Fetch with status filter (utilizing composite index)
    filter_response = await client.get("/api/v1/tasks/?status=completed", headers=auth_headers)
    assert filter_response.status_code == 200
    filtered_tasks = filter_response.json()
    assert len(filtered_tasks) == 1
    assert filtered_tasks[0]["status"] == "completed"


@pytest.mark.asyncio
async def test_get_task_with_owner_join(client: AsyncClient, auth_headers: dict[str, str]):
    create_res = await client.post(
        "/api/v1/tasks/",
        json={"title": "Joined Task Demo", "description": "Demonstrating SQL Joins"},
        headers=auth_headers
    )
    task_id = create_res.json()["id"]

    # Call endpoint that executes SQL JOIN
    response = await client.get(f"/api/v1/tasks/{task_id}/with-owner", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert "owner" in data
    assert data["owner"]["email"] == "testuser@example.com"


@pytest.mark.asyncio
async def test_update_and_delete_task(client: AsyncClient, auth_headers: dict[str, str]):
    create_res = await client.post(
        "/api/v1/tasks/",
        json={"title": "To be updated", "status": "pending"},
        headers=auth_headers
    )
    task_id = create_res.json()["id"]

    # Update task
    update_res = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "status": "completed"},
        headers=auth_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"
    assert update_res.json()["status"] == "completed"

    # Delete task
    delete_res = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["success"] is True

    # Confirm 404 after deletion
    get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 404
