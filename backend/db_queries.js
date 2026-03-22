# ProShop — Backend API → PostgreSQL Query Map
# Every API route the frontend calls, with the exact SQL to use.
# Paste into your Express/Flask/FastAPI backend.
# ============================================================
# Stack assumed: Node.js + Express + pg (node-postgres)
# ============================================================

const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production'
       ? { rejectUnauthorized: false }   // Render requires this
       : false
});


// ── HELPER ────────────────────────────────────────────────────
const query = (text, params) => pool.query(text, params);


// ============================================================
//  AUTH ROUTES
// ============================================================

// POST /api/auth/admin-login
// Body: { username, password }
async function adminLogin(username, password) {
  const { rows } = await query(
    `SELECT id, username
     FROM admins
     WHERE username = $1
       AND password_hash = crypt($2, password_hash)`,
    [username, password]
  );
  return rows[0] || null;   // null = wrong credentials
}

// POST /api/auth/register
// Body: { phone, password }
async function registerCustomer(phone, password) {
  const { rows } = await query(
    `INSERT INTO users (phone, password_hash)
     VALUES ($1, crypt($2, gen_salt('bf', 10)))
     RETURNING id, phone`,
    [phone, password]
  );
  return rows[0];
}

// POST /api/auth/customer-login
// Body: { phone, password }
async function customerLogin(phone, password) {
  const { rows } = await query(
    `SELECT id, phone, apartment, address, pincode
     FROM users
     WHERE phone = $1
       AND password_hash = crypt($2, password_hash)`,
    [phone, password]
  );
  return rows[0] || null;
}

// POST /api/auth/request-otp
// Body: { phone }
async function createOTP(phone) {
  // Auto-register if first time
  await query(
    `INSERT INTO users (phone, password_hash)
     VALUES ($1, crypt(gen_random_uuid()::text, gen_salt('bf', 10)))
     ON CONFLICT (phone) DO NOTHING`,
    [phone]
  );
  const otp = Math.floor(1000 + Math.random() * 9000).toString();
  await query(
    `INSERT INTO otp_store (phone, otp, expires_at)
     VALUES ($1, $2, NOW() + INTERVAL '10 minutes')`,
    [phone, otp]
  );
  return otp;
}

// POST /api/auth/verify-otp
// Body: { phone, otp }
async function verifyOTP(phone, otp) {
  const { rows } = await query(
    `UPDATE otp_store
     SET used = TRUE
     WHERE phone = $1
       AND otp   = $2
       AND used  = FALSE
       AND expires_at > NOW()
     RETURNING id`,
    [phone, otp]
  );
  if (!rows.length) return null;
  // Return user
  const user = await query(
    `SELECT id, phone, apartment, address, pincode
     FROM users WHERE phone = $1`,
    [phone]
  );
  return user.rows[0] || null;
}

// POST /api/auth/save-address
// Headers: X-User-ID
// Body: { pincode, address, apartment }
async function saveAddress(userId, pincode, address, apartment) {
  await query(
    `UPDATE users
     SET apartment = $2, address = $3, pincode = $4
     WHERE id = $1`,
    [userId, apartment, address, pincode]
  );
}


// ============================================================
//  PRODUCT ROUTES
// ============================================================

// GET /api/products  (public)
async function getAllProducts() {
  const { rows } = await query(
    `SELECT id, name, description, price, stock, max_qty,
            delivery_fee, image_url
     FROM products
     WHERE is_active = TRUE
     ORDER BY id ASC`
  );
  return rows;
}

// POST /api/products  (admin only)
// Body: { name, description, price, stock, max_qty, delivery_fee, image_url }
async function createProduct(data) {
  const { rows } = await query(
    `INSERT INTO products
       (name, description, price, stock, max_qty, delivery_fee, image_url)
     VALUES ($1,$2,$3,$4,$5,$6,$7)
     RETURNING *`,
    [data.name, data.description, data.price,
     data.stock, data.max_qty, data.delivery_fee, data.image_url]
  );
  return rows[0];
}

// PUT /api/products/:id  (admin only)
async function updateProduct(id, data) {
  const { rows } = await query(
    `UPDATE products
     SET name=$2, description=$3, price=$4,
         stock=$5, max_qty=$6, delivery_fee=$7, image_url=$8
     WHERE id=$1
     RETURNING *`,
    [id, data.name, data.description, data.price,
     data.stock, data.max_qty, data.delivery_fee, data.image_url]
  );
  return rows[0];
}

// DELETE /api/products/:id  (admin only)
async function deleteProduct(id) {
  // Soft delete — keeps order history intact
  await query(
    `UPDATE products SET is_active = FALSE WHERE id = $1`,
    [id]
  );
}


// ============================================================
//  ORDER ROUTES
// ============================================================

// POST /api/orders/create
// Headers: X-User-ID
// Body: { items:[{id,qty}], delivery_fee, address, pincode, apartment, payment_method }
async function createOrder(userId, body) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // 1. Fetch product prices (never trust client prices)
    const ids = body.items.map(i => i.id);
    const { rows: products } = await client.query(
      `SELECT id, name, price, stock, max_qty
       FROM products
       WHERE id = ANY($1) AND is_active = TRUE`,
      [ids]
    );
    const productMap = Object.fromEntries(products.map(p => [p.id, p]));

    // 2. Validate quantities & compute total
    let subtotal = 0;
    for (const item of body.items) {
      const p = productMap[item.id];
      if (!p) throw new Error(`Product ${item.id} not found`);
      if (item.qty > p.max_qty) throw new Error(`Max qty for ${p.name} is ${p.max_qty}`);
      if (item.qty > p.stock)   throw new Error(`${p.name} is out of stock`);
      subtotal += p.price * item.qty;
    }
    const total = subtotal + Number(body.delivery_fee || 0);

    // 3. Insert order
    const { rows: [order] } = await client.query(
      `INSERT INTO orders
         (user_id, total_amount, delivery_fee, payment_method,
          delivery_address, delivery_pincode, delivery_apartment)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       RETURNING id`,
      [userId, total, body.delivery_fee, body.payment_method || 'gpay',
       body.address, body.pincode, body.apartment]
    );

    // 4. Insert order items + decrement stock
    for (const item of body.items) {
      const p = productMap[item.id];
      await client.query(
        `INSERT INTO order_items (order_id, product_id, name, price, quantity)
         VALUES ($1,$2,$3,$4,$5)`,
        [order.id, p.id, p.name, p.price, item.qty]
      );
      await client.query(
        `UPDATE products SET stock = stock - $1 WHERE id = $2`,
        [item.qty, p.id]
      );
    }

    await client.query('COMMIT');
    return order.id;
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }
}

// POST /api/orders/confirm-payment
// Headers: X-User-ID
// Body: { order_id, upi_ref }
async function confirmPayment(userId, orderId, upiRef) {
  const { rows } = await query(
    `UPDATE orders
     SET upi_ref = $3, status = 'confirmed'
     WHERE id = $1 AND user_id = $2
     RETURNING id`,
    [orderId, userId, upiRef]
  );
  return rows[0] || null;
}

// GET /api/orders   (customer — own orders only)
// Headers: X-User-ID
async function getCustomerOrders(userId) {
  const { rows } = await query(
    `SELECT * FROM v_customer_orders WHERE user_id = $1`,
    [userId]
  );
  return rows;
}


// ============================================================
//  ADMIN ROUTES
// ============================================================

// GET /api/admin/orders
async function getAllOrders() {
  const { rows } = await query(`SELECT * FROM v_admin_orders`);
  return rows;
}

// PUT /api/admin/orders/:id/status
// Body: { status }
async function updateOrderStatus(orderId, status) {
  const valid = ['confirmed','preparing','on_the_way','delivered','cancelled'];
  if (!valid.includes(status)) throw new Error('Invalid status');
  const { rows } = await query(
    `UPDATE orders SET status = $2 WHERE id = $1 RETURNING id`,
    [orderId, status]
  );
  return rows[0] || null;
}

// GET /api/admin/users
async function getAllUsers() {
  const { rows } = await query(
    `SELECT id, phone, apartment, address, pincode, created_at
     FROM users
     ORDER BY created_at DESC`
  );
  return rows;
}


// ============================================================
//  OTP CLEANUP JOB (run every hour via setInterval or cron)
// ============================================================
async function cleanExpiredOTPs() {
  await query(`DELETE FROM otp_store WHERE expires_at < NOW() OR used = TRUE`);
}
// setInterval(cleanExpiredOTPs, 60 * 60 * 1000);


module.exports = {
  pool,
  adminLogin, registerCustomer, customerLogin,
  createOTP, verifyOTP, saveAddress,
  getAllProducts, createProduct, updateProduct, deleteProduct,
  createOrder, confirmPayment, getCustomerOrders,
  getAllOrders, updateOrderStatus, getAllUsers,
  cleanExpiredOTPs
};
