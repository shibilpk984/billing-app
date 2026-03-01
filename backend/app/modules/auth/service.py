from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


def create_super_admin(db: Session, username: str, password: str):
    hashed = hash_password(password)

    db.execute(
        text("""
        INSERT INTO users(tenant_id, username, password_hash, role)
        VALUES(NULL, :username, :password_hash, 'SUPER_ADMIN')
        """),
        {"username": username, "password_hash": hashed}
    )

    db.commit()


def create_tenant_with_admin(
    db: Session,
    name: str,
    business_type: str,
    admin_username: str,
    admin_password: str
):

    tenant_result = db.execute(
        text("""
        INSERT INTO tenants(name, business_type, status)
        VALUES(:name, :business_type, 'ACTIVE')
        RETURNING id
        """),
        {"name": name, "business_type": business_type}
    )

    tenant_id = tenant_result.fetchone()[0]

    hashed = hash_password(admin_password)

    db.execute(
        text("""
        INSERT INTO users(tenant_id, username, password_hash, role)
        VALUES(:tenant_id, :username, :password_hash, 'TENANT_ADMIN')
        """),
        {
            "tenant_id": tenant_id,
            "username": admin_username,
            "password_hash": hashed
        }
    )

    db.commit()

    return tenant_id


def authenticate_user(db: Session, username: str, password: str):

    result = db.execute(
        text("""
        SELECT u.id, u.tenant_id, u.password_hash, u.role, t.status
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.username = :username
        """),
        {"username": username}
    )

    user = result.fetchone()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # Block suspended tenant
    if user.tenant_id and user.status == "SUSPENDED":
        raise HTTPException(status_code=403, detail="Tenant account suspended")

    access_token = create_access_token({
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role
    })

    return access_token, refresh_token