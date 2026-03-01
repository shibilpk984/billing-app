from pydantic import BaseModel, Field
from typing import Literal


# -----------------------------
# LOGIN
# -----------------------------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)


# -----------------------------
# SUPER ADMIN: CREATE TENANT
# -----------------------------
class TenantCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    business_type: str = "cafe"
    admin_username: str = Field(..., min_length=3)
    admin_password: str = Field(..., min_length=4)


# -----------------------------
# SUPER ADMIN: RESET PASSWORD
# -----------------------------
class ResetPasswordRequest(BaseModel):
    user_id: int
    new_password: str = Field(..., min_length=4)


# -----------------------------
# SUPER ADMIN: UPDATE TENANT STATUS
# -----------------------------
class UpdateTenantStatusRequest(BaseModel):
    status: Literal["ACTIVE", "SUSPENDED"]