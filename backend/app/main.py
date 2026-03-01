from fastapi import FastAPI

from app.modules.auth.router import router as auth_router
from app.modules.items.router import router as items_router
from app.modules.orders.router import router as orders_router
from app.modules.print.router import router as print_router


app = FastAPI(
    title="Billing POS API",
    version="1.0.0"
)


@app.get("/")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(items_router)
app.include_router(orders_router)
app.include_router(print_router)