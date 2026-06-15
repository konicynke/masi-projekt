"""Testy modułu administracyjnego – zarządzanie użytkownikami, działami, typami urlopów."""
from conftest import make_user, make_leave_type, make_token, auth
from app.model.user import UserRole


# ── helper ────────────────────────────────────────────────────────────────────

def _admin_token(app):
    uid = make_user(app, email="admin@test.pl", role=UserRole.ADMIN)
    return make_token(app, uid, "ADMIN")


# ── user management ───────────────────────────────────────────────────────────

class TestAdminUsers:
    def test_create_employee(self, app, client):
        token = _admin_token(app)
        res = client.post("/api/admin/users", json={
            "email": "new@test.pl",
            "password": "haslo123",
            "first_name": "Anna",
            "last_name": "Nowak",
            "role": "EMPLOYEE",
        }, headers=auth(token))
        assert res.status_code == 201
        assert "id" in res.json

    def test_create_manager_with_role(self, app, client):
        token = _admin_token(app)
        res = client.post("/api/admin/users", json={
            "email": "mgr@test.pl",
            "password": "haslo123",
            "first_name": "Piotr",
            "last_name": "Kowalski",
            "role": "MANAGER",
        }, headers=auth(token))
        assert res.status_code == 201

    def test_create_employee_with_manager_assignment(self, app, client):
        token = _admin_token(app)
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        res = client.post("/api/admin/users", json={
            "email": "emp@test.pl",
            "password": "haslo123",
            "first_name": "Jan",
            "last_name": "Lis",
            "role": "EMPLOYEE",
            "manager_id": mgr_id,
        }, headers=auth(token))
        assert res.status_code == 201

    def test_duplicate_email_returns_400(self, app, client):
        make_user(app, email="existing@test.pl")
        token = _admin_token(app)
        res = client.post("/api/admin/users", json={
            "email": "existing@test.pl",
            "password": "haslo",
            "first_name": "X",
            "last_name": "Y",
            "role": "EMPLOYEE",
        }, headers=auth(token))
        assert res.status_code == 400

    def test_list_users_returns_all_users(self, app, client):
        token = _admin_token(app)
        make_user(app, email="u1@test.pl")
        make_user(app, email="u2@test.pl")
        res = client.get("/api/admin/users", headers=auth(token))
        assert res.status_code == 200
        # admin + u1 + u2 = 3
        assert len(res.json) == 3

    def test_list_users_response_contains_required_fields(self, app, client):
        token = _admin_token(app)
        res = client.get("/api/admin/users", headers=auth(token))
        assert res.status_code == 200
        for field in ("id", "first_name", "last_name", "email", "role"):
            assert field in res.json[0], f"Missing field: {field}"

    def test_non_admin_cannot_create_user(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/admin/users", json={
            "email": "x@test.pl", "password": "x",
            "first_name": "X", "last_name": "Y", "role": "EMPLOYEE",
        }, headers=auth(token))
        assert res.status_code == 403


# ── department management ─────────────────────────────────────────────────────

class TestAdminDepartments:
    def test_create_department(self, app, client):
        token = _admin_token(app)
        res = client.post("/api/admin/departments", json={"name": "IT"}, headers=auth(token))
        assert res.status_code == 201
        assert "id" in res.json

    def test_create_duplicate_department_returns_400(self, app, client):
        from app.extension import db
        from app.model.department import Department
        with app.app_context():
            _db_dep = Department(name="Finance")
            db.session.add(_db_dep)
            db.session.commit()
        token = _admin_token(app)
        res = client.post("/api/admin/departments", json={"name": "Finance"}, headers=auth(token))
        assert res.status_code == 400

    def test_list_departments(self, app, client):
        from app.extension import db
        from app.model.department import Department
        with app.app_context():
            for name in ("IT", "HR", "Finance"):
                db.session.add(Department(name=name))
            db.session.commit()
        token = _admin_token(app)
        res = client.get("/api/admin/departments", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 3

    def test_assign_department_to_user(self, app, client):
        from app.extension import db
        from app.model.department import Department
        uid = make_user(app, email="emp@test.pl")
        with app.app_context():
            dept = Department(name="R&D")
            db.session.add(dept)
            db.session.commit()
            dept_id = dept.id
        token = _admin_token(app)
        res = client.patch(f"/api/admin/users/{uid}/department",
                           json={"department_id": dept_id},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["department_id"] == dept_id

    def test_assign_nonexistent_department_returns_400(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        token = _admin_token(app)
        res = client.patch(f"/api/admin/users/{uid}/department",
                           json={"department_id": 9999},
                           headers=auth(token))
        assert res.status_code == 400


# ── leave type configuration ──────────────────────────────────────────────────

class TestAdminLeaveTypes:
    def test_create_leave_type(self, app, client):
        token = _admin_token(app)
        res = client.post("/api/admin/leave-types", json={
            "name": "Urlop okolicznościowy",
            "requires_approval": True,
        }, headers=auth(token))
        assert res.status_code == 201
        assert "id" in res.json

    def test_create_leave_type_without_approval_flag(self, app, client):
        token = _admin_token(app)
        res = client.post("/api/admin/leave-types", json={
            "name": "L4",
            "requires_approval": False,
        }, headers=auth(token))
        assert res.status_code == 201

    def test_duplicate_leave_type_name_returns_400(self, app, client):
        make_leave_type(app, name="Urlop wypoczynkowy")
        token = _admin_token(app)
        res = client.post("/api/admin/leave-types", json={
            "name": "Urlop wypoczynkowy",
            "requires_approval": True,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_list_leave_types(self, app, client):
        make_leave_type(app, name="Urlop wypoczynkowy")
        make_leave_type(app, name="L4")
        token = _admin_token(app)
        res = client.get("/api/admin/leave-types", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 2
        for entry in res.json:
            assert "name" in entry
            assert "requires_approval" in entry
