from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from .schema import TenantCreate, UserCreate, LoginRequest
from .service import create_tenant, create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/tenant")
def create_tenant_route(data: TenantCreate, db: Session = Depends(get_db)):

    tenant_id = create_tenant(db, data.name, data.business_type)

    return {"tenant_id": tenant_id}


@router.post("/register")
def register_user(data: UserCreate, db: Session = Depends(get_db)):

    user_id = create_user(
        db,
        data.tenant_id,
        data.username,
        data.password,
        data.role
    )

    return {"user_id": user_id}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    result = authenticate_user(db, data.username, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result