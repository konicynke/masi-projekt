"""WF-07: Moduł raportowy HR – raporty PDF/XLS/CSV i zarządzanie limitami."""
from conftest import (
    make_user, make_leave_type, make_balance,
    make_leave_request, make_token, auth,
)
from app.model.user import UserRole


# ── helpers ───────────────────────────────────────────────────────────────────

def _hr_token(app):
    uid = make_user(app, email="hr@test.pl", role=UserRole.HR)
    return make_token(app, uid, "HR")


def _seed_leave(app):
    """Create a minimal leave request so reports have at least one row."""
    uid = make_user(app, email="emp@test.pl")
    lt_id = make_leave_type(app)
    make_leave_request(app, uid, lt_id)


# ── leave listing ─────────────────────────────────────────────────────────────

class TestHRLeaves:
    def test_hr_lists_all_leaves_across_employees(self, app, client):
        uid1 = make_user(app, email="u1@test.pl")
        uid2 = make_user(app, email="u2@test.pl")
        lt_id = make_leave_type(app)
        make_leave_request(app, uid1, lt_id, start="2026-08-01", end="2026-08-03")
        make_leave_request(app, uid2, lt_id, start="2026-09-01", end="2026-09-03")
        token = _hr_token(app)
        res = client.get("/api/hr/leaves", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 2

    def test_response_contains_required_fields(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app)
        make_leave_request(app, uid, lt_id)
        token = _hr_token(app)
        res = client.get("/api/hr/leaves", headers=auth(token))
        assert res.status_code == 200
        entry = res.json[0]
        for field in ("id", "user_name", "leave_type", "start_date", "end_date", "status"):
            assert field in entry, f"Missing field: {field}"


# ── reports (WF-07) ───────────────────────────────────────────────────────────

class TestHRReports:
    """WF-07: Specjalista HR generuje raport (PDF/XLS) z zestawieniem urlopów."""

    def test_csv_report_returns_200_and_correct_content_type(self, app, client):
        _seed_leave(app)
        token = _hr_token(app)
        res = client.get("/api/hr/reports/csv", headers=auth(token))
        assert res.status_code == 200
        assert "text/csv" in res.content_type

    def test_pdf_report_returns_200_and_correct_content_type(self, app, client):
        _seed_leave(app)
        token = _hr_token(app)
        res = client.get("/api/hr/reports/pdf", headers=auth(token))
        assert res.status_code == 200
        assert "application/pdf" in res.content_type

    def test_xls_report_returns_200_and_correct_content_type(self, app, client):
        _seed_leave(app)
        token = _hr_token(app)
        res = client.get("/api/hr/reports/xls", headers=auth(token))
        assert res.status_code == 200
        assert "spreadsheet" in res.content_type

    def test_csv_report_contains_header_row(self, app, client):
        _seed_leave(app)
        token = _hr_token(app)
        res = client.get("/api/hr/reports/csv", headers=auth(token))
        text = res.data.decode()
        assert "Employee" in text
        assert "Status" in text

    def test_pdf_report_starts_with_pdf_magic_bytes(self, app, client):
        _seed_leave(app)
        token = _hr_token(app)
        res = client.get("/api/hr/reports/pdf", headers=auth(token))
        assert res.data[:4] == b"%PDF"

    def test_reports_require_authentication(self, client):
        for fmt in ("csv", "pdf", "xls"):
            res = client.get(f"/api/hr/reports/{fmt}")
            assert res.status_code == 401, f"Expected 401 for {fmt}"


# ── balance management ────────────────────────────────────────────────────────

class TestHRBalances:
    def test_create_balance_for_employee(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app)
        token = _hr_token(app)
        res = client.post("/api/hr/balances", json={
            "user_id": uid,
            "leave_type_id": lt_id,
            "year": 2026,
            "total_days": 20,
        }, headers=auth(token))
        assert res.status_code == 201
        assert "id" in res.json

    def test_create_duplicate_balance_returns_400(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026)
        token = _hr_token(app)
        res = client.post("/api/hr/balances", json={
            "user_id": uid,
            "leave_type_id": lt_id,
            "year": 2026,
            "total_days": 20,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_update_balance_total_days(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app)
        bal_id = make_balance(app, uid, lt_id, year=2026, total_days=20)
        token = _hr_token(app)
        res = client.patch(f"/api/hr/balances/{bal_id}",
                           json={"total_days": 26},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["total_days"] == 26

    def test_update_balance_below_used_days_returns_400(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app)
        bal_id = make_balance(app, uid, lt_id, year=2026, total_days=20, used_days=10)
        token = _hr_token(app)
        res = client.patch(f"/api/hr/balances/{bal_id}",
                           json={"total_days": 5},  # below used_days=10
                           headers=auth(token))
        assert res.status_code == 400

    def test_list_balances_returns_enriched_data(self, app, client):
        uid = make_user(app, email="emp@test.pl")
        lt_id = make_leave_type(app, name="Urlop wypoczynkowy")
        make_balance(app, uid, lt_id, year=2026, total_days=26, used_days=3)
        token = _hr_token(app)
        res = client.get("/api/hr/balances", headers=auth(token))
        assert res.status_code == 200
        entry = res.json[0]
        assert entry["total_days"] == 26
        assert entry["used_days"] == 3
        assert entry["remaining_days"] == 23
        assert "user_name" in entry
        assert "leave_type_name" in entry


# ── user listing ──────────────────────────────────────────────────────────────

class TestHRUsers:
    def test_list_all_users(self, app, client):
        make_user(app, email="u1@test.pl")
        make_user(app, email="u2@test.pl")
        token = _hr_token(app)
        res = client.get("/api/hr/users", headers=auth(token))
        assert res.status_code == 200
        # hr user itself + u1 + u2 = 3
        assert len(res.json) == 3

    def test_user_list_contains_required_fields(self, app, client):
        make_user(app, email="emp@test.pl")
        token = _hr_token(app)
        res = client.get("/api/hr/users", headers=auth(token))
        assert res.status_code == 200
        for field in ("id", "name", "email", "role"):
            assert field in res.json[0], f"Missing field: {field}"
