from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_super_admin

from .schema import UpdateTenantStatusRequest, ResetPasswordRequest
from .service import (
    list_tenants,
    update_tenant_status,
    reset_tenant_admin_password,
    get_system_stats
)

router = APIRouter(
    prefix="/super-admin",
    tags=["super-admin"]
)


# ----------------------------------------
# LIST TENANTS
# ----------------------------------------
@router.get("/tenants")
def get_tenants(
    db: Session = Depends(get_db),
    user=Depends(require_super_admin)
):
    return list_tenants(db)


# ----------------------------------------
# UPDATE TENANT STATUS
# ----------------------------------------
@router.patch("/tenants/{tenant_id}/status")
def change_tenant_status(
    tenant_id: int,
    data: UpdateTenantStatusRequest,
    db: Session = Depends(get_db),
    user=Depends(require_super_admin)
):
    return update_tenant_status(db, tenant_id, data.status)


# ----------------------------------------
# RESET TENANT ADMIN PASSWORD
# ----------------------------------------
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    user=Depends(require_super_admin)
):
    return reset_tenant_admin_password(
        db,
        data.tenant_id,
        data.new_password
    )


# ----------------------------------------
# SYSTEM STATS
# ----------------------------------------
@router.get("/stats")
def system_stats(
    db: Session = Depends(get_db),
    user=Depends(require_super_admin)
):
    return get_system_stats(db)