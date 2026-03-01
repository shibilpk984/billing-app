from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from weasyprint import HTML
import os
import hashlib

from .service import generate_invoice_html


STORAGE_DIR = "storage/invoices"


def generate_and_store_pdf(db: Session, tenant_id: int, order_id: int):

    html_content = generate_invoice_html(db, tenant_id, order_id)

    order = db.execute(
        text("""
        SELECT order_number
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
        raise HTTPException(status_code=404, detail="Completed order not found")

    order_number = order.order_number

    tenant_folder = f"{STORAGE_DIR}/{tenant_id}"
    os.makedirs(tenant_folder, exist_ok=True)

    file_path = f"{tenant_folder}/{order_number}.pdf"

    HTML(string=html_content).write_pdf(file_path)

    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    db.execute(
        text("""
        INSERT INTO invoices(
            tenant_id,
            order_id,
            file_path,
            file_hash
        )
        VALUES(
            :tenant_id,
            :order_id,
            :file_path,
            :file_hash
        )
        """),
        {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "file_path": file_path,
            "file_hash": file_hash
        }
    )

    db.commit()

    return {
        "status": "PDF generated",
        "file_path": file_path
    }