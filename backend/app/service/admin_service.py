from werkzeug.security import generate_password_hash
from app.extension import db
from app.model.user import User, UserRole
from app.model.leave_type import LeaveType
from app.model.leave_balance import LeaveBalance
from app.model.department import Department


def create_new_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole,
    manager_id: int = None,
    department_id: int = None,
) -> User:
    if db.session.query(User).filter_by(email=email).first():
        raise ValueError("User with this email already exists.")

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        manager_id=manager_id,
        department_id=department_id,
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def create_new_leave_type(name: str, requires_approval: bool) -> LeaveType:
    if db.session.query(LeaveType).filter_by(name=name).first():
        raise ValueError("Leave type with this name already exists.")

    new_type = LeaveType(name=name, requires_approval=requires_approval)
    db.session.add(new_type)
    db.session.commit()
    return new_type


def create_new_balance(user_id: int, leave_type_id: int, year: int, total_days: int) -> LeaveBalance:
    existing = db.session.query(LeaveBalance).filter_by(
        user_id=user_id, leave_type_id=leave_type_id, year=year
    ).first()

    if existing:
        raise ValueError("Balance already exists for this user, leave type, and year.")

    new_balance = LeaveBalance(
        user_id=user_id,
        leave_type_id=leave_type_id,
        year=year,
        total_days=total_days,
        used_days=0
    )
    db.session.add(new_balance)
    db.session.commit()
    return new_balance


def create_new_department(name: str) -> Department:
    if db.session.query(Department).filter_by(name=name).first():
        raise ValueError("Department with this name already exists.")

    dept = Department(name=name)
    db.session.add(dept)
    db.session.commit()
    return dept


def assign_user_to_department(user_id: int, department_id: int | None) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found.")

    if department_id is not None:
        dept = db.session.get(Department, department_id)
        if not dept:
            raise ValueError("Department not found.")

    user.department_id = department_id
    db.session.commit()
    return user
