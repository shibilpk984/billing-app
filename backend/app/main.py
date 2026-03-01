import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.modules.auth.router import router as auth_router
from app.modules.items.router import router as items_router
from app.modules.orders.router import router as orders_router
from app.modules.print.router import router as print_router
from app.modules.super_admin.router import router as super_admin_router


# --------------------------------------------------
# ENV CONFIG
# --------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ENV = os.getenv("ENV", "development")

# Allow multiple origins if needed (comma separated)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")


app = FastAPI(
    title="Billing POS API",
    version="2.0.0"
)


# --------------------------------------------------
# CORS CONFIG (JWT Cookie Support)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# TRUSTED HOSTS (Production Only)
# --------------------------------------------------
if ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )


# --------------------------------------------------
# STATIC FILES (Item Images + Invoice PDFs)
# --------------------------------------------------
# Ensure storage folder exists
os.makedirs("storage", exist_ok=True)

app.mount(
    "/storage",
    StaticFiles(directory="storage"),
    name="storage"
)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}


# --------------------------------------------------
# API ROUTES (Versioned)
# --------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(super_admin_router, prefix=API_PREFIX)
app.include_router(items_router, prefix=API_PREFIX)
app.include_router(orders_router, prefix=API_PREFIX)
app.include_router(print_router, prefix=API_PREFIX)