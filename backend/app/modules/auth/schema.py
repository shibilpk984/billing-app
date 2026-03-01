from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    business_type: str = "cafe"


class UserCreate(BaseModel):
    tenant_id: int
    username: str
    password: str
    role: str = "admin"


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: int
    user_id: int