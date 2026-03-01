from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid


def generate_order_number():
    return "ORD-" + uuid.uuid4().hex[:6].upper()


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


def add_item_to_order(db: Session, tenant_id: int, order_id: int, item_id: int, quantity: int):

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
        raise Exception("Item not found")

    price = float(item.price)
    total = price * quantity

    db.execute(
        text("""
        INSERT INTO order_items(
            tenant_id,
            order_id,
            item_id,
            quantity,
            price_at_sale,
            total
        )
        VALUES(
            :tenant_id,
            :order_id,
            :item_id,
            :quantity,
            :price,
            :total
        )
        """),
        {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "item_id": item_id,
            "quantity": quantity,
            "price": price,
            "total": total
        }
    )

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


def get_order_details(db: Session, tenant_id: int, order_id: int):

    result = db.execute(
        text("""
        SELECT
            oi.item_id,
            i.name,
            oi.quantity,
            oi.price_at_sale,
            oi.total
        FROM order_items oi
        JOIN items i ON i.id = oi.item_id
        WHERE oi.order_id = :order_id
        AND oi.tenant_id = :tenant_id
        ORDER BY oi.id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    )

    return [
        {
            "item_id": row.item_id,
            "name": row.name,
            "quantity": row.quantity,
            "price": float(row.price_at_sale),
            "total": float(row.total)
        }
        for row in result.fetchall()
    ]


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
        raise Exception("Order not found")

    if order.status != "DRAFT":
        raise Exception("Order already completed")

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


# NEW — FULL BILL SUMMARY
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
        raise Exception("Order not found")

    items = get_order_details(db, tenant_id, order_id)

    return {
        "order_number": order.order_number,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "created_at": str(order.created_at),
        "items": items
    }