from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from datetime import datetime


def format_invoice_datetime(dt: datetime) -> str:
    if not dt:
        return None
    return dt.strftime("%d %b %Y, %I:%M:%S %p")


def format_currency(amount: float) -> str:
    return f"₹{amount:.2f}"


def get_printable_invoice(db: Session, tenant_id: int, order_id: int):

    tenant = db.execute(
        text("""
        SELECT name, address, phone, invoice_footer
        FROM tenants
        WHERE id = :tenant_id
        """),
        {"tenant_id": tenant_id}
    ).fetchone()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    order = db.execute(
        text("""
        SELECT order_number, total_amount, created_at
        FROM orders
        WHERE id = :order_id
        AND tenant_id = :tenant_id
        AND status = 'COMPLETED'
        """),
        {
            "order_id": order_id,
            "tenant_id": tenant_id
        }
    ).fetchone()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not completed")

    items = db.execute(
        text("""
        SELECT
            item_name_snapshot,
            quantity,
            price_at_sale,
            total
        FROM order_items
        WHERE order_id = :order_id
        AND tenant_id = :tenant_id
        ORDER BY id
        """),
        {"order_id": order_id, "tenant_id": tenant_id}
    ).fetchall()

    return {
        "cafe": {
            "name": tenant.name,
            "address": tenant.address,
            "phone": tenant.phone,
            "footer": tenant.invoice_footer
        },
        "order": {
            "order_number": order.order_number,
            "created_at": format_invoice_datetime(order.created_at),
            "total": float(order.total_amount)
        },
        "items": [
            {
                "name": item.item_name_snapshot,
                "quantity": item.quantity,
                "price": float(item.price_at_sale),
                "total": float(item.total)
            }
            for item in items
        ]
    }


def generate_invoice_html(db: Session, tenant_id: int, order_id: int):

    data = get_printable_invoice(db, tenant_id, order_id)

    cafe = data["cafe"]
    order = data["order"]
    items = data["items"]

    items_html = ""

    for item in items:
        items_html += f"""
        <tr>
            <td class="col-name">{item['name']}</td>
            <td class="col-qty">{item['quantity']}</td>
            <td class="col-amount">{format_currency(item['total'])}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Invoice</title>
<style>
body {{
    width: 80mm;
    font-family: monospace;
    font-size: 12px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
.col-qty {{ text-align:center; }}
.col-amount {{ text-align:right; }}
.total-row td {{ font-weight:bold; }}
</style>
</head>
<body>

<h3 style="text-align:center;">{cafe['name']}</h3>
<hr>

Order: {order['order_number']}<br>
Date: {order['created_at']}
<hr>

<table>
<thead>
<tr>
<td>Item</td>
<td class="col-qty">Qty</td>
<td class="col-amount">Amount</td>
</tr>
</thead>
<tbody>
{items_html}
</tbody>
</table>

<hr>
<table>
<tr class="total-row">
<td>Total</td>
<td></td>
<td class="col-amount">{format_currency(order['total'])}</td>
</tr>
</table>

<hr>
<div style="text-align:center;">{cafe['footer']}</div>

</body>
</html>
"""

    return html