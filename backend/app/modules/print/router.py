from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import require_tenant_user

from .service import (
    get_printable_invoice,
    generate_invoice_html
)
from .pdf_service import generate_and_store_pdf

router = APIRouter(prefix="/print", tags=["print"])


# ----------------------------------------
# JSON Invoice (Secure)
# ----------------------------------------
@router.get("/{order_id}")
def get_print_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):
    tenant_id = user.get("tenant_id")

    return get_printable_invoice(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id
    )


# ----------------------------------------
# HTML Invoice (Secure)
# ----------------------------------------
@router.get("/{order_id}/html", response_class=HTMLResponse)
def get_print_invoice_html(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):
    tenant_id = user.get("tenant_id")

    html = generate_invoice_html(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id
    )

    return HTMLResponse(content=html)


# ----------------------------------------
# Generate PDF
# ----------------------------------------
@router.post("/{order_id}/pdf")
def generate_pdf(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):
    tenant_id = user.get("tenant_id")

    return generate_and_store_pdf(
        db=db,
        tenant_id=tenant_id,
        order_id=order_id
    )


# ----------------------------------------
# Download Latest PDF
# ----------------------------------------
@router.get("/{order_id}/download")
def download_pdf(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    from sqlalchemy import text

    tenant_id = user.get("tenant_id")

    invoice = db.execute(
        text("""
        SELECT file_path
        FROM invoices
        WHERE tenant_id = :tenant_id
        AND order_id = :order_id
        ORDER BY created_at DESC
        LIMIT 1
        """),
        {
            "tenant_id": tenant_id,
            "order_id": order_id
        }
    ).fetchone()

    if not invoice:
        raise HTTPException(status_code=404, detail="PDF not found")

    file_path = invoice.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path)
    )