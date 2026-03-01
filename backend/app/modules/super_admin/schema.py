from pydantic import BaseModel, Field
from typing import Literal


class UpdateTenantStatusRequest(BaseModel):
    status: Literal["ACTIVE", "SUSPENDED", "DELETED"]


class ResetPasswordRequest(BaseModel):
    tenant_id: int
    new_password: str = Field(..., min_length=4)