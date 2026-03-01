from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from .schema import ItemCreate
from .service import create_item, list_items

router = APIRouter(prefix="/items", tags=["items"])


# Create item
@router.post("")
def create_item_route(
    data: ItemCreate,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    item_id = create_item(
        db=db,
        tenant_id=x_tenant_id,
        name=data.name,
        price=data.price,
        category=data.category,
        description=data.description,
        tags=data.tags,
        image_url=data.image_url,
        display_order=data.display_order
    )

    return {"item_id": item_id}


# List items
@router.get("")
def list_items_route(
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(...)
):

    items = list_items(
        db=db,
        tenant_id=x_tenant_id
    )

    return items