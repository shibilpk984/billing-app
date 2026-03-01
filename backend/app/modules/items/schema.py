from pydantic import BaseModel
from typing import Optional, List


class ItemCreate(BaseModel):

    name: str
    price: float

    category: Optional[str] = None
    description: Optional[str] = None

    tags: Optional[List[str]] = None

    image_url: Optional[str] = None

    display_order: Optional[int] = 0


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