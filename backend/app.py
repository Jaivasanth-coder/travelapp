from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app, supports_credentials=True, origins=['http://localhost:5500', 'http://localhost:8000', 'http://127.0.0.1:5500'])

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

def get_user_id():
    """Get user_id from session or header"""
    user_id = session.get('user_id')
    if not user_id:
        user_id = request.headers.get('X-User-ID')
    return user_id

def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  phone TEXT UNIQUE, role TEXT, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp
                 (id INTEGER PRIMARY KEY, phone TEXT, otp TEXT, 
                  expires_at TIMESTAMP, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT, 
                  price REAL, image_url TEXT, stock INTEGER, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart
                 (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, 
                  quantity INTEGER, added_at TIMESTAMP, 
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, user_id INTEGER, total_amount REAL, 
                  status TEXT, payment_method TEXT, created_at TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS order_items
                 (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, 
                  quantity INTEGER, price REAL,
                  FOREIGN KEY(order_id) REFERENCES orders(id))''')
    conn.commit()
    conn.close()

def seed_sample_data():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE role=?', ('admin',))
    if not c.fetchone():
        hashed_pwd = generate_password_hash('admin123')
        c.execute('INSERT INTO users (username, password, phone, role, created_at) VALUES (?, ?, ?, ?, ?)',
                  ('admin', hashed_pwd, '0000000000', 'admin', datetime.now()))
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        products = [
            ('Laptop Pro 15', 'High-performance laptop', 999.99, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400', 10),
            ('Wireless Earbuds', 'Noise-cancelling earbuds', 149.99, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', 25),
            ('Smart Watch', 'Smartwatch with health tracking', 299.99, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400', 15),
            ('USB-C Cable', 'Fast charging cable', 19.99, 'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400', 50),
            ('Phone Stand', 'Adjustable phone holder', 24.99, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400', 30),
            ('Mechanical Keyboard', 'RGB mechanical keyboard', 129.99, 'https://images.unsplash.com/photo-1587829191301-dec8891c4158?w=400', 20),
        ]
        for name, desc, price, img, stock in products:
            c.execute('INSERT INTO products (name, description, price, image_url, stock, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                      (name, desc, price, img, stock, datetime.now()))
    conn.commit()
    conn.close()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id, username, password, role FROM users WHERE username=? AND role=?', (username, 'admin'))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        return jsonify({'success': True, 'message': 'Admin login successful', 'role': 'admin', 'user_id': user[0]})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/request-otp', methods=['POST'])
def request_otp():
    data = request.json
    phone = data.get('phone')
    if not phone or not phone.isdigit() or len(phone) < 10:
        return jsonify({'error': 'Valid phone number required'}), 400
    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now() + timedelta(minutes=5)
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM otp WHERE phone=?', (phone,))
    c.execute('INSERT INTO otp (phone, otp, expires_at, created_at) VALUES (?, ?, ?, ?)',
              (phone, otp, expires_at, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'OTP sent to {phone}', 'otp': otp})

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT otp, expires_at FROM otp WHERE phone=? ORDER BY created_at DESC LIMIT 1', (phone,))
    otp_record = c.fetchone()
    if not otp_record or otp_record[0] != otp:
        conn.close()
        return jsonify({'error': 'Invalid OTP'}), 401
    if datetime.fromisoformat(otp_record[1]) < datetime.now():
        conn.close()
        return jsonify({'error': 'OTP expired'}), 401
    c.execute('SELECT id FROM users WHERE phone=?', (phone,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (username, phone, role, created_at) VALUES (?, ?, ?, ?)',
                  (f'customer_{phone}', phone, 'customer', datetime.now()))
        conn.commit()
        user_id = c.lastrowid
    else:
        user_id = user[0]
    c.execute('DELETE FROM otp WHERE phone=?', (phone,))
    conn.commit()
    conn.close()
    session['user_id'] = user_id
    session['phone'] = phone
    session['role'] = 'customer'
    return jsonify({'success': True, 'message': 'Login successful', 'role': 'customer', 'user_id': user_id})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/auth/session', methods=['GET'])
def get_session_info():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_id': session.get('user_id'), 'username': session.get('username'), 'role': session.get('role')})
    return jsonify({'authenticated': False})

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(products)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id=?', (product_id,))
    product = c.fetchone()
    conn.close()
    if product:
        return jsonify(dict(product))
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT c.id, c.product_id, c.quantity, p.name, p.price, p.image_url
                 FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=?''', (user_id,))
    cart_items = [dict(row) for row in c.fetchall()]
    conn.close()
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    return jsonify({'items': cart_items, 'total': round(total, 2), 'count': len(cart_items)})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    if not product_id or quantity < 1:
        return jsonify({'error': 'Invalid product or quantity'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT stock FROM products WHERE id=?', (product_id,))
    product = c.fetchone()
    if not product or product[0] < quantity:
        conn.close()
        return jsonify({'error': 'Product not available'}), 400
    c.execute('SELECT id, quantity FROM cart WHERE user_id=? AND product_id=?', (user_id, product_id))
    cart_item = c.fetchone()
    if cart_item:
        c.execute('UPDATE cart SET quantity=? WHERE id=?', (cart_item[1] + quantity, cart_item[0]))
    else:
        c.execute('INSERT INTO cart (user_id, product_id, quantity, added_at) VALUES (?, ?, ?, ?)',
                  (user_id, product_id, quantity, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Product added to cart'})

@app.route('/api/cart/update/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    quantity = data.get('quantity')
    if quantity is None or quantity < 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    if quantity == 0:
        c.execute('DELETE FROM cart WHERE id=?', (cart_id,))
    else:
        c.execute('UPDATE cart SET quantity=? WHERE id=?', (quantity, cart_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Cart updated'})

@app.route('/api/cart/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE id=?', (cart_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Item removed'})

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Cart cleared'})

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    payment_method = data.get('payment_method', 'credit_card')
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''SELECT c.product_id, c.quantity, p.price, p.stock
                 FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=?''', (user_id,))
    cart_items = c.fetchall()
    if not cart_items:
        conn.close()
        return jsonify({'error': 'Cart is empty'}), 400
    total = sum(item[1] * item[2] for item in cart_items)
    for product_id, quantity, price, stock in cart_items:
        if stock < quantity:
            conn.close()
            return jsonify({'error': f'Insufficient stock'}), 400
    c.execute('INSERT INTO orders (user_id, total_amount, status, payment_method, created_at) VALUES (?, ?, ?, ?, ?)',
              (user_id, total, 'pending', payment_method, datetime.now()))
    order_id = c.lastrowid
    for product_id, quantity, price, stock in cart_items:
        c.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                  (order_id, product_id, quantity, price))
        c.execute('UPDATE products SET stock = stock - ? WHERE id=?', (quantity, product_id))
    c.execute('DELETE FROM cart WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': order_id, 'total_amount': total})

@app.route('/api/orders/process-payment', methods=['POST'])
def process_payment():
    data = request.json
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Order ID required'}), 400
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?', ('completed', order_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'order_id': order_id, 'transaction_id': f"TXN_{order_id}"})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT o.id, o.total_amount, o.status, o.payment_method, o.created_at
                 FROM orders o WHERE o.user_id=? ORDER BY o.created_at DESC''', (user_id,))
    orders = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE id=? AND user_id=?', (order_id, user_id))
    order = c.fetchone()
    if not order:
        conn.close()
        return jsonify({'error': 'Order not found'}), 404
    c.execute('''SELECT oi.product_id, oi.quantity, oi.price, p.name, p.image_url
                 FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id=?''', (order_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'order': dict(order), 'items': items})

if __name__ == '__main__':
    init_db()
    seed_sample_data()
    app.run(debug=True, port=5000)