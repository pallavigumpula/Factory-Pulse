import pytest
from fastapi import HTTPException
from backend.app.schemas.user import LoginRequest
from backend.app.routers.auth import login, get_current_user_profile
from backend.app.routers.users import list_users
from backend.app.dependencies import require_role

def test_login_success(db):
    req = LoginRequest(username="admin", password="admin123")
    res = login(req, db=db)
    assert res.access_token is not None
    assert res.user.username == "admin"
    assert res.user.role == "ADMIN"

def test_login_invalid_password(db):
    req = LoginRequest(username="admin", password="wrongpassword")
    with pytest.raises(HTTPException) as excinfo:
        login(req, db=db)
    assert excinfo.value.status_code == 401

def test_get_current_user_profile(admin_user):
    profile = get_current_user_profile(current_user=admin_user)
    assert profile.username == "admin"
    assert profile.role == "ADMIN"

def test_rbac_admin_allowed_users_management(db, admin_user):
    users = list_users(skip=0, limit=10, db=db, admin=admin_user)
    assert len(users) >= 5

def test_rbac_role_checker_enforces_permissions(operator_user):
    admin_checker = require_role("ADMIN")
    with pytest.raises(HTTPException) as excinfo:
        admin_checker(current_user=operator_user)
    assert excinfo.value.status_code == 403
