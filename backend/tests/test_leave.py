"""WF-02 (podgląd limitu) i WF-03 (składanie, edycja, wycofywanie wniosków)."""
from conftest import (
    make_user, make_leave_type, make_balance,
    make_leave_request, make_token, auth,
)
from app.model.leave_request import LeaveRequestStatus


class TestLeaveBalance:
    """WF-02: System wyświetla aktualną liczbę dostępnych dni urlopowych."""

    def test_balance_shows_remaining_days_for_current_year(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26, used_days=5)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/leaves/balance", headers=auth(token))
        assert res.status_code == 200
        entry = res.json[0]
        assert entry["total_days"] == 26
        assert entry["used_days"] == 5
        assert entry["remaining_days"] == 21

    def test_balance_is_empty_when_no_records_exist(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/leaves/balance", headers=auth(token))
        assert res.status_code == 200
        assert res.json == []

    def test_balance_requires_authentication(self, client):
        res = client.get("/api/leaves/balance")
        assert res.status_code == 401

    def test_multiple_leave_types_listed_separately(self, app, client):
        uid = make_user(app)
        lt1 = make_leave_type(app, name="Wypoczynkowy")
        lt2 = make_leave_type(app, name="L4")
        make_balance(app, uid, lt1, year=2026, total_days=26)
        make_balance(app, uid, lt2, year=2026, total_days=10)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/leaves/balance", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 2


class TestLeaveTypes:
    def test_leave_types_list_returned(self, app, client):
        uid = make_user(app)
        make_leave_type(app, name="Urlop wypoczynkowy")
        make_leave_type(app, name="L4")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/leaves/types", headers=auth(token))
        assert res.status_code == 200
        names = [t["name"] for t in res.json]
        assert "Urlop wypoczynkowy" in names
        assert "L4" in names


class TestSubmitLeave:
    """WF-03: Pracownik wypełnia formularz (data od-do, typ urlopu)."""

    def test_valid_request_creates_pending_leave(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-05",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 201
        assert "id" in res.json

    def test_request_with_reason_is_accepted(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-03",
            "leave_type_id": lt_id,
            "reason": "Wakacje",
        }, headers=auth(token))
        assert res.status_code == 201

    def test_insufficient_balance_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=3)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-10",  # 10 days, only 3 available
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_missing_balance_record_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-05",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_end_date_before_start_date_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-10",
            "end_date": "2026-08-01",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_overlapping_active_request_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26)
        make_leave_request(app, uid, lt_id, start="2026-08-01", end="2026-08-10")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.post("/api/leaves", json={
            "start_date": "2026-08-05",
            "end_date": "2026-08-15",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_submit_requires_authentication(self, client):
        res = client.post("/api/leaves", json={})
        assert res.status_code == 401


class TestListMyLeaves:
    def test_employee_sees_only_own_requests(self, app, client):
        uid1 = make_user(app, email="u1@test.pl")
        uid2 = make_user(app, email="u2@test.pl")
        lt_id = make_leave_type(app)
        make_leave_request(app, uid1, lt_id, start="2026-08-01", end="2026-08-03")
        make_leave_request(app, uid2, lt_id, start="2026-09-01", end="2026-09-03")
        token = make_token(app, uid1, "EMPLOYEE")
        res = client.get("/api/leaves/my", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 1

    def test_status_included_in_response(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_leave_request(app, uid, lt_id)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/leaves/my", headers=auth(token))
        assert res.status_code == 200
        assert res.json[0]["status"] == "PENDING"


class TestEditLeave:
    """WF-03: Pracownik może edytować wniosek ze statusem PENDING."""

    def test_edit_pending_request_succeeds(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26)
        lr_id = make_leave_request(app, uid, lt_id, start="2026-08-01", end="2026-08-05")
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}", json={
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 200

    def test_edit_approved_request_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        make_balance(app, uid, lt_id, year=2026, total_days=26, used_days=5)
        lr_id = make_leave_request(app, uid, lt_id, status=LeaveRequestStatus.APPROVED)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}", json={
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_edit_other_users_request_returns_400(self, app, client):
        uid1 = make_user(app, email="u1@test.pl")
        uid2 = make_user(app, email="u2@test.pl")
        lt_id = make_leave_type(app)
        make_balance(app, uid1, lt_id, year=2026, total_days=26)
        lr_id = make_leave_request(app, uid1, lt_id)
        token = make_token(app, uid2, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}", json={
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "leave_type_id": lt_id,
        }, headers=auth(token))
        assert res.status_code == 400


class TestCancelLeave:
    """WF-03: Pracownik może wycofać wniosek (PENDING lub APPROVED)."""

    def test_cancel_pending_request(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, uid, lt_id)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}/cancel", headers=auth(token))
        assert res.status_code == 200
        assert res.json["status"] == "CANCELLED"

    def test_cancel_approved_request_restores_used_days(self, app, client):
        from app.extension import db
        from app.model.leave_balance import LeaveBalance
        uid = make_user(app)
        lt_id = make_leave_type(app)
        # Simulate state after approval: 5 days used for leave 2026-08-01–05
        bal_id = make_balance(app, uid, lt_id, year=2026, total_days=26, used_days=5)
        lr_id = make_leave_request(
            app, uid, lt_id,
            start="2026-08-01", end="2026-08-05",
            status=LeaveRequestStatus.APPROVED,
        )
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}/cancel", headers=auth(token))
        assert res.status_code == 200
        with app.app_context():
            bal = db.session.get(LeaveBalance, bal_id)
            assert bal.used_days == 0  # 5 used - 5 restored = 0

    def test_cancel_rejected_request_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, uid, lt_id, status=LeaveRequestStatus.REJECTED)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}/cancel", headers=auth(token))
        assert res.status_code == 400

    def test_cancel_already_cancelled_request_returns_400(self, app, client):
        uid = make_user(app)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, uid, lt_id, status=LeaveRequestStatus.CANCELLED)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}/cancel", headers=auth(token))
        assert res.status_code == 400

    def test_cancel_other_users_request_returns_400(self, app, client):
        uid1 = make_user(app, email="u1@test.pl")
        uid2 = make_user(app, email="u2@test.pl")
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, uid1, lt_id)
        token = make_token(app, uid2, "EMPLOYEE")
        res = client.patch(f"/api/leaves/{lr_id}/cancel", headers=auth(token))
        assert res.status_code == 400
