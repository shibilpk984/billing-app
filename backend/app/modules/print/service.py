from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime


# Format datetime for invoice display
def format_invoice_datetime(dt: datetime) -> str:

    if not dt:
        return None

    return dt.strftime("%d %b %Y, %I:%M:%S %p")


# Format currency in Indian Rupees
def format_currency(amount: float) -> str:

    return f"₹{amount:.2f}"


# JSON invoice data
def get_printable_invoice(
    db: Session,
    tenant_id: int,
    order_id: int
):

    tenant = db.execute(
        text("""
        SELECT name, address, phone, invoice_footer
        FROM tenants
        WHERE id = :tenant_id
        """),
        {"tenant_id": tenant_id}
    ).fetchone()

    if not tenant:
        raise Exception("Tenant not found")

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
        raise Exception("Order not found or not completed")

    items = db.execute(
        text("""
        SELECT
            i.name,
            oi.quantity,
            oi.price_at_sale,
            oi.total
        FROM order_items oi
        JOIN items i ON i.id = oi.item_id
        WHERE oi.order_id = :order_id
        ORDER BY oi.id
        """),
        {"order_id": order_id}
    ).fetchall()

    item_list = []

    for item in items:

        item_list.append({
            "name": item.name,
            "quantity": item.quantity,
            "price": float(item.price_at_sale),
            "total": float(item.total)
        })

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

        "items": item_list
    }


# HTML invoice generator — ENTERPRISE THERMAL VERSION
def generate_invoice_html(
    db: Session,
    tenant_id: int,
    order_id: int
):

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

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Invoice</title>

<script>
window.onload = function() {{
    window.print();
}};
</script>

<style>

html, body {{
    width: 80mm;
    max-width: 80mm;
    margin: 0;
    padding: 3mm;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.4;
}}

.center {{
    text-align: center;
}}

h3 {{
    margin: 2px 0 6px 0;
}}

hr {{
    border: none;
    border-top: 1px dashed black;
    margin: 6px 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

thead td {{
    font-weight: bold;
}}

td {{
    padding: 2px 0;
}}

.col-name {{
    width: 50%;
}}

.col-qty {{
    width: 20%;
    text-align: center;
}}

.col-amount {{
    width: 30%;
    text-align: right;
}}

.total-row td {{
    font-weight: bold;
    font-size: 14px;
}}

.footer {{
    text-align: center;
    margin-top: 8px;
}}

@media print {{

    html, body {{
        width: 80mm;
        margin: 0;
        padding: 2mm;
    }}

    @page {{
        size: 80mm auto;
        margin: 0;
    }}
}}

</style>

</head>

<body>

<div class="center">
<h3>{cafe['name']}</h3>
</div>

<hr>

<div>
Order: {order['order_number']}<br>
Date: {order['created_at']}
</div>

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

<div class="footer">
{cafe['footer']}
</div>

</body>
</html>
"""

    return html