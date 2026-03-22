from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
import random
import string
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ── Load .env for local development ───────────────────────────────────────
# On Render, DATABASE_URL is injected automatically as an env var.
# Locally, it is read from your .env file.
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'proshop-secret-2024')

# ── CORS ───────────────────────────────────────────────────────────────────
# supports_credentials=False + origins='*' is correct for header-based auth.
# allow_headers must include X-User-ID and X-User-Role so preflight passes.
CORS(app,
     supports_credentials=False,
     origins='*',
     allow_headers=['Content-Type', 'X-User-ID', 'X-User-Role'],
     expose_headers=['Content-Type', 'X-User-ID', 'X-User-Role'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', 'YOUR_FAST2SMS_API_KEY_HERE')

# ── DB CONNECTION ──────────────────────────────────────────────────────────
def get_db():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    # Strip pgbouncer=true param — psycopg2 doesn't recognise it
    # but keep sslmode if present
    import urllib.parse as _up
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(db_url)
    params = parse_qs(parsed.query)
    params.pop('pgbouncer', None)          # remove pgbouncer=true
    if 'sslmode' not in params:
        params['sslmode'] = ['require']    # always require SSL
    new_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=new_query))
    return psycopg2.connect(clean_url, connect_timeout=10)

# ── AUTH HELPERS ───────────────────────────────────────────────────────────
def get_user_id():
    """Read user ID from X-User-ID header. Returns int or None."""
    uid = request.headers.get('X-User-ID', '').strip()
    return int(uid) if uid.isdigit() else None

def get_user_role(conn, uid):
    """Fetch role for a user ID using an existing connection."""
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE id=%s', (uid,))
    row = c.fetchone()
    return row[0] if row else None

def is_admin():
    """
    Check if the requesting user is an admin.
    Opens its own short-lived connection so it never conflicts with
    a caller's open transaction.
    """
    uid = get_user_id()
    if not uid:
        return False
    try:
        conn = get_db()
        role = get_user_role(conn, uid)
        conn.close()
        return role == 'admin'
    except Exception:
        return False

# ── DB INIT ────────────────────────────────────────────────────────────────
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id SERIAL PRIMARY KEY,
                 username TEXT UNIQUE,
                 password TEXT,
                 phone TEXT UNIQUE,
                 role TEXT,
                 created_at TIMESTAMP,
                 address TEXT,
                 pincode TEXT,
                 apartment TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS otp (
                 id SERIAL PRIMARY KEY,
                 phone TEXT,
                 otp TEXT,
                 expires_at TIMESTAMP,
                 created_at TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id SERIAL PRIMARY KEY,
                 name TEXT,
                 description TEXT,
                 price REAL,
                 image_url TEXT,
                 stock INTEGER,
                 max_qty INTEGER DEFAULT 10,
                 delivery_fee REAL DEFAULT 40.0,
                 created_at TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS cart (
                 id SERIAL PRIMARY KEY,
                 user_id INTEGER REFERENCES users(id),
                 product_id INTEGER,
                 quantity INTEGER,
                 added_at TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 id SERIAL PRIMARY KEY,
                 user_id INTEGER REFERENCES users(id),
                 total_amount REAL,
                 status TEXT,
                 payment_method TEXT,
                 payment_status TEXT DEFAULT 'pending',
                 upi_ref TEXT,
                 created_at TIMESTAMP,
                 updated_at TIMESTAMP,
                 delivery_address TEXT,
                 delivery_pincode TEXT,
                 delivery_apartment TEXT,
                 customer_phone TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
                 id SERIAL PRIMARY KEY,
                 order_id INTEGER REFERENCES orders(id),
                 product_id INTEGER,
                 quantity INTEGER,
                 price REAL)''')

    # Safe column-add migration (won't fail if column already exists)
    def add_col(table, col, typedef):
        c.execute("""SELECT 1 FROM information_schema.columns
                     WHERE table_name=%s AND column_name=%s""", (table, col))
        if not c.fetchone():
            c.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')

    add_col('users',    'address',            'TEXT')
    add_col('users',    'pincode',            'TEXT')
    add_col('users',    'apartment',          'TEXT')
    add_col('products', 'max_qty',            'INTEGER DEFAULT 10')
    add_col('products', 'delivery_fee',       'REAL DEFAULT 40.0')
    add_col('orders',   'payment_status',     "TEXT DEFAULT 'pending'")
    add_col('orders',   'upi_ref',            'TEXT')
    add_col('orders',   'updated_at',         'TIMESTAMP')
    add_col('orders',   'delivery_address',   'TEXT')
    add_col('orders',   'delivery_pincode',   'TEXT')
    add_col('orders',   'delivery_apartment', 'TEXT')
    add_col('orders',   'customer_phone',     'TEXT')

    conn.commit()
    conn.close()
    print("✅ Database tables ready.")

# ── SEED DATA ──────────────────────────────────────────────────────────────
def seed_sample_data():
    conn = get_db()
    c = conn.cursor()

    # Admin user
    c.execute("SELECT id FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute('''INSERT INTO users (username,password,phone,role,created_at)
                     VALUES (%s,%s,%s,%s,%s)''',
                  ('admin', generate_password_hash('admin123'),
                   '0000000000', 'admin', datetime.now()))
        print("✅ Admin user created  →  username: admin  |  password: admin123")

    # Sample customer
    c.execute('SELECT id FROM users WHERE phone=%s', ('9994656840',))
    if not c.fetchone():
        c.execute('''INSERT INTO users (username,password,phone,role,created_at)
                     VALUES (%s,%s,%s,%s,%s)''',
                  ('user_9994656840', generate_password_hash('8899'),
                   '9994656840', 'customer', datetime.now()))

    # Sample products
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        rows = [
            ('Veg Sandwich',           'AnyTime | Fresh vegetables with chutney in toasted bread',             60.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 50, 10,  0.0),
            ('Paneer Sandwich',        'AnyTime | Spiced cottage cheese filling in soft bread',                80.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Mushroom Sandwich',      'AnyTime | Sauteed mushrooms with herbs in toasted bread',              85.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Corn Sandwich',          'AnyTime | Sweet corn with mayo and veggies in bread',                  70.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Veg Cheese Sandwich',    'AnyTime | Fresh vegetables loaded with melted cheese',                 90.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Paneer Cheese Sandwich', 'AnyTime | Paneer and cheese combo in grilled bread',                  110.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Corn Cheese Sandwich',   'AnyTime | Sweet corn with extra cheese in toasted bread',              95.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Bread Toast',            'AnyTime | Crispy buttered bread toast, served with chutney',           30.0,  'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=400', 60, 10,  0.0),
            ('Veg Maggi Noodles',      'AnyTime | Classic Maggi noodles cooked with fresh vegetables',         60.0,  'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400', 50, 10,  0.0),
            ('Sesame Oil',             'Groceries | Oil | Cold-pressed pure sesame oil, 500 ml',              180.0,  'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Deepa Oil',              'Groceries | Oil | Deepa brand refined cooking oil, 1 L',              150.0,  'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Groundnut Oil',          'Groceries | Oil | Cold-pressed groundnut oil, 1 L',                   200.0,  'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 25,  5, 40.0),
            ('Sunflower Oil',          'Groceries | Oil | Refined sunflower cooking oil, 1 L',                160.0,  'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Mango Pickle',           'Groceries | Pickles | Spicy raw mango pickle in sesame oil, 300 g',    90.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),
            ('Lemon Pickle',           'Groceries | Pickles | Tangy lemon pickle with spices, 300 g',          85.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),
        ]
        for r in rows:
            c.execute('''INSERT INTO products
                         (name,description,price,image_url,stock,max_qty,delivery_fee,created_at)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', (*r, datetime.now()))
        print(f"✅ Seeded {len(rows)} products.")

    conn.commit()
    conn.close()

# ── FRONTEND ───────────────────────────────────────────────────────────────
@app.route('/')
def serve_index():
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
    return send_from_directory(frontend_dir, 'index.html')

# ── HEALTH ─────────────────────────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/debug/auth', methods=['GET'])
def debug_auth():
    """Useful for debugging header-based auth issues."""
    uid = get_user_id()
    role = None
    if uid:
        try:
            conn = get_db()
            role = get_user_role(conn, uid)
            conn.close()
        except Exception:
            pass
    return jsonify({
        'user_id': uid,
        'role': role,
        'is_admin': role == 'admin',
        'x_user_id_header': request.headers.get('X-User-ID'),
        'x_user_role_header': request.headers.get('X-User-Role'),
        'all_headers': dict(request.headers)
    })

# ── AUTH ───────────────────────────────────────────────────────────────────
@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    d        = request.json or {}
    username = d.get('username', '').strip()
    password = d.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id,username,password,role FROM users WHERE username=%s AND role='admin'",
              (username,))
    user = c.fetchone()
    conn.close()
    if not user or not check_password_hash(user[2], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'success': True, 'role': 'admin', 'user_id': user[0], 'username': user[1]})

@app.route('/api/auth/customer-login', methods=['POST'])
def customer_login():
    d     = request.json or {}
    phone = d.get('phone', '').strip()
    pwd   = d.get('password', '').strip()
    if not phone or not pwd:
        return jsonify({'error': 'Phone and password required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id,password,address,pincode,apartment FROM users WHERE phone=%s AND role='customer'",
              (phone,))
    user = c.fetchone()
    conn.close()
    if not user or not check_password_hash(user[1], pwd):
        return jsonify({'error': 'Invalid phone or password'}), 401
    saved = {'address': user[2], 'pincode': user[3], 'apartment': user[4]} if user[2] else None
    return jsonify({'success': True, 'role': 'customer', 'user_id': user[0], 'saved_address': saved})

@app.route('/api/auth/register', methods=['POST'])
def register():
    d     = request.json or {}
    phone = d.get('phone', '').strip()
    pwd   = d.get('password', '').strip()
    if not phone or not phone.isdigit() or len(phone) != 10 or phone[0] not in '6789':
        return jsonify({'error': 'Enter a valid 10-digit Indian mobile number'}), 400
    if not pwd or len(pwd) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE phone=%s', (phone,))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'This mobile number is already registered. Please login.'}), 409
    c.execute('''INSERT INTO users (username,password,phone,role,created_at)
                 VALUES (%s,%s,%s,%s,%s) RETURNING id''',
              (f'user_{phone}', generate_password_hash(pwd), phone, 'customer', datetime.now()))
    uid = c.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'role': 'customer', 'user_id': uid})

@app.route('/api/auth/request-otp', methods=['POST'])
def request_otp():
    phone = (request.json or {}).get('phone', '').strip()
    if not phone or not phone.isdigit() or len(phone) != 10 or phone[0] not in '6789':
        return jsonify({'error': 'Enter a valid 10-digit Indian mobile number'}), 400
    otp        = ''.join(random.choices(string.digits, k=4))
    expires_at = datetime.now() + timedelta(minutes=5)
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM otp WHERE phone=%s', (phone,))
    c.execute('INSERT INTO otp (phone,otp,expires_at,created_at) VALUES (%s,%s,%s,%s)',
              (phone, otp, expires_at, datetime.now()))
    conn.commit()
    conn.close()
    sms_sent  = False
    sms_error = ''
    try:
        resp = requests.post('https://www.fast2sms.com/dev/bulkV2',
            headers={'authorization': FAST2SMS_API_KEY},
            json={'route': 'otp', 'variables_values': otp, 'numbers': phone, 'flash': 0},
            timeout=10)
        result   = resp.json()
        sms_sent = result.get('return', False)
        if not sms_sent:
            sms_error = str(result.get('message', 'SMS failed'))
    except Exception as e:
        sms_error = str(e)
    res = {'success': True}
    if not sms_sent:
        res['otp']       = otp
        res['sms_error'] = sms_error
    return jsonify(res)

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    d     = request.json or {}
    phone = d.get('phone', '').strip()
    otp   = d.get('otp', '').strip()
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT otp,expires_at FROM otp WHERE phone=%s ORDER BY created_at DESC LIMIT 1',
              (phone,))
    rec = c.fetchone()
    if not rec or rec[0] != otp:
        conn.close()
        return jsonify({'error': 'Invalid OTP'}), 401
    # psycopg2 returns expires_at as a Python datetime — no fromisoformat needed
    if rec[1] < datetime.now():
        conn.close()
        return jsonify({'error': 'OTP expired. Request a new one.'}), 401
    c.execute('SELECT id,address,pincode,apartment FROM users WHERE phone=%s', (phone,))
    user = c.fetchone()
    if not user:
        c.execute('''INSERT INTO users (username,phone,role,created_at)
                     VALUES (%s,%s,%s,%s) RETURNING id''',
                  (f'user_{phone}', phone, 'customer', datetime.now()))
        user_id = c.fetchone()[0]
        saved   = None
    else:
        user_id = user[0]
        saved   = {'address': user[1], 'pincode': user[2], 'apartment': user[3]} if user[1] else None
    c.execute('DELETE FROM otp WHERE phone=%s', (phone,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'role': 'customer', 'user_id': user_id, 'saved_address': saved})

@app.route('/api/auth/save-address', methods=['POST'])
def save_address():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d = request.json or {}
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET address=%s,pincode=%s,apartment=%s WHERE id=%s',
              (d.get('address'), d.get('pincode'), d.get('apartment'), uid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True})

# ── ADMIN ──────────────────────────────────────────────────────────────────
@app.route('/api/admin/users')
def admin_get_users():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("""SELECT id,username,phone,role,created_at,address,pincode,apartment
                 FROM users WHERE role != 'admin' ORDER BY created_at DESC""")
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/orders')
def admin_get_orders():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("""SELECT o.*, u.phone AS user_phone
                 FROM orders o LEFT JOIN users u ON o.user_id = u.id
                 WHERE o.payment_status IN ('paid','claimed')
                 ORDER BY o.created_at DESC""")
    orders = []
    for row in c.fetchall():
        order = dict(row)
        c2 = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c2.execute("""SELECT oi.quantity, oi.price, p.name
                      FROM order_items oi
                      LEFT JOIN products p ON oi.product_id = p.id
                      WHERE oi.order_id = %s""", (order['id'],))
        order['items'] = [dict(r) for r in c2.fetchall()]
        orders.append(order)
    conn.close()
    return jsonify(orders)

@app.route('/api/admin/orders/<int:oid>/verify-payment', methods=['POST'])
def admin_verify_payment(oid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d      = request.json or {}
    action = d.get('action', '').strip()
    if action not in ('confirm', 'reject'):
        return jsonify({'error': 'action must be confirm or reject'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id,payment_status FROM orders WHERE id=%s', (oid,))
    order = c.fetchone()
    if not order:
        conn.close()
        return jsonify({'error': 'Order not found'}), 404
    if action == 'confirm':
        c.execute('UPDATE orders SET status=%s,payment_status=%s,updated_at=%s WHERE id=%s',
                  ('confirmed', 'paid', datetime.now(), oid))
        msg = 'Payment confirmed'
    else:
        c.execute('SELECT product_id,quantity FROM order_items WHERE order_id=%s', (oid,))
        for pid, qty in c.fetchall():
            c.execute('UPDATE products SET stock=stock+%s WHERE id=%s', (qty, pid))
        c.execute('UPDATE orders SET status=%s,payment_status=%s,updated_at=%s WHERE id=%s',
                  ('cancelled', 'rejected', datetime.now(), oid))
        msg = 'Payment rejected, order cancelled'
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': msg})

@app.route('/api/admin/orders/<int:oid>/status', methods=['PUT'])
def admin_update_order_status(oid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d      = request.json or {}
    status = d.get('status', '').strip()
    valid  = ['confirmed', 'preparing', 'on_the_way', 'delivered', 'cancelled']
    if status not in valid:
        return jsonify({'error': 'Invalid status'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE orders SET status=%s,updated_at=%s WHERE id=%s',
              (status, datetime.now(), oid))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid, 'status': status})

# ── PRODUCTS ───────────────────────────────────────────────────────────────
@app.route('/api/products')
def get_products():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute('SELECT * FROM products ORDER BY id')
    products = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d    = request.json or {}
    name = d.get('name', '').strip()
    if not name or d.get('price') is None:
        return jsonify({'error': 'Name and price required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO products
                 (name,description,price,image_url,stock,max_qty,delivery_fee,created_at)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''',
              (name, d.get('description', ''), float(d['price']),
               d.get('image_url', ''), int(d.get('stock', 0)),
               int(d.get('max_qty', 10)), float(d.get('delivery_fee', 40.0)),
               datetime.now()))
    new_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d = request.json or {}
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE products
                 SET name=%s,description=%s,price=%s,image_url=%s,
                     stock=%s,max_qty=%s,delivery_fee=%s
                 WHERE id=%s''',
              (d.get('name'), d.get('description'), float(d.get('price', 0)),
               d.get('image_url', ''), int(d.get('stock', 0)),
               int(d.get('max_qty', 10)), float(d.get('delivery_fee', 0.0)), pid))
    conn.commit()
    c2 = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c2.execute('SELECT * FROM products WHERE id=%s', (pid,))
    updated = c2.fetchone()
    conn.close()
    if updated:
        return jsonify({'success': True, 'product': dict(updated)})
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE product_id=%s', (pid,))
    c.execute('DELETE FROM products WHERE id=%s', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── CART ───────────────────────────────────────────────────────────────────
@app.route('/api/cart')
def get_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute('''SELECT c.id,c.product_id,c.quantity,p.name,p.price,p.image_url
                 FROM cart c JOIN products p ON c.product_id=p.id
                 WHERE c.user_id=%s''', (uid,))
    items = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({
        'items': items,
        'total': round(sum(i['quantity'] * i['price'] for i in items), 2),
        'count': len(items)
    })

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d   = request.json or {}
    pid = d.get('product_id')
    qty = int(d.get('quantity', 1))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT stock,max_qty FROM products WHERE id=%s', (pid,))
    p = c.fetchone()
    if not p:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    stock, max_qty = p
    c.execute('SELECT id,quantity FROM cart WHERE user_id=%s AND product_id=%s', (uid, pid))
    existing = c.fetchone()
    new_qty  = (existing[1] if existing else 0) + qty
    if new_qty > max_qty:
        conn.close()
        return jsonify({'error': f'Maximum {max_qty} items allowed'}), 400
    if new_qty > stock:
        conn.close()
        return jsonify({'error': 'Not enough stock'}), 400
    if existing:
        c.execute('UPDATE cart SET quantity=%s WHERE id=%s', (new_qty, existing[0]))
    else:
        c.execute('INSERT INTO cart (user_id,product_id,quantity,added_at) VALUES (%s,%s,%s,%s)',
                  (uid, pid, qty, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/update/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    qty = int((request.json or {}).get('quantity', 0))
    conn = get_db()
    c = conn.cursor()
    if qty <= 0:
        c.execute('DELETE FROM cart WHERE id=%s', (cart_id,))
    else:
        c.execute('UPDATE cart SET quantity=%s WHERE id=%s', (qty, cart_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE id=%s', (cart_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user_id=%s', (uid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── ORDERS ─────────────────────────────────────────────────────────────────
@app.route('/api/orders/create', methods=['POST'])
def create_order():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d            = request.json or {}
    delivery_fee = float(d.get('delivery_fee', 0))
    conn = get_db()
    c = conn.cursor()

    # Frontend sends cart items in the request body.
    # Fall back to DB cart if items not in body.
    frontend_items = d.get('items', [])
    if frontend_items:
        items = []
        for entry in frontend_items:
            pid = int(entry.get('id') or entry.get('product_id') or 0)
            qty = int(entry.get('qty') or entry.get('quantity') or 1)
            if not pid or qty < 1:
                continue
            c.execute('SELECT price,stock,max_qty FROM products WHERE id=%s', (pid,))
            row = c.fetchone()
            if not row:
                conn.close()
                return jsonify({'error': f'Product {pid} not found'}), 400
            price, stock, max_qty = row
            if qty > (max_qty or 10):
                conn.close()
                return jsonify({'error': f'Max {max_qty} per order for product {pid}'}), 400
            if stock < qty:
                conn.close()
                return jsonify({'error': f'Insufficient stock for product {pid}'}), 400
            items.append((pid, qty, price, stock))
        if not items:
            conn.close()
            return jsonify({'error': 'No valid items in order'}), 400
    else:
        c.execute('''SELECT c.product_id,c.quantity,p.price,p.stock
                     FROM cart c JOIN products p ON c.product_id=p.id
                     WHERE c.user_id=%s''', (uid,))
        items = c.fetchall()
        if not items:
            conn.close()
            return jsonify({'error': 'Cart is empty'}), 400
        for pid, qty, price, stock in items:
            if stock < qty:
                conn.close()
                return jsonify({'error': 'Insufficient stock'}), 400

    subtotal = sum(qty * price for _, qty, price, _ in items)
    total    = subtotal + delivery_fee

    c.execute('SELECT phone FROM users WHERE id=%s', (uid,))
    user_row       = c.fetchone()
    customer_phone = user_row[0] if user_row else ''

    c.execute('''INSERT INTO orders
                 (user_id,total_amount,status,payment_method,payment_status,
                  created_at,delivery_address,delivery_pincode,delivery_apartment,customer_phone)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''',
              (uid, total, 'awaiting_payment', 'gpay', 'pending', datetime.now(),
               d.get('address', ''), d.get('pincode', ''),
               d.get('apartment', ''), customer_phone))
    oid = c.fetchone()[0]

    for pid, qty, price, _ in items:
        c.execute('INSERT INTO order_items (order_id,product_id,quantity,price) VALUES (%s,%s,%s,%s)',
                  (oid, pid, qty, price))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid, 'total_amount': total})

@app.route('/api/orders/confirm-payment', methods=['POST'])
def confirm_payment():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d       = request.json or {}
    oid     = d.get('order_id')
    upi_ref = d.get('upi_ref', '').strip() or 'MANUAL_VERIFY_PENDING'
    if not oid:
        return jsonify({'error': 'Order ID required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id,total_amount,payment_status,user_id FROM orders WHERE id=%s AND user_id=%s',
              (oid, uid))
    order = c.fetchone()
    if not order:
        conn.close()
        return jsonify({'error': 'Order not found'}), 404
    if order[2] == 'paid':
        conn.close()
        return jsonify({'error': 'Order already paid'}), 400
    c.execute('UPDATE orders SET status=%s,payment_status=%s,upi_ref=%s,updated_at=%s WHERE id=%s',
              ('pending_confirmation', 'claimed', upi_ref, datetime.now(), oid))
    c.execute('SELECT product_id,quantity FROM order_items WHERE order_id=%s', (oid,))
    for pid, qty in c.fetchall():
        c.execute('UPDATE products SET stock=stock-%s WHERE id=%s', (qty, pid))
    c.execute('DELETE FROM cart WHERE user_id=%s', (uid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid})

@app.route('/api/orders')
def get_orders():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("""SELECT * FROM orders
                 WHERE user_id=%s AND payment_status IN ('paid','claimed')
                 ORDER BY created_at DESC""", (uid,))
    orders = []
    for row in c.fetchall():
        order = dict(row)
        c2 = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c2.execute('''SELECT oi.quantity,oi.price,p.name
                      FROM order_items oi
                      LEFT JOIN products p ON oi.product_id=p.id
                      WHERE oi.order_id=%s''', (order['id'],))
        order['items'] = [dict(r) for r in c2.fetchall()]
        orders.append(order)
    conn.close()
    return jsonify(orders)

@app.route('/api/orders/<int:oid>')
def get_order(oid):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute('SELECT * FROM orders WHERE id=%s AND user_id=%s', (oid, uid))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(dict(row))

# ── ERROR HANDLERS ─────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found', 'path': request.path}), 404
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
    return send_from_directory(frontend_dir, 'index.html')

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

# ── STARTUP ────────────────────────────────────────────────────────────────
init_db()
#seed_sample_data()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
