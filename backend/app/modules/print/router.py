from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db

from .service import (
    get_printable_invoice,
    generate_invoice_html
)

router = APIRouter(prefix="/print", tags=["print"])


# JSON invoice endpoint (SECURE — uses header)
@router.get("/{order_id}")
def get_print_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    try:

        return get_printable_invoice(
            db=db,
            tenant_id=x_tenant_id,
            order_id=order_id
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# HTML printable invoice endpoint (BROWSER-FRIENDLY)
# Uses query param instead of header
# Example: /print/1/html?tenant_id=1
@router.get("/{order_id}/html", response_class=HTMLResponse)
def get_print_invoice_html(
    order_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):

    try:

        html = generate_invoice_html(
            db=db,
            tenant_id=tenant_id,
            order_id=order_id
        )

        return HTMLResponse(content=html)

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )