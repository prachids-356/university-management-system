"""Authentication and role-based authorization.

Credentials are never stored in plaintext: a user record holds a PBKDF2-HMAC
hash plus its salt. Accounts are loaded from a JSON file (``users.json`` by
default) so real credentials stay out of version control; if that file is
absent, demo accounts are generated at runtime.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

PBKDF2_ITERATIONS = 240_000
DEFAULT_USERS_FILE = Path(
    os.environ.get("UMS_USERS_FILE", Path(__file__).resolve().parent.parent / "users.json")
)


class Role(str, Enum):
    ADMIN = "admin"
    FACULTY = "faculty"
    STUDENT = "student"


class AuthError(Exception):
    """Raised when authentication fails or a role lacks a permission."""


PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.ADMIN: frozenset(
        {
            "student:create",
            "faculty:create",
            "course:create",
            "enrollment:create",
            "assignment:create",
            "data:view",
        }
    ),
    Role.FACULTY: frozenset({"enrollment:create", "data:view"}),
    Role.STUDENT: frozenset({"data:view"}),
}


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Return ``(salt_hex, hash_hex)`` for ``password``."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return salt.hex(), digest.hex()


@dataclass(frozen=True)
class User:
    username: str
    role: Role
    salt: str
    password_hash: str

    def verify(self, password: str) -> bool:
        _, candidate = hash_password(password, bytes.fromhex(self.salt))
        return hmac.compare_digest(candidate, self.password_hash)

    def can(self, permission: str) -> bool:
        return permission in PERMISSIONS[self.role]


def _demo_users() -> dict[str, User]:
    """Development accounts, used only when no users file exists."""
    demo = {"admin": Role.ADMIN, "faculty": Role.FACULTY, "student": Role.STUDENT}
    users: dict[str, User] = {}
    for username, role in demo.items():
        salt, digest = hash_password(f"{username}123")
        users[username] = User(username, role, salt, digest)
    return users


def load_users(path: Path | None = None) -> dict[str, User]:
    """Load users from ``path``, falling back to demo accounts when it is absent."""
    path = Path(path or DEFAULT_USERS_FILE)
    if not path.exists():
        return _demo_users()
    raw = json.loads(path.read_text())
    return {
        username: User(
            username=username,
            role=Role(record["role"]),
            salt=record["salt"],
            password_hash=record["password_hash"],
        )
        for username, record in raw.items()
    }


def save_users(users: dict[str, User], path: Path | None = None) -> None:
    path = Path(path or DEFAULT_USERS_FILE)
    payload = {
        u.username: {"role": u.role.value, "salt": u.salt, "password_hash": u.password_hash}
        for u in users.values()
    }
    path.write_text(json.dumps(payload, indent=2))


def authenticate(username: str, password: str, users: dict[str, User]) -> User:
    """Return the matching :class:`User` or raise :class:`AuthError`."""
    user = users.get((username or "").strip())
    if user is None or not user.verify(password or ""):
        raise AuthError("Invalid credentials.")
    return user


def require(user: User | None, permission: str) -> None:
    """Raise :class:`AuthError` unless ``user`` holds ``permission``."""
    if user is None:
        raise AuthError("Not signed in.")
    if not user.can(permission):
        raise AuthError(f"Role '{user.role.value}' is not allowed to perform this action.")
