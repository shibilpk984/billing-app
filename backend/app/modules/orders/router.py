from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_tenant_user

from .schema import AddItemRequest, OrderResponse
from .service import (
    create_draft_order,
    list_draft_orders,
    add_item_to_order,
    get_order_details,
    complete_order,
    get_completed_order_summary
)

router = APIRouter(prefix="/orders", tags=["orders"])


# ----------------------------------------
# CREATE DRAFT ORDER
# ----------------------------------------
@router.post("/draft", response_model=OrderResponse)
def create_draft_order_route(
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")
    user_id = user.get("user_id")

    return create_draft_order(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id
    )


# ----------------------------------------
# LIST DRAFT ORDERS
# ----------------------------------------
@router.get("/draft", response_model=List[OrderResponse])
def list_draft_orders_route(
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")
    return list_draft_orders(db=db, tenant_id=tenant_id)


# ----------------------------------------
# ADD ITEM TO ORDER
# ----------------------------------------
@router.post("/add-item")
def add_item_to_order_route(
    data: AddItemRequest,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")

    return add_item_to_order(
        db=db,
        tenant_id=tenant_id,
        order_id=data.order_id,
        item_id=data.item_id,
        quantity=data.quantity
    )


# ----------------------------------------
# GET ORDER DETAILS
# ----------------------------------------
@router.get("/{order_id}")
def get_order_details_route(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")
    return get_order_details(db=db, tenant_id=tenant_id, order_id=order_id)


# ----------------------------------------
# COMPLETE ORDER
# ----------------------------------------
@router.post("/{order_id}/complete")
def complete_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")

    return complete_order(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id
    )


# ----------------------------------------
# FULL ORDER SUMMARY
# ----------------------------------------
@router.get("/{order_id}/summary")
def get_order_summary_route(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")

    return get_completed_order_summary(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id
    )