"""
SCRIPT 2 — seed_admin.py
Creates the admin user and one sample customer account.
Run AFTER fix_tables.py.

Usage:
    python seed_admin.py
"""

import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from datetime import datetime

load_dotenv()

def get_db():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise RuntimeError("DATABASE_URL not set in .env")
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return psycopg2.connect(db_url)

def seed_admin():
    conn = get_db()
    c = conn.cursor()

    # ── Admin user ─────────────────────────────────────────────────────────
    c.execute("SELECT id FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute('''
            INSERT INTO users (username, password, phone, role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', ('admin', generate_password_hash('admin123'), '0000000000', 'admin', datetime.now()))
        print("✅ Admin created   → username: admin   | password: admin123")
    else:
        print("ℹ️  Admin already exists — skipped.")

    # ── Sample customer ────────────────────────────────────────────────────
    c.execute("SELECT id FROM users WHERE phone=%s", ('9994656840',))
    if not c.fetchone():
        c.execute('''
            INSERT INTO users (username, password, phone, role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', ('user_9994656840', generate_password_hash('8899'), '9994656840', 'customer', datetime.now()))
        print("✅ Sample customer → phone: 9994656840 | password: 8899")
    else:
        print("ℹ️  Sample customer already exists — skipped.")

    conn.commit()
    conn.close()
    print("\n✅ Users seeded.")
    print("👉 Run:  python seed_products.py   next.")

if __name__ == '__main__':
    seed_admin()
