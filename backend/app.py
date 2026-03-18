from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ── CONFIG: all secrets from environment variables ─────────────────────
# Set these in Render Dashboard → Your Service → Environment tab.
# For local dev, export them in your shell or use a .env file.
#
#   PROSHOP_SECRET_KEY   → any long random string
#   FAST2SMS_API_KEY     → your Fast2SMS API key
#   ALLOWED_ORIGINS      → comma-separated list of allowed frontend URLs
#                          e.g. https://your-app.onrender.com,https://yourdomain.com
#                          leave unset (or set to *) during development
#
app.secret_key = os.environ.get('PROSHOP_SECRET_KEY', 'change-me-in-production')

FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', '')

# ── CORS ───────────────────────────────────────────────────────────────
# On Render both the Flask API and the static index.html are served from
# the same origin, so CORS is only needed during local development where
# the frontend runs on a different port.  We read allowed origins from an
# env var so you never have to hard-code a URL.
#
_raw_origins = os.environ.get('ALLOWED_ORIGINS', '*')
_allowed_origins = (
    [o.strip() for o in _raw_origins.split(',') if o.strip()]
    if _raw_origins != '*'
    else '*'
)

CORS(app,
     supports_credentials=False,
     origins=_allowed_origins,
     allow_headers=['Content-Type', 'X-User-ID', 'X-User-Role'],
     expose_headers=['Content-Type'])

# ── AUTH via custom headers ────────────────────────────────────────────
# Frontend stores user_id in localStorage and sends as X-User-ID header.
# This avoids all cookie/session/CORS/SameSite issues completely.
def get_user_id():
    uid = request.headers.get('X-User-ID', '').strip()
    return int(uid) if uid.isdigit() else None

def is_admin():
    uid = get_user_id()
    if not uid:
        return False
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE id=?', (uid,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 'admin'

# ── DB INIT ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT,
                  phone TEXT UNIQUE, role TEXT, created_at TIMESTAMP,
                  address TEXT, pincode TEXT, apartment TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp
                 (id INTEGER PRIMARY KEY, phone TEXT, otp TEXT,
                  expires_at TIMESTAMP, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT,
                  price REAL, image_url TEXT, stock INTEGER,
                  max_qty INTEGER DEFAULT 10, delivery_fee REAL DEFAULT 40.0,
                  created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart
                 (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER,
                  quantity INTEGER, added_at TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, user_id INTEGER, total_amount REAL,
                  status TEXT, payment_method TEXT,
                  payment_status TEXT DEFAULT 'pending',
                  upi_ref TEXT, created_at TIMESTAMP, updated_at TIMESTAMP,
                  delivery_address TEXT, delivery_pincode TEXT,
                  delivery_apartment TEXT, customer_phone TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS order_items
                 (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER,
                  quantity INTEGER, price REAL,
                  FOREIGN KEY(order_id) REFERENCES orders(id))''')
    for table, col, typedef in [
        ('users',    'address',            'TEXT'),
        ('users',    'pincode',            'TEXT'),
        ('users',    'apartment',          'TEXT'),
        ('products', 'max_qty',            'INTEGER DEFAULT 10'),
        ('products', 'delivery_fee',       'REAL DEFAULT 40.0'),
        ('orders',   'payment_status',     "TEXT DEFAULT 'pending'"),
        ('orders',   'upi_ref',            'TEXT'),
        ('orders',   'updated_at',         'TIMESTAMP'),
        ('orders',   'delivery_address',   'TEXT'),
        ('orders',   'delivery_pincode',   'TEXT'),
        ('orders',   'delivery_apartment', 'TEXT'),
        ('orders',   'customer_phone',     'TEXT'),
    ]:
        try:
            c.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
        except Exception:
            pass
    conn.commit()
    conn.close()

def seed_sample_data():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE role="admin"')
    if not c.fetchone():
        c.execute('INSERT INTO users (username,password,phone,role,created_at) VALUES (?,?,?,?,?)',
                  ('admin', generate_password_hash('admin123'), '0000000000', 'admin', datetime.now()))
    c.execute('SELECT id FROM users WHERE phone=?', ('9994656840',))
    if not c.fetchone():
        c.execute('INSERT INTO users (username,password,phone,role,created_at) VALUES (?,?,?,?,?)',
                  ('user_9994656840', generate_password_hash('8899'), '9994656840', 'customer', datetime.now()))
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        rows = [
            ('Veg Sandwich',          'AnyTime | Fresh vegetables with chutney in toasted bread',            60.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 50, 10,  0.0),
            ('Paneer Sandwich',       'AnyTime | Spiced cottage cheese filling in soft bread',               80.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Mushroom Sandwich',     'AnyTime | Sauteed mushrooms with herbs in toasted bread',             85.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Corn Sandwich',         'AnyTime | Sweet corn with mayo and veggies in bread',                 70.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Veg Cheese Sandwich',   'AnyTime | Fresh vegetables loaded with melted cheese',                90.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10,  0.0),
            ('Paneer Cheese Sandwich','AnyTime | Paneer and cheese combo in grilled bread',                 110.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Corn Cheese Sandwich',  'AnyTime | Sweet corn with extra cheese in toasted bread',             95.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10,  0.0),
            ('Bread Toast',           'AnyTime | Crispy buttered bread toast, served with chutney',          30.0, 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=400', 60, 10,  0.0),
            ('Veg Maggi Noodles',     'AnyTime | Classic Maggi noodles cooked with fresh vegetables',        60.0, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400', 50, 10,  0.0),
            ('Sesame Oil',            'Groceries | Oil | Cold-pressed pure sesame oil, 500 ml',             180.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Deepa Oil',             'Groceries | Oil | Deepa brand refined cooking oil, 1 L',             150.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Groundnut Oil',         'Groceries | Oil | Cold-pressed groundnut oil, 1 L',                  200.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 25,  5, 40.0),
            ('Sunflower Oil',         'Groceries | Oil | Refined sunflower cooking oil, 1 L',               160.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30,  5, 40.0),
            ('Mango Pickle',          'Groceries | Pickles | Spicy raw mango pickle in sesame oil, 300 g',   90.0, 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),
            ('Lemon Pickle',          'Groceries | Pickles | Tangy lemon pickle with spices, 300 g',         85.0, 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),
        ]
        for r in rows:
            c.execute('INSERT INTO products (name,description,price,image_url,stock,max_qty,delivery_fee,created_at) VALUES (?,?,?,?,?,?,?,?)', (*r, datetime.now()))
    conn.commit()
    conn.close()

# ── HEALTH ─────────────────────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/debug/auth', methods=['GET'])
def debug_auth():
    return jsonify({'user_id': get_user_id(), 'is_admin': is_admin(), 'x_user_id_header': request.headers.get('X-User-ID')})

# ── AUTH ───────────────────────────────────────────────────────────────
@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    d = request.json or {}
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id,username,password,role FROM users WHERE username=? AND role="admin"', (d.get('username'),))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], d.get('password', '')):
        return jsonify({'success': True, 'role': 'admin', 'user_id': user[0], 'username': user[1]})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/customer-login', methods=['POST'])
def customer_login():
    d = request.json or {}
    phone = d.get('phone', '').strip()
    pwd   = d.get('password', '').strip()
    if not phone or not pwd:
        return jsonify({'error': 'Phone and password required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id,password,address,pincode,apartment FROM users WHERE phone=? AND role="customer"', (phone,))
    user = c.fetchone()
    conn.close()
    if not user or not check_password_hash(user[1], pwd):
        return jsonify({'error': 'Invalid phone or password'}), 401
    saved = {'address': user[2], 'pincode': user[3], 'apartment': user[4]} if user[2] else None
    return jsonify({'success': True, 'role': 'customer', 'user_id': user[0], 'saved_address': saved})

@app.route('/api/auth/register', methods=['POST'])
def register():
    d = request.json or {}
    phone = d.get('phone', '').strip()
    pwd   = d.get('password', '').strip()
    if not phone or not phone.isdigit() or len(phone) != 10 or phone[0] not in '6789':
        return jsonify({'error': 'Enter a valid 10-digit Indian mobile number'}), 400
    if not pwd or len(pwd) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE phone=?', (phone,))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'This mobile number is already registered. Please login.'}), 409
    c.execute('INSERT INTO users (username,password,phone,role,created_at) VALUES (?,?,?,?,?)',
              (f'user_{phone}', generate_password_hash(pwd), phone, 'customer', datetime.now()))
    conn.commit()
    uid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'role': 'customer', 'user_id': uid})

@app.route('/api/auth/request-otp', methods=['POST'])
def request_otp():
    phone = (request.json or {}).get('phone', '').strip()
    if not phone or not phone.isdigit() or len(phone) != 10 or phone[0] not in '6789':
        return jsonify({'error': 'Enter a valid 10-digit Indian mobile number'}), 400
    otp = ''.join(random.choices(string.digits, k=4))
    expires_at = datetime.now() + timedelta(minutes=5)
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM otp WHERE phone=?', (phone,))
    c.execute('INSERT INTO otp (phone,otp,expires_at,created_at) VALUES (?,?,?,?)', (phone, otp, expires_at, datetime.now()))
    conn.commit()
    conn.close()
    sms_sent = False
    sms_error = ''
    try:
        resp = requests.post('https://www.fast2sms.com/dev/bulkV2',
            headers={'authorization': FAST2SMS_API_KEY},
            json={'route': 'otp', 'variables_values': otp, 'numbers': phone, 'flash': 0}, timeout=10)
        result = resp.json()
        sms_sent = result.get('return', False)
        if not sms_sent:
            sms_error = str(result.get('message', 'SMS failed'))
    except Exception as e:
        sms_error = str(e)
    res = {'success': True}
    if not sms_sent:
        res['otp'] = otp
        res['sms_error'] = sms_error
    return jsonify(res)

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    d = request.json or {}
    phone = d.get('phone', '').strip()
    otp   = d.get('otp', '').strip()
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT otp,expires_at FROM otp WHERE phone=? ORDER BY created_at DESC LIMIT 1', (phone,))
    rec = c.fetchone()
    if not rec or rec[0] != otp:
        conn.close()
        return jsonify({'error': 'Invalid OTP'}), 401
    if datetime.fromisoformat(rec[1]) < datetime.now():
        conn.close()
        return jsonify({'error': 'OTP expired. Request a new one.'}), 401
    c.execute('SELECT id,address,pincode,apartment FROM users WHERE phone=?', (phone,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (username,phone,role,created_at) VALUES (?,?,?,?)',
                  (f'user_{phone}', phone, 'customer', datetime.now()))
        conn.commit()
        user_id, saved = c.lastrowid, None
    else:
        user_id = user[0]
        saved = {'address': user[1], 'pincode': user[2], 'apartment': user[3]} if user[1] else None
    c.execute('DELETE FROM otp WHERE phone=?', (phone,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'role': 'customer', 'user_id': user_id, 'saved_address': saved})

@app.route('/api/auth/save-address', methods=['POST'])
def save_address():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d = request.json or {}
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('UPDATE users SET address=?,pincode=?,apartment=? WHERE id=?',
              (d.get('address'), d.get('pincode'), d.get('apartment'), uid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True})

# ── ADMIN ──────────────────────────────────────────────────────────────
@app.route('/api/admin/users')
def admin_get_users():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id,username,phone,role,created_at,address,pincode,apartment FROM users WHERE role != "admin" ORDER BY created_at DESC')
    cols = ['id','username','phone','role','created_at','address','pincode','apartment']
    users = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/orders')
def admin_get_orders():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT o.*, u.phone as user_phone FROM orders o
                 LEFT JOIN users u ON o.user_id = u.id
                 WHERE o.payment_status = 'paid' ORDER BY o.created_at DESC''')
    orders = []
    for row in c.fetchall():
        order = dict(row)
        c.execute('''SELECT oi.quantity, oi.price, p.name FROM order_items oi
                     LEFT JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?''', (order['id'],))
        order['items'] = [dict(zip(['quantity','price','name'], r)) for r in c.fetchall()]
        orders.append(order)
    conn.close()
    return jsonify(orders)

@app.route('/api/admin/orders/<int:oid>/status', methods=['PUT'])
def admin_update_order_status(oid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d = request.json or {}
    status = d.get('status', '').strip()
    valid = ['confirmed','preparing','on_the_way','delivered','cancelled']
    if status not in valid:
        return jsonify({'error': f'Invalid status'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET status=?, updated_at=? WHERE id=?', (status, datetime.now(), oid))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid, 'status': status})

# ── PRODUCTS ───────────────────────────────────────────────────────────
@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products ORDER BY id')
    products = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d = request.json or {}
    name = d.get('name', '').strip()
    if not name or d.get('price') is None:
        return jsonify({'error': 'Name and price required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('INSERT INTO products (name,description,price,image_url,stock,max_qty,delivery_fee,created_at) VALUES (?,?,?,?,?,?,?,?)',
              (name, d.get('description',''), float(d['price']), d.get('image_url',''),
               int(d.get('stock',0)), int(d.get('max_qty',10)), float(d.get('delivery_fee',40.0)), datetime.now()))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    d = request.json or {}
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('UPDATE products SET name=?,description=?,price=?,image_url=?,stock=?,max_qty=?,delivery_fee=? WHERE id=?',
              (d.get('name'), d.get('description'), float(d.get('price',0)),
               d.get('image_url',''), int(d.get('stock',0)),
               int(d.get('max_qty',10)), float(d.get('delivery_fee',0.0)), pid))
    conn.commit()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id=?', (pid,))
    updated = c.fetchone()
    conn.close()
    if updated:
        return jsonify({'success': True, 'product': dict(updated)})
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE product_id=?', (pid,))
    c.execute('DELETE FROM products WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── CART ───────────────────────────────────────────────────────────────
@app.route('/api/cart')
def get_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT c.id,c.product_id,c.quantity,p.name,p.price,p.image_url FROM cart c JOIN products p ON c.product_id=p.id WHERE c.user_id=?', (uid,))
    items = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'items': items, 'total': round(sum(i['quantity']*i['price'] for i in items), 2), 'count': len(items)})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d = request.json or {}
    pid = d.get('product_id')
    qty = int(d.get('quantity', 1))
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT stock,max_qty FROM products WHERE id=?', (pid,))
    p = c.fetchone()
    if not p:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    stock, max_qty = p
    c.execute('SELECT id,quantity FROM cart WHERE user_id=? AND product_id=?', (uid, pid))
    existing = c.fetchone()
    new_qty = (existing[1] if existing else 0) + qty
    if new_qty > max_qty:
        conn.close()
        return jsonify({'error': f'Maximum {max_qty} items allowed'}), 400
    if new_qty > stock:
        conn.close()
        return jsonify({'error': 'Not enough stock'}), 400
    if existing:
        c.execute('UPDATE cart SET quantity=? WHERE id=?', (new_qty, existing[0]))
    else:
        c.execute('INSERT INTO cart (user_id,product_id,quantity,added_at) VALUES (?,?,?,?)', (uid, pid, qty, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/update/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    qty = int((request.json or {}).get('quantity', 0))
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    if qty <= 0:
        c.execute('DELETE FROM cart WHERE id=?', (cart_id,))
    else:
        c.execute('UPDATE cart SET quantity=? WHERE id=?', (qty, cart_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE id=?', (cart_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user_id=?', (uid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── ORDERS ─────────────────────────────────────────────────────────────
@app.route('/api/orders/create', methods=['POST'])
def create_order():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d = request.json or {}
    delivery_fee = float(d.get('delivery_fee', 0))
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    # ── BUG FIX: Frontend manages cart in JS memory only; it never writes
    # to the DB cart table.  Accept items[] from the request body so the
    # backend doesn't query an always-empty DB cart. Falls back to DB cart
    # for any server-side flow that does write to it. ────────────────────
    frontend_items = d.get('items', [])   # [{id, qty}, ...]
    if frontend_items:
        items = []
        for entry in frontend_items:
            pid = int(entry.get('id') or entry.get('product_id') or 0)
            qty = int(entry.get('qty') or entry.get('quantity') or 1)
            if not pid or qty < 1:
                continue
            c.execute('SELECT price, stock, max_qty FROM products WHERE id=?', (pid,))
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
        # Fallback: DB-managed cart
        c.execute('SELECT c.product_id,c.quantity,p.price,p.stock FROM cart c JOIN products p ON c.product_id=p.id WHERE c.user_id=?', (uid,))
        items = c.fetchall()
        if not items:
            conn.close()
            return jsonify({'error': 'Cart is empty'}), 400
        for pid, qty, price, stock in items:
            if stock < qty:
                conn.close()
                return jsonify({'error': 'Insufficient stock'}), 400

    subtotal = sum(qty * price for _, qty, price, _ in items)
    total = subtotal + delivery_fee
    c.execute('SELECT phone FROM users WHERE id=?', (uid,))
    user_row = c.fetchone()
    customer_phone = user_row[0] if user_row else ''
    c.execute('INSERT INTO orders (user_id,total_amount,status,payment_method,payment_status,created_at,delivery_address,delivery_pincode,delivery_apartment,customer_phone) VALUES (?,?,?,?,?,?,?,?,?,?)',
              (uid, total, 'awaiting_payment', 'gpay', 'pending', datetime.now(),
               d.get('address',''), d.get('pincode',''), d.get('apartment',''), customer_phone))
    oid = c.lastrowid
    for pid, qty, price, _ in items:
        c.execute('INSERT INTO order_items (order_id,product_id,quantity,price) VALUES (?,?,?,?)', (oid, pid, qty, price))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid, 'total_amount': total})

@app.route('/api/orders/confirm-payment', methods=['POST'])
def confirm_payment():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    d = request.json or {}
    oid = d.get('order_id')
    upi_ref = d.get('upi_ref', '').strip() or 'MANUAL_VERIFY_PENDING'
    if not oid:
        return jsonify({'error': 'Order ID required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id,total_amount,payment_status,user_id FROM orders WHERE id=? AND user_id=?', (oid, uid))
    order = c.fetchone()
    if not order:
        conn.close()
        return jsonify({'error': 'Order not found'}), 404
    if order[2] == 'paid':
        conn.close()
        return jsonify({'error': 'Order already paid'}), 400
    c.execute('UPDATE orders SET status=?,payment_status=?,upi_ref=?,updated_at=? WHERE id=?',
              ('confirmed', 'paid', upi_ref, datetime.now(), oid))
    c.execute('SELECT product_id,quantity FROM order_items WHERE order_id=?', (oid,))
    for pid, qty in c.fetchall():
        c.execute('UPDATE products SET stock=stock-? WHERE id=?', (qty, pid))
    c.execute('DELETE FROM cart WHERE user_id=?', (uid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': oid})

@app.route('/api/orders')
def get_orders():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id=? AND payment_status='paid' ORDER BY created_at DESC", (uid,))
    orders = []
    for row in c.fetchall():
        order = dict(row)
        c.execute('SELECT oi.quantity, oi.price, p.name FROM order_items oi LEFT JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?', (order['id'],))
        order['items'] = [dict(zip(['quantity','price','name'], r)) for r in c.fetchall()]
        orders.append(order)
    conn.close()
    return jsonify(orders)

@app.route('/api/orders/<int:oid>')
def get_order(oid):
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE id=? AND user_id=?', (oid, uid))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(dict(row))

if __name__ == '__main__':
    init_db()
    seed_sample_data()
    app.run(debug=True, port=5000)
