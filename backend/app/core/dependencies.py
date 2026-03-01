from fastapi import Request, Depends, HTTPException, status
from app.modules.auth.security import decode_token


def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = decode_token(token)

    # Ensure this is access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return payload


def require_super_admin(user=Depends(get_current_user)):
    if user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return user


def require_tenant_user(user=Depends(get_current_user)):
    if user.get("role") not in ["TENANT_ADMIN", "CASHIER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access required"
        )
    return user


def require_tenant_admin(user=Depends(get_current_user)):
    if user.get("role") != "TENANT_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin required"
        )
    return user