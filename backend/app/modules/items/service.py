from sqlalchemy.orm import Session
from sqlalchemy import text


def create_item(
    db: Session,
    tenant_id: int,
    name: str,
    price: float,
    category: str = None,
    description: str = None,
    tags: list = None,
    image_url: str = None,
    display_order: int = 0
):

    result = db.execute(
        text("""
        INSERT INTO items(
            tenant_id,
            name,
            price,
            category,
            description,
            tags,
            image_url,
            display_order
        )
        VALUES(
            :tenant_id,
            :name,
            :price,
            :category,
            :description,
            :tags,
            :image_url,
            :display_order
        )
        RETURNING id
        """),
        {
            "tenant_id": tenant_id,
            "name": name,
            "price": price,
            "category": category,
            "description": description,
            "tags": tags,
            "image_url": image_url,
            "display_order": display_order
        }
    )

    item_id = result.fetchone()[0]

    db.commit()

    return item_id


def list_items(db: Session, tenant_id: int):

    result = db.execute(
        text("""
        SELECT *
        FROM items
        WHERE tenant_id = :tenant_id
        AND is_active = TRUE
        ORDER BY display_order, name
        """),
        {"tenant_id": tenant_id}
    )

    items = []

    for row in result.fetchall():

        items.append({
            "id": row.id,
            "name": row.name,
            "price": float(row.price),
            "category": row.category,
            "description": row.description,
            "tags": row.tags,
            "image_url": row.image_url,
            "display_order": row.display_order,
            "is_active": row.is_active
        })

    return items