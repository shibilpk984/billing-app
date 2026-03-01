from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import imghdr

from app.core.database import get_db
from app.core.dependencies import require_tenant_user, require_tenant_admin

from .schema import ItemCreate, ItemResponse
from .service import create_item, list_items

router = APIRouter(prefix="/items", tags=["items"])


# -------------------------------------------------
# CREATE ITEM (Tenant Admin Only)
# -------------------------------------------------
@router.post("", response_model=dict)
def create_item_route(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_tenant_admin)
):

    tenant_id = user.get("tenant_id")

    item_id = create_item(
        db=db,
        tenant_id=tenant_id,
        name=data.name,
        price=data.price,
        category=data.category,
        description=data.description,
        tags=data.tags,
        image_url=data.image_url,
        display_order=data.display_order
    )

    return {"item_id": item_id}


# -------------------------------------------------
# LIST ITEMS (Tenant Users)
# -------------------------------------------------
@router.get("", response_model=List[ItemResponse])
def list_items_route(
    db: Session = Depends(get_db),
    user=Depends(require_tenant_user)
):

    tenant_id = user.get("tenant_id")
    return list_items(db=db, tenant_id=tenant_id)


# -------------------------------------------------
# IMAGE UPLOAD (Tenant Admin Only)
# -------------------------------------------------
@router.post("/upload-image")
async def upload_item_image(
    file: UploadFile = File(...),
    user=Depends(require_tenant_admin)
):

    tenant_id = user.get("tenant_id")

    # Limit 2MB
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    # Validate real image type
    image_type = imghdr.what(None, contents)
    if image_type not in ["jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP allowed")

    folder_path = f"storage/items/{tenant_id}"
    os.makedirs(folder_path, exist_ok=True)

    filename = f"{uuid.uuid4()}.{image_type}"
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "image_url": f"/storage/items/{tenant_id}/{filename}"
    }