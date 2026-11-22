"""
In-memory user store for MVP.
Replace with a real database (SQLAlchemy + PostgreSQL) in a later milestone.
"""
import bcrypt
from models.schemas import UserRole


def _hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _verify(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)


# Seed users built lazily to avoid import-time hashing cost
def _make_seed() -> dict[str, dict]:
    return {
        "customer@example.com": {
            "id": 1,
            "name": "Rahul Kumar",
            "hashed_password": _hash("customer123"),
            "role": UserRole.customer,
        },
        "company@example.com": {
            "id": 2,
            "name": "GreenScrap Co.",
            "hashed_password": _hash("company123"),
            "role": UserRole.company,
        },
    }


_users: dict[str, dict] = _make_seed()
_next_id = 3


def get_user(email: str) -> dict | None:
    return _users.get(email)


def create_user(name: str, email: str, password: str, role: UserRole) -> dict:
    global _next_id
    if email in _users:
        raise ValueError("Email already registered")
    record = {
        "id": _next_id,
        "name": name,
        "hashed_password": _hash(password),
        "role": role,
    }
    _users[email] = record
    _next_id += 1
    return record


def verify_password(plain: str, hashed: bytes) -> bool:
    return _verify(plain, hashed)
