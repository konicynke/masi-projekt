from datetime import date

from app.extension import db
from app.model.leave_request import LeaveRequest, LeaveRequestStatus
from app.model.leave_balance import LeaveBalance
from app.model.user import User
from app.service.notification_service import send_status_update_email

def create_leave_request(
    user_id: int,
    leave_type_id: int,
    start_date: date,
    end_date: date,
    reason: str | None = None
) -> LeaveRequest:

    if start_date > end_date:
        raise ValueError("Start date cannot be later than end date.")

    overlapping_request = db.session.query(LeaveRequest).filter(
        LeaveRequest.user_id == user_id,
        LeaveRequest.status.in_([
            LeaveRequestStatus.PENDING,
            LeaveRequestStatus.APPROVED
        ]),
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date
    ).first()

    if overlapping_request:
        raise ValueError("You already have an active leave request during this period.")

    requested_days = (end_date - start_date).days + 1
    request_year = start_date.year

    balance = db.session.query(LeaveBalance).filter_by(
        user_id=user_id,
        leave_type_id=leave_type_id,
        year=request_year
    ).first()

    if not balance:
        raise ValueError("No leave balance defined for this leave type in the selected year.")

    available_days = balance.total_days - balance.used_days

    if requested_days > available_days:
        raise ValueError(f"Not enough available days. Requested: {requested_days}, available: {available_days}.")

    new_request = LeaveRequest(
        user_id=user_id,
        leave_type_id=leave_type_id,
        start_date=start_date,
        end_date=end_date,
        status=LeaveRequestStatus.PENDING,
        request_reason=reason
    )

    db.session.add(new_request)
    db.session.commit()

    return new_request


def get_user_leaves(user_id: int) -> list[LeaveRequest]:
    return db.session.query(LeaveRequest).filter_by(user_id=user_id).all()


def get_team_leaves(manager_id: int) -> list[LeaveRequest]:
    return db.session.query(LeaveRequest).join(User).filter(
        User.manager_id == manager_id
    ).all()


def update_leave_status(
    request_id: int,
    manager_id: int,
    new_status: LeaveRequestStatus,
    comment: str | None = None
) -> LeaveRequest:

    request = db.session.query(LeaveRequest).get(request_id)

    if not request:
        raise ValueError("Leave request not found.")

    user = db.session.query(User).get(request.user_id)

    if user.manager_id != manager_id:
        raise ValueError("You are not authorized to manage this user's leaves.")

    if request.status != LeaveRequestStatus.PENDING:
        raise ValueError("Only PENDING requests can be updated.")

    request.status = new_status
    request.manager_comment = comment

    if new_status == LeaveRequestStatus.APPROVED:
        days = (request.end_date - request.start_date).days + 1

        balance = db.session.query(LeaveBalance).filter_by(
            user_id=request.user_id,
            leave_type_id=request.leave_type_id,
            year=request.start_date.year
        ).first()

        balance.used_days += days

    db.session.commit()
    
    send_status_update_email(
        user=user,
        status=new_status.value,
        start_date=request.start_date.isoformat(),
        end_date=request.end_date.isoformat()
    )

    return request


def cancel_leave_request(request_id: int, user_id: int) -> LeaveRequest:

    request = db.session.query(LeaveRequest).get(request_id)

    if not request or request.user_id != user_id:
        raise ValueError("Leave request not found or access denied.")

    if request.status in [
        LeaveRequestStatus.REJECTED,
        LeaveRequestStatus.CANCELLED
    ]:
        raise ValueError("This request is already finalized or cancelled.")

    if request.status == LeaveRequestStatus.APPROVED:
        days = (request.end_date - request.start_date).days + 1

        balance = db.session.query(LeaveBalance).filter_by(
            user_id=request.user_id,
            leave_type_id=request.leave_type_id,
            year=request.start_date.year
        ).first()

        balance.used_days -= days

    request.status = LeaveRequestStatus.CANCELLED

    db.session.commit()

    user = db.session.query(User).get(request.user_id)
    send_status_update_email(
        user=user,
        status=LeaveRequestStatus.CANCELLED.value,
        start_date=request.start_date.isoformat(),
        end_date=request.end_date.isoformat()
    )

    return request