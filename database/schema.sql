-- =========================================
-- TENANTS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS tenants (

    id SERIAL PRIMARY KEY,

    name VARCHAR(150) NOT NULL,

    business_type VARCHAR(100) DEFAULT 'cafe',

    address TEXT,

    phone VARCHAR(50),

    invoice_footer TEXT DEFAULT 'Thank you! Visit again.',

    logo_url TEXT,

    currency VARCHAR(10) DEFAULT 'INR',

    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',

    -- SaaS Controls
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'SUSPENDED', 'DELETED')),

    plan VARCHAR(50) NOT NULL DEFAULT 'FREE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_plan ON tenants(plan);



-- =========================================
-- USERS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS users (

    id SERIAL PRIMARY KEY,

    -- NULL allowed only for SUPER_ADMIN
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,

    username VARCHAR(100) NOT NULL,

    password_hash TEXT NOT NULL,

    role VARCHAR(50) NOT NULL
        CHECK (role IN ('SUPER_ADMIN', 'TENANT_ADMIN', 'CASHIER')),

    is_active BOOLEAN DEFAULT TRUE,

    last_login TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique per tenant (allows same username in different tenants)
    CONSTRAINT unique_user_per_tenant UNIQUE (tenant_id, username)
);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);



-- =========================================
-- ITEMS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS items (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(150) NOT NULL,

    description TEXT,

    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),

    category VARCHAR(100),

    tags TEXT[],

    image_url TEXT,

    display_order INTEGER DEFAULT 0,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_tenant ON items(tenant_id);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_active ON items(is_active);



-- =========================================
-- ORDERS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS orders (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_number VARCHAR(50) NOT NULL,

    status VARCHAR(20) NOT NULL CHECK (
        status IN ('DRAFT', 'COMPLETED', 'CANCELLED')
    ),

    subtotal NUMERIC(12,2) DEFAULT 0,
    tax NUMERIC(12,2) DEFAULT 0,
    discount NUMERIC(12,2) DEFAULT 0,
    total_amount NUMERIC(12,2) DEFAULT 0,

    created_by INTEGER REFERENCES users(id),

    completed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_order_per_tenant UNIQUE (tenant_id, order_number)
);

CREATE INDEX IF NOT EXISTS idx_orders_tenant ON orders(tenant_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);



-- =========================================
-- ORDER ITEMS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS order_items (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,

    item_id INTEGER NOT NULL REFERENCES items(id),

    item_name_snapshot VARCHAR(150),

    quantity INTEGER NOT NULL CHECK (quantity > 0),

    price_at_sale NUMERIC(10,2) NOT NULL,

    total NUMERIC(12,2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_tenant ON order_items(tenant_id);



-- =========================================
-- INVOICES TABLE (PDF STORAGE)
-- =========================================
CREATE TABLE IF NOT EXISTS invoices (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,

    invoice_number VARCHAR(50),

    file_path TEXT NOT NULL,

    file_hash TEXT,

    file_size INTEGER,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_order ON invoices(order_id);
CREATE INDEX IF NOT EXISTS idx_invoices_generated ON invoices(generated_at);