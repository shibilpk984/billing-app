from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
import uuid


def generate_order_number():
    return "ORD-" + uuid.uuid4().hex[:6].upper()


# ----------------------------------------
# CREATE DRAFT ORDER
# ----------------------------------------
def create_draft_order(db: Session, tenant_id: int, user_id: int):

    order_number = generate_order_number()

    result = db.execute(
        text("""
        INSERT INTO orders(
            tenant_id,
            order_number,
            status,
            total_amount,
            created_by
        )
        VALUES(
            :tenant_id,
            :order_number,
            'DRAFT',
            0,
            :created_by
        )
        RETURNING id, order_number, status, total_amount
        """),
        {
            "tenant_id": tenant_id,
            "order_number": order_number,
            "created_by": user_id
        }
    )

    order = result.fetchone()
    db.commit()

    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "total_amount": float(order.total_amount)
    }


# ----------------------------------------
# LIST DRAFT ORDERS
# ----------------------------------------
def list_draft_orders(db: Session, tenant_id: int):

    result = db.execute(
        text("""
        SELECT id, order_number, status, total_amount
        FROM orders
        WHERE tenant_id = :tenant_id
        AND status = 'DRAFT'
        ORDER BY created_at DESC
        """),
        {"tenant_id": tenant_id}
    )

    return [
        {
            "id": row.id,
            "order_number": row.order_number,
            "status": row.status,
            "total_amount": float(row.total_amount)
        }
        for row in result.fetchall()
    ]


# ----------------------------------------
# ADD ITEM TO ORDER
# ----------------------------------------
def add_item_to_order(db: Session, tenant_id: int, order_id: int, item_id: int, quantity: int):

    # Validate order ownership + draft status
    order = db.execute(
        text("""
        SELECT status
        FROM orders
        WHERE id = :order_id
        AND tenant_id = :tenant_id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    ).fetchone()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Cannot modify completed order")

    item = db.execute(
        text("""
        SELECT price, name
        FROM items
        WHERE id = :item_id
        AND tenant_id = :tenant_id
        AND is_active = TRUE
        """),
        {"item_id": item_id, "tenant_id": tenant_id}
    ).fetchone()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    price = float(item.price)
    total = price * quantity

    db.execute(
        text("""
        INSERT INTO order_items(
            tenant_id,
            order_id,
            item_id,
            item_name_snapshot,
            quantity,
            price_at_sale,
            total
        )
        VALUES(
            :tenant_id,
            :order_id,
            :item_id,
            :item_name,
            :quantity,
            :price,
            :total
        )
        """),
        {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "item_id": item_id,
            "item_name": item.name,
            "quantity": quantity,
            "price": price,
            "total": total
        }
    )

    # Update total
    db.execute(
        text("""
        UPDATE orders
        SET total_amount = (
            SELECT COALESCE(SUM(total), 0)
            FROM order_items
            WHERE order_id = :order_id
        ),
        updated_at = CURRENT_TIMESTAMP
        WHERE id = :order_id
        """),
        {"order_id": order_id}
    )

    db.commit()

    return {
        "status": "item added",
        "item": item.name,
        "quantity": quantity,
        "line_total": total
    }


# ----------------------------------------
# GET ORDER DETAILS
# ----------------------------------------
def get_order_details(db: Session, tenant_id: int, order_id: int):

    result = db.execute(
        text("""
        SELECT
            oi.item_id,
            oi.item_name_snapshot,
            oi.quantity,
            oi.price_at_sale,
            oi.total
        FROM order_items oi
        WHERE oi.order_id = :order_id
        AND oi.tenant_id = :tenant_id
        ORDER BY oi.id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    )

    return [
        {
            "item_id": row.item_id,
            "name": row.item_name_snapshot,
            "quantity": row.quantity,
            "price": float(row.price_at_sale),
            "total": float(row.total)
        }
        for row in result.fetchall()
    ]


# ----------------------------------------
# COMPLETE ORDER
# ----------------------------------------
def complete_order(db: Session, tenant_id: int, order_id: int):

    order = db.execute(
        text("""
        SELECT status
        FROM orders
        WHERE id = :order_id
        AND tenant_id = :tenant_id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    ).fetchone()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Order already completed")

    db.execute(
        text("""
        UPDATE orders
        SET status = 'COMPLETED',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :order_id
        """),
        {"order_id": order_id}
    )

    db.commit()

    return {"status": "completed", "order_id": order_id}


# ----------------------------------------
# ORDER SUMMARY
# ----------------------------------------
def get_completed_order_summary(db: Session, tenant_id: int, order_id: int):

    order = db.execute(
        text("""
        SELECT order_number, total_amount, status, created_at
        FROM orders
        WHERE id = :order_id
        AND tenant_id = :tenant_id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    ).fetchone()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = get_order_details(db, tenant_id, order_id)

    return {
        "order_number": order.order_number,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "created_at": str(order.created_at),
        "items": items
    }