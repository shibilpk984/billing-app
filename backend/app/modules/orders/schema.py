from pydantic import BaseModel, Field
from typing import Optional, List


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float


class AddItemRequest(BaseModel):
    order_id: int
    item_id: int
    quantity: int = Field(..., gt=0)