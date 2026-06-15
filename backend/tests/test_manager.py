"""WF-04 (akceptacja/odrzucenie wniosków) i WF-05 (widok nieobecności zespołu)."""
from conftest import (
    make_user, make_leave_type, make_balance,
    make_leave_request, make_token, auth,
)
from app.model.user import UserRole
from app.model.leave_request import LeaveRequestStatus


class TestTeamLeaves:
    """WF-05: Menadżer widzi zbiorczy kalendarz nieobecności podległych pracowników."""

    def test_manager_sees_subordinates_requests(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.get("/api/manager/team-leaves", headers=auth(token))
        assert res.status_code == 200
        assert len(res.json) == 1
        assert "user_name" in res.json[0]
        assert "start" in res.json[0]
        assert "status" in res.json[0]

    def test_manager_does_not_see_other_teams_requests(self, app, client):
        mgr1_id = make_user(app, email="mgr1@test.pl", role=UserRole.MANAGER)
        mgr2_id = make_user(app, email="mgr2@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr2_id)
        lt_id = make_leave_type(app)
        make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr1_id, "MANAGER")
        res = client.get("/api/manager/team-leaves", headers=auth(token))
        assert res.status_code == 200
        assert res.json == []

    def test_employee_cannot_access_team_view(self, app, client):
        uid = make_user(app)
        token = make_token(app, uid, "EMPLOYEE")
        res = client.get("/api/manager/team-leaves", headers=auth(token))
        assert res.status_code == 403


class TestApproveLeave:
    """WF-04: Menadżer akceptuje wniosek."""

    def test_approve_changes_status_to_approved(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        make_balance(app, emp_id, lt_id, year=2026, total_days=26)
        lr_id = make_leave_request(app, emp_id, lt_id, start="2026-08-01", end="2026-08-05")
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "APPROVED"},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["new_status"] == "APPROVED"

    def test_approve_increments_used_days(self, app, client):
        from app.extension import db
        from app.model.leave_balance import LeaveBalance
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        bal_id = make_balance(app, emp_id, lt_id, year=2026, total_days=26)
        # 2026-08-01 to 2026-08-05 = 5 days
        lr_id = make_leave_request(app, emp_id, lt_id, start="2026-08-01", end="2026-08-05")
        token = make_token(app, mgr_id, "MANAGER")
        client.patch(f"/api/manager/leaves/{lr_id}/status",
                     json={"status": "APPROVED"},
                     headers=auth(token))
        with app.app_context():
            bal = db.session.get(LeaveBalance, bal_id)
            assert bal.used_days == 5

    def test_approve_with_optional_comment(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        make_balance(app, emp_id, lt_id, year=2026, total_days=26)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "APPROVED", "comment": "Miłego wypoczynku"},
                           headers=auth(token))
        assert res.status_code == 200

    def test_cannot_approve_already_approved_request(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        make_balance(app, emp_id, lt_id, year=2026, total_days=26, used_days=5)
        lr_id = make_leave_request(app, emp_id, lt_id, status=LeaveRequestStatus.APPROVED)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "APPROVED"},
                           headers=auth(token))
        assert res.status_code == 400

    def test_manager_cannot_approve_other_teams_request(self, app, client):
        mgr1_id = make_user(app, email="mgr1@test.pl", role=UserRole.MANAGER)
        mgr2_id = make_user(app, email="mgr2@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr2_id)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr1_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "APPROVED"},
                           headers=auth(token))
        assert res.status_code == 400


class TestRejectLeave:
    """WF-04: Menadżer odrzuca wniosek – uzasadnienie jest wymagane."""

    def test_reject_without_comment_returns_400(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "REJECTED"},
                           headers=auth(token))
        assert res.status_code == 400

    def test_reject_with_comment_changes_status_to_rejected(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "REJECTED", "comment": "Brak zastępstwa"},
                           headers=auth(token))
        assert res.status_code == 200
        assert res.json["new_status"] == "REJECTED"

    def test_invalid_status_value_returns_400(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={"status": "MAYBE"},
                           headers=auth(token))
        assert res.status_code == 400

    def test_missing_status_field_returns_400(self, app, client):
        mgr_id = make_user(app, email="mgr@test.pl", role=UserRole.MANAGER)
        emp_id = make_user(app, email="emp@test.pl", manager_id=mgr_id)
        lt_id = make_leave_type(app)
        lr_id = make_leave_request(app, emp_id, lt_id)
        token = make_token(app, mgr_id, "MANAGER")
        res = client.patch(f"/api/manager/leaves/{lr_id}/status",
                           json={},
                           headers=auth(token))
        assert res.status_code == 400
