def test_create_task(client, user_headers):
    r = client.post("/api/tasks", json={
        "title": "Test Task", "description": "Test Description"
    }, headers=user_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert data["owner_name"] == "testuser"


def test_list_tasks(client, user_headers):
    client.post("/api/tasks", json={"title": "Task 1"}, headers=user_headers)
    client.post("/api/tasks", json={"title": "Task 2"}, headers=user_headers)
    r = client.get("/api/tasks", headers=user_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2


def test_get_task(client, user_headers):
    r = client.post("/api/tasks", json={"title": "My Task"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.get(f"/api/tasks/{task_id}", headers=user_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "My Task"


def test_get_task_not_found(client, user_headers):
    r = client.get("/api/tasks/9999", headers=user_headers)
    assert r.status_code == 404


def test_update_task_title(client, user_headers):
    r = client.post("/api/tasks", json={"title": "Old Title"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.put(f"/api/tasks/{task_id}", json={
        "title": "New Title"
    }, headers=user_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "New Title"


def test_update_task_completed(client, user_headers):
    r = client.post("/api/tasks", json={"title": "Do it"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.put(f"/api/tasks/{task_id}", json={
        "completed": True
    }, headers=user_headers)
    assert r.status_code == 200
    assert r.json()["completed"] is True


def test_delete_task(client, user_headers):
    r = client.post("/api/tasks", json={"title": "Delete me"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.delete(f"/api/tasks/{task_id}", headers=user_headers)
    assert r.status_code == 204
    r = client.get(f"/api/tasks/{task_id}", headers=user_headers)
    assert r.status_code == 404


def test_user_cannot_see_others_tasks(client, user_headers, second_user_headers):
    client.post("/api/tasks", json={"title": "User1 Task"}, headers=user_headers)
    r = client.get("/api/tasks", headers=second_user_headers)
    tasks = r.json()
    assert all(t["owner_id"] != 1 for t in tasks)


def test_user_cannot_get_others_task(client, user_headers, second_user_headers):
    r = client.post("/api/tasks", json={"title": "Secret"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.get(f"/api/tasks/{task_id}", headers=second_user_headers)
    assert r.status_code == 403


def test_user_cannot_update_others_task(client, user_headers, second_user_headers):
    r = client.post("/api/tasks", json={"title": "Not yours"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.put(f"/api/tasks/{task_id}", json={
        "title": "Hacked"
    }, headers=second_user_headers)
    assert r.status_code == 403


def test_user_cannot_delete_others_task(client, user_headers, second_user_headers):
    r = client.post("/api/tasks", json={"title": "Not yours"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.delete(f"/api/tasks/{task_id}", headers=second_user_headers)
    assert r.status_code == 403


def test_admin_sees_all_tasks(client, user_headers, admin_headers, second_user_headers):
    client.post("/api/tasks", json={"title": "User1 Task"}, headers=user_headers)
    client.post("/api/tasks", json={"title": "User2 Task"}, headers=second_user_headers)
    r = client.get("/api/tasks", headers=admin_headers)
    assert len(r.json()) == 2


def test_admin_can_update_any_task(client, user_headers, admin_headers):
    r = client.post("/api/tasks", json={"title": "Admin fix"}, headers=user_headers)
    task_id = r.json()["id"]
    r = client.put(f"/api/tasks/{task_id}", json={
        "completed": True
    }, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["completed"] is True
