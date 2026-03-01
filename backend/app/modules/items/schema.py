from pydantic import BaseModel, Field
from typing import Optional, List


# ----------------------------------------
# CREATE ITEM
# ----------------------------------------
class ItemCreate(BaseModel):

    name: str = Field(..., min_length=1, max_length=150)
    price: float = Field(..., ge=0)

    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    tags: Optional[List[str]] = None

    image_url: Optional[str] = None

    display_order: Optional[int] = Field(0, ge=0)


# ----------------------------------------
# UPDATE ITEM
# ----------------------------------------
class ItemUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    price: Optional[float] = Field(None, ge=0)

    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)

    is_active: Optional[bool] = None


# ----------------------------------------
# RESPONSE MODEL
# ----------------------------------------
class ItemResponse(BaseModel):

    id: int
    name: str
    price: float

    category: Optional[str]
    description: Optional[str]

    tags: Optional[List[str]]

    image_url: Optional[str]

    display_order: int

    is_active: bool

    class Config:
        from_attributes = True