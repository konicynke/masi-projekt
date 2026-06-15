"""WF-01: Zarządzanie profilami – logowanie, wylogowanie, edycja danych."""
from conftest import make_user, make_token, auth


class TestLogin:
    def test_valid_credentials_return_token_and_user(self, app, client):
        make_user(app, email="a@test.pl", password="secret")
        res = client.post("/api/auth/login", json={"email": "a@test.pl", "password": "secret"})
        assert res.status_code == 200
        assert "token" in res.json
        assert res.json["user"]["email"] == "a@test.pl"
        assert res.json["user"]["role"] == "EMPLOYEE"

    def test_wrong_password_returns_401(self, app, client):
        make_user(app, email="a@test.pl", password="secret")
        res = client.post("/api/auth/login", json={"email": "a@test.pl", "password": "wrong"})
        assert res.status_code == 401

    def test_unknown_email_returns_401(self, client):
        res = client.post("/api/auth/login", json={"email": "nobody@test.pl", "password": "x"})
        assert res.status_code == 401

    def test_manager_role_reflected_in_token_response(self, app, client):
        from app.model.user import UserRole
        make_user(app, email="mgr@test.pl", password="pass", role=UserRole.MANAGER)
        res = client.post("/api/auth/login", json={"email": "mgr@test.pl", "password": "pass"})
        assert res.status_code == 200
        assert res.json["user"]["role"] == "MANAGER"


class TestGetProfile:
    def test_authenticated_user_gets_own_profile(self, app, client):
        uid = make_user(app, email="b@test.pl", first_name="Anna", last_name="Nowak")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/auth/me", headers=auth(token))
        assert res.status_code == 200
        assert res.json["email"] == "b@test.pl"
        assert res.json["first_name"] == "Anna"
        assert res.json["last_name"] == "Nowak"
        assert res.json["role"] == "EMPLOYEE"

    def test_unauthenticated_request_returns_401(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401


class TestUpdateProfile:
    def test_update_first_and_last_name(self, app, client):
        uid = make_user(app, email="c@test.pl", first_name="Jan", last_name="Kowalski")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch("/api/auth/me",
                           json={"first_name": "Piotr", "last_name": "Nowak"},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["first_name"] == "Piotr"
        assert res.json["last_name"] == "Nowak"

    def test_update_email_to_unused_address(self, app, client):
        uid = make_user(app, email="d@test.pl")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch("/api/auth/me",
                           json={"email": "new@test.pl"},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["email"] == "new@test.pl"

    def test_update_email_to_already_taken_address_fails(self, app, client):
        make_user(app, email="taken@test.pl")
        uid = make_user(app, email="mine@test.pl")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch("/api/auth/me",
                           json={"email": "taken@test.pl"},
                           headers=auth(token))
        assert res.status_code == 400

    def test_update_requires_authentication(self, client):
        res = client.patch("/api/auth/me", json={"first_name": "X"})
        assert res.status_code == 401
