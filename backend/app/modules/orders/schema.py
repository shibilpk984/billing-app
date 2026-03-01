from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):

    # optional label for UI (example: Table 1, Takeaway, etc.)
    note: Optional[str] = None


class OrderResponse(BaseModel):

    id: int
    order_number: str
    status: str
    total_amount: float


# ADD THIS NEW CLASS BELOW
class AddItemRequest(BaseModel):

    order_id: int
    item_id: int
    quantity: int