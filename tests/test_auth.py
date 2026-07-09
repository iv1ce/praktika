def test_register_success(client):
    r = client.post("/api/auth/register", json={
        "username": "newuser", "email": "new@test.com", "password": "password123"
    })
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@test.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "dupuser", "email": "first@test.com", "password": "password123"
    })
    r = client.post("/api/auth/register", json={
        "username": "dupuser", "email": "second@test.com", "password": "password123"
    })
    assert r.status_code == 400
    assert "already taken" in r.json()["detail"]


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "username": "user1", "email": "same@test.com", "password": "password123"
    })
    r = client.post("/api/auth/register", json={
        "username": "user2", "email": "same@test.com", "password": "password123"
    })
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "mypassword"
    })
    r = client.post("/api/auth/login", json={
        "username": "loginuser", "password": "mypassword"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrongpass", "email": "wrong@test.com", "password": "correctpass"
    })
    r = client.post("/api/auth/login", json={
        "username": "wrongpass", "password": "wrongpass"
    })
    assert r.status_code == 401
    assert "Invalid" in r.json()["detail"]


def test_login_nonexistent_user(client):
    r = client.post("/api/auth/login", json={
        "username": "nobody", "password": "password123"
    })
    assert r.status_code == 401


def test_login_blocked_user(client, admin_headers):
    client.post("/api/auth/register", json={
        "username": "blocked", "email": "blocked@test.com", "password": "password123"
    })
    client.patch("/api/users/2/status", json={"is_active": False}, headers=admin_headers)

    r = client.post("/api/auth/login", json={
        "username": "blocked", "password": "password123"
    })
    assert r.status_code == 403
    assert "blocked" in r.json()["detail"].lower()


def test_brute_force_lockout(client):
    client.post("/api/auth/register", json={
        "username": "bruteforce", "email": "brute@test.com", "password": "realpass123"
    })
    for _ in range(5):
        client.post("/api/auth/login", json={
            "username": "bruteforce", "password": "wrongpass"
        })
    r = client.post("/api/auth/login", json={
        "username": "bruteforce", "password": "realpass123"
    })
    assert r.status_code == 423
    assert "locked" in r.json()["detail"].lower()


def test_brute_force_counter_resets_on_success(client):
    client.post("/api/auth/register", json={
        "username": "resetuser", "email": "reset@test.com", "password": "realpass123"
    })
    for _ in range(3):
        client.post("/api/auth/login", json={
            "username": "resetuser", "password": "wrongpass"
        })
    r = client.post("/api/auth/login", json={
        "username": "resetuser", "password": "realpass123"
    })
    assert r.status_code == 200

    for _ in range(5):
        client.post("/api/auth/login", json={
            "username": "resetuser", "password": "wrongpass"
        })
    r = client.post("/api/auth/login", json={
        "username": "resetuser", "password": "realpass123"
    })
    assert r.status_code == 423


def _login_get_token(client, username, password):
    r = client.post("/api/auth/login", json={
        "username": username, "password": password
    })
    return r.json()["access_token"]
