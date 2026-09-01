from fastapi.testclient import TestClient


def create_test_project(client: TestClient) -> dict:
    response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Integration test project",
        },
    )

    assert response.status_code == 201

    return response.json()

def test_create_project(client: TestClient) -> None:
    response = client.post(
        "/api/projects",
        json={
            "name": "EVM Project",
            "description": "Integration test",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "EVM Project"
    assert body["description"] == "Integration test"
    assert isinstance(body["id"], int)

    assert "created_at" in body
    assert "updated_at" in body

def test_list_projects(client: TestClient) -> None:
    create_test_project(client)

    response = client.get("/api/projects")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["name"] == "Test Project"

def test_get_project(client: TestClient) -> None:
    project = create_test_project(client)

    response = client.get(
        f"/api/projects/{project['id']}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == project["id"]
    assert body["name"] == "Test Project"
    assert body["description"] == "Integration test project"

def test_update_project(client: TestClient) -> None:
    project = create_test_project(client)

    response = client.put(
        f"/api/projects/{project['id']}",
        json={
            "name": "Updated Project",
            "description": "Updated through integration test",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == project["id"]
    assert body["name"] == "Updated Project"
    assert body["description"] == "Updated through integration test"

def test_delete_project(client: TestClient) -> None:
    project = create_test_project(client)

    response = client.delete(
        f"/api/projects/{project['id']}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"/api/projects/{project['id']}"
    )

    assert get_response.status_code == 404
def test_get_unknown_project_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/api/projects/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }
def test_create_project_rejects_empty_name(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/projects",
        json={
            "name": "   ",
            "description": "Invalid project",
        },
    )

    assert response.status_code == 422