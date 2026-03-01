from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from app.modules.auth.security import hash_password


# ----------------------------------------
# LIST TENANTS WITH BASIC STATS
# ----------------------------------------
def list_tenants(db: Session):

    result = db.execute(text("""
        SELECT
            t.id,
            t.name,
            t.status,
            t.plan,
            t.created_at,

            (SELECT COUNT(*) FROM users u WHERE u.tenant_id = t.id) AS total_users,
            (SELECT COUNT(*) FROM orders o WHERE o.tenant_id = t.id) AS total_orders,
            (SELECT COUNT(*) FROM invoices i WHERE i.tenant_id = t.id) AS total_invoices

        FROM tenants t
        ORDER BY t.created_at DESC
    """))

    return [dict(row._mapping) for row in result]


# ----------------------------------------
# UPDATE TENANT STATUS (SOFT DELETE)
# ----------------------------------------
def update_tenant_status(db: Session, tenant_id: int, status: str):

    result = db.execute(
        text("SELECT id FROM tenants WHERE id = :id"),
        {"id": tenant_id}
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")

    db.execute(
        text("""
        UPDATE tenants
        SET status = :status,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id
        """),
        {"status": status, "id": tenant_id}
    )

    db.commit()

    return {"message": f"Tenant status updated to {status}"}


# ----------------------------------------
# RESET TENANT ADMIN PASSWORD
# ----------------------------------------
def reset_tenant_admin_password(
    db: Session,
    tenant_id: int,
    new_password: str
):
    hashed = hash_password(new_password)

    # Find tenant admin
    admin = db.execute(
        text("""
        SELECT id
        FROM users
        WHERE tenant_id = :tenant_id
        AND role = 'TENANT_ADMIN'
        LIMIT 1
        """),
        {"tenant_id": tenant_id}
    ).fetchone()

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Tenant admin not found"
        )

    db.execute(
        text("""
        UPDATE users
        SET password_hash = :password_hash,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id
        """),
        {
            "password_hash": hashed,
            "id": admin.id
        }
    )

    db.commit()

    return {"message": "Tenant admin password reset successful"}


# ----------------------------------------
# SYSTEM DASHBOARD STATS
# ----------------------------------------
def get_system_stats(db: Session):

    result = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM tenants) AS total_tenants,
            (SELECT COUNT(*) FROM tenants WHERE status = 'ACTIVE') AS active_tenants,
            (SELECT COUNT(*) FROM tenants WHERE status = 'SUSPENDED') AS suspended_tenants,
            (SELECT COUNT(*) FROM tenants WHERE status = 'DELETED') AS deleted_tenants,
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT COUNT(*) FROM orders) AS total_orders,
            (SELECT COUNT(*) FROM invoices) AS total_invoices
    """)).fetchone()

    return dict(result._mapping)