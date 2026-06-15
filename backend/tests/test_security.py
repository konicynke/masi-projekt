"""WNF-01: Dostęp do danych musi być ograniczony zgodnie z rolami.

Pracownik widzi tylko swoje dane; menadżer dane zespołu;
HR i Admin mają szerszy dostęp – ale nie wzajemny.
"""
import pytest
from conftest import make_user, make_token, auth
from app.model.user import UserRole


# ── endpoint matrices ─────────────────────────────────────────────────────────

MANAGER_ENDPOINTS = [
    ("GET", "/api/manager/team-leaves"),
]

HR_ENDPOINTS = [
    ("GET", "/api/hr/leaves"),
    ("GET", "/api/hr/reports/csv"),
    ("GET", "/api/hr/reports/pdf"),
    ("GET", "/api/hr/reports/xls"),
    ("GET", "/api/hr/balances"),
    ("GET", "/api/hr/users"),
    ("GET", "/api/hr/leave-types"),
]

ADMIN_ENDPOINTS = [
    ("GET", "/api/admin/users"),
    ("GET", "/api/admin/departments"),
    ("GET", "/api/admin/leave-types"),
]


# ── unauthenticated access ────────────────────────────────────────────────────

class TestUnauthenticatedAccess:
    @pytest.mark.parametrize("path", [
        "/api/auth/me",
        "/api/leaves/my",
        "/api/leaves/balance",
        "/api/leaves/types",
        "/api/manager/team-leaves",
        "/api/hr/leaves",
        "/api/admin/users",
    ])
    def test_protected_endpoint_returns_401_without_token(self, client, path):
        res = client.get(path)
        assert res.status_code == 401, f"Expected 401 for GET {path}"


# ── employee access restrictions ──────────────────────────────────────────────

class TestEmployeeRestrictions:
    def test_employee_forbidden_on_all_manager_endpoints(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        for method, path in MANAGER_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"

    def test_employee_forbidden_on_all_hr_endpoints(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        for method, path in HR_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"

    def test_employee_forbidden_on_all_admin_endpoints(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        for method, path in ADMIN_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"


# ── manager access restrictions ───────────────────────────────────────────────

class TestManagerRestrictions:
    def test_manager_allowed_on_team_leaves(self, app, client):
        uid = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        token = make_token(app, uid, "MANAGER")
        res = client.get("/api/manager/team-leaves", headers=auth(token))
        assert res.status_code == 200

    def test_manager_forbidden_on_hr_endpoints(self, app, client):
        uid = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        token = make_token(app, uid, "MANAGER")
        for method, path in HR_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"

    def test_manager_forbidden_on_admin_endpoints(self, app, client):
        uid = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        token = make_token(app, uid, "MANAGER")
        for method, path in ADMIN_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"


# ── HR access restrictions ────────────────────────────────────────────────────

class TestHRRestrictions:
    def test_hr_allowed_on_hr_endpoints(self, app, client):
        uid = make_user(app, email="hr@test.pl", role=UserRole.HR)
        token = make_token(app, uid, "HR")
        res = client.get("/api/hr/users", headers=auth(token))
        assert res.status_code == 200

    def test_hr_forbidden_on_admin_endpoints(self, app, client):
        uid = make_user(app, email="hr@test.pl", role=UserRole.HR)
        token = make_token(app, uid, "HR")
        for method, path in ADMIN_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"

    def test_hr_forbidden_on_manager_endpoints(self, app, client):
        uid = make_user(app, email="hr@test.pl", role=UserRole.HR)
        token = make_token(app, uid, "HR")
        for method, path in MANAGER_ENDPOINTS:
            res = getattr(client, method.lower())(path, headers=auth(token))
            assert res.status_code == 403, f"Expected 403 for {method} {path}"


# ── admin access ──────────────────────────────────────────────────────────────

class TestAdminAccess:
    def test_admin_allowed_on_admin_endpoints(self, app, client):
        uid = make_user(app, email="admin@test.pl", role=UserRole.ADMIN)
        token = make_token(app, uid, "ADMIN")
        res = client.get("/api/admin/users", headers=auth(token))
        assert res.status_code == 200

    def test_admin_allowed_on_hr_endpoints(self, app, client):
        """Admin ma dostęp do endpointów HR (zdefiniowane w hr_controller @role_required('HR','ADMIN'))."""
        uid = make_user(app, email="admin@test.pl", role=UserRole.ADMIN)
        token = make_token(app, uid, "ADMIN")
        res = client.get("/api/hr/users", headers=auth(token))
        assert res.status_code == 200


# ── data isolation ────────────────────────────────────────────────────────────

class TestDataIsolation:
    def test_employee_sees_only_own_leave_requests(self, app, client):
        uid1 = make_user(app, email="u1@test.pl")
        uid2 = make_user(app, email="u2@test.pl")
        from conftest import make_leave_type, make_leave_request
        lt_id = make_leave_type(app)
        make_leave_request(app, uid1, lt_id, start="2026-08-01", end="2026-08-03")
        make_leave_request(app, uid2, lt_id, start="2026-09-01", end="2026-09-03")

        token = make_token(app, uid1, "EMPLOYEE")
        res = client.get("/api/leaves/my", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 1

    def test_manager_sees_only_subordinates_not_all_employees(self, app, client):
        mgr1_id = make_user(app, email="mgr1@test.pl", role=UserRole.MANAGER)
        mgr2_id = make_user(app, email="mgr2@test.pl", role=UserRole.MANAGER)
        emp1_id = make_user(app, email="emp1@test.pl", manager_id=mgr1_id)
        emp2_id = make_user(app, email="emp2@test.pl", manager_id=mgr2_id)
        from conftest import make_leave_type, make_leave_request
        lt_id = make_leave_type(app)
        make_leave_request(app, emp1_id, lt_id)
        make_leave_request(app, emp2_id, lt_id)

        token = make_token(app, mgr1_id, "MANAGER")
        res = client.get("/api/manager/team-leaves", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 1  # only emp1's request
