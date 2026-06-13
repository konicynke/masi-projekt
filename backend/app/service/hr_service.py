import csv
import io
from app.extension import db
from app.model.leave_request import LeaveRequest
from app.model.user import User
from app.model.leave_type import LeaveType

def get_all_leaves() -> list[LeaveRequest]:
    return db.session.query(LeaveRequest).all()

def generate_leaves_csv_report() -> str:
    leaves = db.session.query(
        LeaveRequest, User, LeaveType
    ).join(
        User, LeaveRequest.user_id == User.id
    ).join(
        LeaveType, LeaveRequest.leave_type_id == LeaveType.id
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Request ID', 'Employee', 'Email', 'Leave Type', 'Start Date', 'End Date', 'Status'])
    
    for request, user, leave_type in leaves:
        writer.writerow([
            request.id,
            f"{user.first_name} {user.last_name}",
            user.email,
            leave_type.name,
            request.start_date.isoformat(),
            request.end_date.isoformat(),
            request.status.value
        ])
        
    return output.getvalue()