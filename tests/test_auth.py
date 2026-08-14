import pytest

from university.auth import (
    AuthError,
    Role,
    User,
    authenticate,
    hash_password,
    load_users,
    require,
    save_users,
)


@pytest.fixture
def users() -> dict[str, User]:
    return load_users(path="does-not-exist.json")


def test_password_is_not_stored_in_plaintext(users):
    admin = users["admin"]
    assert "admin123" not in (admin.password_hash, admin.salt)
    assert admin.verify("admin123")
    assert not admin.verify("wrong")


def test_same_password_gets_different_hashes():
    salt_a, hash_a = hash_password("hunter2")
    salt_b, hash_b = hash_password("hunter2")
    assert salt_a != salt_b and hash_a != hash_b


def test_authenticate_rejects_bad_credentials(users):
    assert authenticate("admin", "admin123", users).role is Role.ADMIN
    with pytest.raises(AuthError):
        authenticate("admin", "nope", users)
    with pytest.raises(AuthError):
        authenticate("ghost", "admin123", users)


def test_roles_have_distinct_permissions(users):
    require(users["admin"], "student:create")
    require(users["faculty"], "enrollment:create")

    with pytest.raises(AuthError, match="not allowed"):
        require(users["faculty"], "student:create")
    with pytest.raises(AuthError, match="not allowed"):
        require(users["student"], "enrollment:create")
    with pytest.raises(AuthError, match="Not signed in"):
        require(None, "data:view")


def test_users_round_trip_through_disk(tmp_path, users):
    path = tmp_path / "users.json"
    save_users(users, path)
    reloaded = load_users(path)
    assert reloaded["student"].role is Role.STUDENT
    assert reloaded["student"].verify("student123")
