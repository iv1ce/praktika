import pytest


class TestRegisterValidation:
    def test_username_too_short(self, client):
        r = client.post("/api/auth/register", json={
            "username": "ab", "email": "test@test.com", "password": "password123"
        })
        assert r.status_code == 422

    def test_username_special_chars(self, client):
        r = client.post("/api/auth/register", json={
            "username": "user name!", "email": "test@test.com", "password": "password123"
        })
        assert r.status_code == 422

    def test_username_cyrillic(self, client):
        r = client.post("/api/auth/register", json={
            "username": "пользователь", "email": "test@test.com", "password": "password123"
        })
        assert r.status_code == 422

    def test_password_too_short(self, client):
        r = client.post("/api/auth/register", json={
            "username": "validuser", "email": "test@test.com", "password": "1234567"
        })
        assert r.status_code == 422

    def test_invalid_email(self, client):
        r = client.post("/api/auth/register", json={
            "username": "validuser", "email": "not-an-email", "password": "password123"
        })
        assert r.status_code == 422

    def test_empty_title_task(self, client, user_headers):
        r = client.post("/api/tasks", json={
            "title": "", "description": "desc"
        }, headers=user_headers)
        assert r.status_code == 422

    def test_invalid_role_value(self, client, admin_headers):
        client.post("/api/auth/register", json={
            "username": "victim", "email": "v@test.com", "password": "password123"
        })
        r = client.patch("/api/users/2/role", json={"role": "superadmin"}, headers=admin_headers)
        assert r.status_code == 400
