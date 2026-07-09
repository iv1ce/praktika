def test_get_me(client, user_headers):
    r = client.get("/api/users/me", headers=user_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "testuser"
    assert data["email"] == "user@test.com"
    assert data["role"] == "user"
    assert "id" in data


def test_update_profile_email(client, user_headers):
    r = client.put("/api/users/me", json={
        "email": "newemail@test.com"
    }, headers=user_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "newemail@test.com"


def test_update_profile_password(client, user_headers):
    r = client.put("/api/users/me", json={
        "old_password": "password123",
        "new_password": "newpass4567"
    }, headers=user_headers)
    assert r.status_code == 200

    token = _get_token(client, "testuser", "newpass4567")
    assert token is not None


def test_update_profile_wrong_old_password(client, user_headers):
    r = client.put("/api/users/me", json={
        "old_password": "wrongpass",
        "new_password": "newpass4567"
    }, headers=user_headers)
    assert r.status_code == 400
    assert "incorrect" in r.json()["detail"].lower()


def test_update_profile_missing_old_password(client, user_headers):
    r = client.put("/api/users/me", json={
        "new_password": "newpass4567"
    }, headers=user_headers)
    assert r.status_code == 400
    assert "required" in r.json()["detail"].lower()


def test_update_profile_duplicate_email(client, user_headers):
    client.post("/api/auth/register", json={
        "username": "other", "email": "other@test.com", "password": "password123"
    })
    r = client.put("/api/users/me", json={
        "email": "other@test.com"
    }, headers=user_headers)
    assert r.status_code == 400
    assert "already taken" in r.json()["detail"]


def test_list_users_admin(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "someone", "email": "someone@test.com", "password": "password123"
    })
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200
    users = r.json()
    assert len(users) == 2  # admin + someone
    usernames = {u["username"] for u in users}
    assert "admin" in usernames
    assert "someone" in usernames


def test_list_users_forbidden_for_user(client, user_headers):
    r = client.get("/api/users", headers=user_headers)
    assert r.status_code == 403


def test_admin_block_user(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "victim", "email": "victim@test.com", "password": "password123"
    })
    r = client.patch("/api/users/2/status", json={"is_active": False}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_admin_unblock_user(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "victim", "email": "victim@test.com", "password": "password123"
    })
    client.patch("/api/users/2/status", json={"is_active": False}, headers=admin_headers)
    r = client.patch("/api/users/2/status", json={"is_active": True}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["is_active"] is True


def test_admin_cannot_block_self(client, admin_headers):
    r = client.patch("/api/users/1/status", json={"is_active": False}, headers=admin_headers)
    assert r.status_code == 400
    assert "Cannot block yourself" in r.json()["detail"]


def test_admin_change_role(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "victim", "email": "victim@test.com", "password": "password123"
    })
    r = client.patch("/api/users/2/role", json={"role": "admin"}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["role"] == "admin"


def test_admin_cannot_demote_self(client, admin_headers):
    r = client.patch("/api/users/1/role", json={"role": "user"}, headers=admin_headers)
    assert r.status_code == 400
    assert "Cannot change your own role" in r.json()["detail"]


def test_admin_delete_user(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "goner", "email": "goner@test.com", "password": "password123"
    })
    r = client.delete("/api/users/2", headers=admin_headers)
    assert r.status_code == 204
    r = client.get("/api/users", headers=admin_headers)
    assert len(r.json()) == 1


def test_admin_delete_user_not_found(client, admin_headers):
    r = client.delete("/api/users/9999", headers=admin_headers)
    assert r.status_code == 404


def _get_token(client, username, password):
    r = client.post("/api/auth/login", json={
        "username": username, "password": password
    })
    if r.status_code == 200:
        return r.json()["access_token"]
    return None
