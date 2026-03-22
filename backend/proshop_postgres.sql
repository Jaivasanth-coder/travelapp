-- ============================================================
--  ProShop — PostgreSQL Schema
--  Works for both LOCAL and PRODUCTION (Render / Railway / Supabase)
--  Run this file once to bootstrap either database.
-- ============================================================

-- ── 0. EXTENSIONS ────────────────────────────────────────────
-- pgcrypto: used for password hashing (gen_salt, crypt)
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ── 1. USERS (customers) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    phone           VARCHAR(15)  NOT NULL UNIQUE,          -- 10-digit mobile
    password_hash   TEXT         NOT NULL,                  -- bcrypt via pgcrypto
    role            VARCHAR(20)  NOT NULL DEFAULT 'customer',
    -- saved delivery info (pre-filled at checkout)
    apartment       VARCHAR(200),
    address         TEXT,
    pincode         VARCHAR(10),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);


-- ── 2. ADMIN USERS ───────────────────────────────────────────
-- Kept separate so you can have multiple admins with usernames
CREATE TABLE IF NOT EXISTS admins (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    password_hash   TEXT         NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Default admin: username=admin / password=admin123
-- Password is bcrypt-hashed. Re-hash if you change it.
INSERT INTO admins (username, password_hash)
VALUES (
    'admin',
    crypt('admin123', gen_salt('bf', 10))
)
ON CONFLICT (username) DO NOTHING;


-- ── 3. OTP STORE ─────────────────────────────────────────────
-- Temporary OTPs; expired rows cleaned up by your backend.
CREATE TABLE IF NOT EXISTS otp_store (
    id          SERIAL PRIMARY KEY,
    phone       VARCHAR(15)  NOT NULL,
    otp         VARCHAR(10)  NOT NULL,
    expires_at  TIMESTAMPTZ  NOT NULL DEFAULT (NOW() + INTERVAL '10 minutes'),
    used        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_otp_phone       ON otp_store(phone);
CREATE INDEX IF NOT EXISTS idx_otp_expires_at  ON otp_store(expires_at);


-- ── 4. PRODUCTS ──────────────────────────────────────────────
-- Categories are derived from description prefix in the frontend
-- (AnyTime | Groceries | Pickles) — keep same convention.
CREATE TABLE IF NOT EXISTS products (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,                                   -- contains category prefix
    price           NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock           INTEGER       NOT NULL DEFAULT 0 CHECK (stock >= 0),
    max_qty         INTEGER       NOT NULL DEFAULT 10 CHECK (max_qty >= 1),
    delivery_fee    NUMERIC(10,2) NOT NULL DEFAULT 40 CHECK (delivery_fee >= 0),
    image_url       TEXT,
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,    -- soft-delete / hide
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

-- ── Sample seed products (optional — delete if not needed) ───
INSERT INTO products (name, description, price, stock, max_qty, delivery_fee, image_url)
VALUES
  ('Veg Sandwich',      'AnyTime | Fresh veg sandwich',          60,  50, 10, 0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400'),
  ('Poha',              'AnyTime | Light breakfast poha',        40,  30, 5,  0,  'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400'),
  ('Basmati Rice 1kg',  'Groceries | Premium basmati rice 1kg',  120, 20, 3,  40, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400'),
  ('Toor Dal 500g',     'Groceries | Toor dal 500g pack',        80,  25, 5,  40, 'https://images.unsplash.com/photo-1612257416648-8b7f2a7c4b9e?w=400'),
  ('Mango Pickle 300g', 'Pickles | Home-made mango pickle 300g', 150, 15, 2,  40, 'https://images.unsplash.com/photo-1599599810694-b5b37304c041?w=400')
ON CONFLICT DO NOTHING;


-- ── 5. ORDERS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER       NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status              VARCHAR(30)   NOT NULL DEFAULT 'confirmed',
    -- status values: confirmed | preparing | on_the_way | delivered
    --                awaiting_payment | cancelled
    total_amount        NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    delivery_fee        NUMERIC(10,2) NOT NULL DEFAULT 0,
    payment_method      VARCHAR(30)   NOT NULL DEFAULT 'gpay',
    upi_ref             VARCHAR(200),                       -- UTR / transaction ref
    -- delivery snapshot (captured at order time, not from users table)
    delivery_address    TEXT,
    delivery_pincode    VARCHAR(10),
    delivery_apartment  VARCHAR(200),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id    ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);


-- ── 6. ORDER ITEMS ───────────────────────────────────────────
-- Snapshot of product name + price at time of order
-- so historical orders are accurate even if product changes.
CREATE TABLE IF NOT EXISTS order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER       NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id      INTEGER       REFERENCES products(id) ON DELETE SET NULL,
    name            VARCHAR(200)  NOT NULL,                 -- snapshot
    price           NUMERIC(10,2) NOT NULL,                 -- snapshot
    quantity        INTEGER       NOT NULL CHECK (quantity > 0),
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);


-- ── 7. AUTO-UPDATE updated_at TRIGGER ────────────────────────
-- Applies to: users, products, orders
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ── 8. HELPFUL VIEWS ─────────────────────────────────────────

-- Admin orders view: joins everything the admin panel needs
CREATE OR REPLACE VIEW v_admin_orders AS
SELECT
    o.id,
    o.status,
    o.total_amount,
    o.delivery_fee,
    o.upi_ref,
    o.payment_method,
    o.delivery_address,
    o.delivery_pincode,
    o.delivery_apartment,
    o.created_at,
    u.phone  AS user_phone,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'id',       oi.product_id,
            'name',     oi.name,
            'quantity', oi.quantity,
            'price',    oi.price
        ) ORDER BY oi.id
    ) AS items
FROM orders o
JOIN users       u  ON u.id  = o.user_id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, u.phone
ORDER BY o.created_at DESC;


-- Customer orders view: what the customer tracking page needs
CREATE OR REPLACE VIEW v_customer_orders AS
SELECT
    o.id,
    o.user_id,
    o.status,
    o.total_amount,
    o.delivery_fee,
    o.upi_ref,
    o.delivery_address,
    o.delivery_pincode,
    o.delivery_apartment,
    o.created_at,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'id',    oi.product_id,
            'name',  oi.name,
            'qty',   oi.quantity,
            'price', oi.price
        ) ORDER BY oi.id
    ) AS items
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id
ORDER BY o.created_at DESC;


-- ============================================================
--  END OF SCHEMA
-- ============================================================
