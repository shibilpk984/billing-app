-- =========================
-- TENANTS TABLE (UPDATED FOR INVOICES)
-- =========================
CREATE TABLE tenants (

    id SERIAL PRIMARY KEY,

    name VARCHAR(150) NOT NULL,

    business_type VARCHAR(100) DEFAULT 'cafe',

    address TEXT,

    phone VARCHAR(50),

    invoice_footer TEXT DEFAULT 'Thank you! Visit again.',

    logo_url TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE users (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    username VARCHAR(100) NOT NULL,

    password_hash TEXT NOT NULL,

    role VARCHAR(50) NOT NULL DEFAULT 'cashier',

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_per_tenant UNIQUE (tenant_id, username)
);


-- =========================
-- ITEMS TABLE
-- =========================
CREATE TABLE items (

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

CREATE INDEX idx_items_tenant ON items(tenant_id);
CREATE INDEX idx_items_category ON items(category);


-- =========================
-- ORDERS TABLE
-- =========================
CREATE TABLE orders (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_number VARCHAR(50) NOT NULL,

    status VARCHAR(20) NOT NULL CHECK (
        status IN ('DRAFT', 'COMPLETED', 'CANCELLED')
    ),

    total_amount NUMERIC(12,2) DEFAULT 0,

    created_by INTEGER REFERENCES users(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_tenant ON orders(tenant_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);


-- =========================
-- ORDER ITEMS TABLE
-- =========================
CREATE TABLE order_items (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,

    item_id INTEGER NOT NULL REFERENCES items(id),

    quantity INTEGER NOT NULL CHECK (quantity > 0),

    price_at_sale NUMERIC(10,2) NOT NULL,

    total NUMERIC(12,2) NOT NULL
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_tenant ON order_items(tenant_id);


-- =========================
-- INVOICES TABLE (PDF STORAGE)
-- =========================
CREATE TABLE invoices (

    id SERIAL PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,

    file_path TEXT NOT NULL,

    file_hash TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_order ON invoices(order_id);