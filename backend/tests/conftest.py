import os
import sys

# Add backend/ to path so `import app` resolves correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide defaults before create_app() calls load_dotenv(), so the real .env
# file does not bleed into the test run.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_PORT", "25")
os.environ.setdefault("MAIL_USE_TLS", "False")
os.environ.setdefault("MAIL_USERNAME", "")
os.environ.setdefault("MAIL_PASSWORD", "")
os.environ.setdefault("MAIL_DEFAULT_SENDER", "test@test.pl")

import pytest
from datetime import date
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app import create_app
from app.extension import db as _db
from app.model.user import User, UserRole
from app.model.leave_type import LeaveType
from app.model.leave_balance import LeaveBalance
from app.model.leave_request import LeaveRequest, LeaveRequestStatus


# ── application fixture (session scope = one DB for all tests) ────────────────

@pytest.fixture(scope="session")
def app():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        },
        "JWT_SECRET_KEY": "test-secret-key",
        "MAIL_SUPPRESS_SEND": True,
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# ── isolation: wipe all rows after every test ─────────────────────────────────

@pytest.fixture(autouse=True)
def clear_tables(app):
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


# ── suppress e-mail sending for every test ────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr(
        "app.service.leave_service.send_status_update_email",
        lambda *args, **kwargs: None,
    )


# ── JWT helpers ───────────────────────────────────────────────────────────────

def make_token(app, user_id: int, role: str) -> str:
    with app.app_context():
        return create_access_token(
            identity=str(user_id),
            additional_claims={"role": role},
        )


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── data factories ─────────────────────────────────────────────────────────────

def make_user(
    app,
    email: str = "user@test.pl",
    password: str = "haslo123",
    first_name: str = "Jan",
    last_name: str = "Kowalski",
    role: UserRole = UserRole.EMPLOYEE,
    manager_id: int | None = None,
    department_id: int | None = None,
) -> int:
    with app.app_context():
        u = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            manager_id=manager_id,
            department_id=department_id,
        )
        _db.session.add(u)
        _db.session.commit()
        return u.id


def make_leave_type(
    app,
    name: str = "Urlop wypoczynkowy",
    requires_approval: bool = True,
) -> int:
    with app.app_context():
        lt = LeaveType(name=name, requires_approval=requires_approval)
        _db.session.add(lt)
        _db.session.commit()
        return lt.id


def make_balance(
    app,
    user_id: int,
    leave_type_id: int,
    year: int = 2026,
    total_days: int = 26,
    used_days: int = 0,
) -> int:
    with app.app_context():
        b = LeaveBalance(
            user_id=user_id,
            leave_type_id=leave_type_id,
            year=year,
            total_days=total_days,
            used_days=used_days,
        )
        _db.session.add(b)
        _db.session.commit()
        return b.id


def make_leave_request(
    app,
    user_id: int,
    leave_type_id: int,
    start: str = "2026-08-01",
    end: str = "2026-08-05",
    status: LeaveRequestStatus = LeaveRequestStatus.PENDING,
) -> int:
    with app.app_context():
        lr = LeaveRequest(
            user_id=user_id,
            leave_type_id=leave_type_id,
            start_date=date.fromisoformat(start),
            end_date=date.fromisoformat(end),
            status=status,
        )
        _db.session.add(lr)
        _db.session.commit()
        return lr.id
