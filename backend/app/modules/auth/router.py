from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import require_super_admin, get_current_user
from .schema import LoginRequest, TenantCreateRequest
from .service import authenticate_user, create_tenant_with_admin
from .security import (
    decode_token,
    create_access_token,
    create_refresh_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


# --------------------------------------------------
# ENV CONFIG
# --------------------------------------------------
ENV = os.getenv("ENV", "development")
SECURE_COOKIE = True if ENV == "production" else False


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    tokens = authenticate_user(db, data.username, data.password)

    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, refresh_token = tokens

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite="lax"
    )

    return {"message": "Login successful"}


# --------------------------------------------------
# GET CURRENT USER
# --------------------------------------------------
@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "user_id": user.get("user_id"),
        "tenant_id": user.get("tenant_id"),
        "role": user.get("role")
    }


# --------------------------------------------------
# REFRESH TOKEN
# --------------------------------------------------
@router.post("/refresh")
def refresh_token(request: Request, response: Response):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({
        "user_id": payload["user_id"],
        "tenant_id": payload["tenant_id"],
        "role": payload["role"]
    })

    new_refresh = create_refresh_token({
        "user_id": payload["user_id"],
        "tenant_id": payload["tenant_id"],
        "role": payload["role"]
    })

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite="lax"
    )

    return {"message": "Token refreshed"}


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@router.post("/logout")
def logout(response: Response):

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}


# --------------------------------------------------
# SUPER ADMIN → CREATE TENANT
# --------------------------------------------------
@router.post("/tenant", status_code=status.HTTP_201_CREATED)
def create_tenant(
    data: TenantCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_super_admin)
):

    tenant_id = create_tenant_with_admin(
        db,
        data.name,
        data.business_type,
        data.admin_username,
        data.admin_password
    )

    return {"tenant_id": tenant_id}