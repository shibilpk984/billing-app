from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from .schema import AddItemRequest
from .service import (
    create_draft_order,
    list_draft_orders,
    add_item_to_order,
    get_order_details,
    complete_order,
    get_completed_order_summary
)

router = APIRouter(prefix="/orders", tags=["orders"])


# Create draft order
@router.post("/draft")
def create_draft_order_route(
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...),
    x_user_id: int = Header(...)
):

    return create_draft_order(
        db=db,
        tenant_id=x_tenant_id,
        user_id=x_user_id
    )


# List draft orders
@router.get("/draft")
def list_draft_orders_route(
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    return list_draft_orders(
        db=db,
        tenant_id=x_tenant_id
    )


# Add item to order
@router.post("/add-item")
def add_item_to_order_route(
    data: AddItemRequest,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    try:

        return add_item_to_order(
            db=db,
            tenant_id=x_tenant_id,
            order_id=data.order_id,
            item_id=data.item_id,
            quantity=data.quantity
        )

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))


# Get items inside order (raw view)
@router.get("/{order_id}")
def get_order_details_route(
    order_id: int,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    return get_order_details(
        db=db,
        tenant_id=x_tenant_id,
        order_id=order_id
    )


# Complete order
@router.post("/{order_id}/complete")
def complete_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    try:

        return complete_order(
            db=db,
            tenant_id=x_tenant_id,
            order_id=order_id
        )

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))


# FULL BILL SUMMARY (invoice data)
@router.get("/{order_id}/summary")
def get_order_summary_route(
    order_id: int,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    try:

        return get_completed_order_summary(
            db=db,
            tenant_id=x_tenant_id,
            order_id=order_id
        )

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))