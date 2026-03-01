from sqlalchemy.orm import Session
from sqlalchemy import text
from .security import hash_password, verify_password, create_access_token


def create_tenant(db: Session, name: str, business_type: str):

    result = db.execute(
        text("""
        INSERT INTO tenants(name, business_type)
        VALUES(:name, :business_type)
        RETURNING id
        """),
        {"name": name, "business_type": business_type}
    )

    tenant_id = result.fetchone()[0]

    db.commit()

    return tenant_id


def create_user(db: Session, tenant_id: int, username: str, password: str, role: str):

    hashed = hash_password(password)

    result = db.execute(
        text("""
        INSERT INTO users(tenant_id, username, password_hash, role)
        VALUES(:tenant_id, :username, :password_hash, :role)
        RETURNING id
        """),
        {
            "tenant_id": tenant_id,
            "username": username,
            "password_hash": hashed,
            "role": role
        }
    )

    user_id = result.fetchone()[0]

    db.commit()

    return user_id


def authenticate_user(db: Session, username: str, password: str):

    result = db.execute(
        text("""
        SELECT id, tenant_id, password_hash
        FROM users
        WHERE username = :username
        """),
        {"username": username}
    )

    user = result.fetchone()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    token = create_access_token({
        "user_id": user.id,
        "tenant_id": user.tenant_id
    })

    return {
        "access_token": token,
        "tenant_id": user.tenant_id,
        "user_id": user.id
    }