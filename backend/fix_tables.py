"""
SCRIPT 1 — fix_tables.py
Drops all existing tables and recreates them with the correct structure.
Run this ONCE to fix the schema.

Usage:
    python fix_tables.py
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise RuntimeError("DATABASE_URL not set in .env")
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return psycopg2.connect(db_url)

def fix_tables():
    conn = get_db()
    c = conn.cursor()

    print("⚠️  Dropping all existing tables...")

    # Drop in reverse dependency order (FK constraints)
    c.execute("DROP TABLE IF EXISTS order_items CASCADE")
    c.execute("DROP TABLE IF EXISTS orders     CASCADE")
    c.execute("DROP TABLE IF EXISTS cart       CASCADE")
    c.execute("DROP TABLE IF EXISTS products   CASCADE")
    c.execute("DROP TABLE IF EXISTS otp        CASCADE")
    c.execute("DROP TABLE IF EXISTS users      CASCADE")
    print("   ✅ All old tables dropped.")

    print("🔧 Creating tables with correct structure...")

    c.execute('''
        CREATE TABLE users (
            id         SERIAL PRIMARY KEY,
            username   TEXT UNIQUE,
            password   TEXT,
            phone      TEXT UNIQUE,
            role       TEXT,
            created_at TIMESTAMP,
            address    TEXT,
            pincode    TEXT,
            apartment  TEXT
        )
    ''')
    print("   ✅ users")

    c.execute('''
        CREATE TABLE otp (
            id         SERIAL PRIMARY KEY,
            phone      TEXT,
            otp        TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP
        )
    ''')
    print("   ✅ otp")

    c.execute('''
        CREATE TABLE products (
            id           SERIAL PRIMARY KEY,
            name         TEXT,
            description  TEXT,
            price        REAL,
            image_url    TEXT,
            stock        INTEGER,
            max_qty      INTEGER DEFAULT 10,
            delivery_fee REAL    DEFAULT 40.0,
            created_at   TIMESTAMP
        )
    ''')
    print("   ✅ products")

    c.execute('''
        CREATE TABLE cart (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER,
            quantity   INTEGER,
            added_at   TIMESTAMP
        )
    ''')
    print("   ✅ cart")

    c.execute('''
        CREATE TABLE orders (
            id                 SERIAL PRIMARY KEY,
            user_id            INTEGER REFERENCES users(id) ON DELETE SET NULL,
            total_amount       REAL,
            status             TEXT,
            payment_method     TEXT,
            payment_status     TEXT DEFAULT 'pending',
            upi_ref            TEXT,
            created_at         TIMESTAMP,
            updated_at         TIMESTAMP,
            delivery_address   TEXT,
            delivery_pincode   TEXT,
            delivery_apartment TEXT,
            customer_phone     TEXT
        )
    ''')
    print("   ✅ orders")

    c.execute('''
        CREATE TABLE order_items (
            id         SERIAL PRIMARY KEY,
            order_id   INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER,
            quantity   INTEGER,
            price      REAL
        )
    ''')
    print("   ✅ order_items")

    conn.commit()
    conn.close()
    print("\n✅ All tables created successfully with correct structure.")
    print("👉 Run:  python seed_admin.py   next.")

if __name__ == '__main__':
    fix_tables()
