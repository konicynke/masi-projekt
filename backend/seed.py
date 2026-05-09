from werkzeug.security import generate_password_hash
from app import create_app
from app.extension import db
from app.model.user import User, UserRole
from app.model.leave_type import LeaveType
from app.model.leave_balance import LeaveBalance

app = create_app()

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        vacation_leave = LeaveType(name="Vacation", requires_approval=True)
        on_demand_leave = LeaveType(name="On Demand", requires_approval=True)
        training_leave = LeaveType(name="Training", requires_approval=True)

        db.session.add_all([
            vacation_leave,
            on_demand_leave,
            training_leave
        ])
        db.session.commit()

        admin = User(
            email="admin@example.com",
            password_hash=generate_password_hash("password"),
            first_name="Jan",
            last_name="Kowalski",
            role=UserRole.ADMIN
        )

        manager = User(
            email="manager@example.com",
            password_hash=generate_password_hash("password"),
            first_name="Anna",
            last_name="Nowak",
            role=UserRole.MANAGER
        )

        db.session.add_all([admin, manager])
        db.session.commit()

        employee = User(
            email="employee@example.com",
            password_hash=generate_password_hash("password"),
            first_name="Piotr",
            last_name="Kowalski",
            role=UserRole.EMPLOYEE,
            manager_id=manager.id
        )

        db.session.add(employee)
        db.session.commit()

        vacation_leave_balance = LeaveBalance(
            year=2026,
            total_days=26,
            used_days=0,
            user_id=employee.id,
            leave_type_id=vacation_leave.id
        )

        db.session.add(vacation_leave_balance)
        db.session.commit()

        print("Seeding completed.")

if __name__ == "__main__":
    seed_data()