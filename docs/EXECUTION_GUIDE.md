# 📖 ProShop - Complete Execution Guide (Step by Step)

## Table of Contents
1. Prerequisites Check
2. Installation
3. Running the Application
4. Testing All Features
5. Troubleshooting
6. Customization
7. Next Steps

---

## Part 1: Prerequisites Check ✅

### What You Need:
- ✅ Windows/Mac/Linux Computer
- ✅ Python 3.8 or higher
- ✅ Internet connection (optional, for images)
- ✅ Any modern web browser
- ✅ Text editor (Notepad, VS Code, etc.)

### Verify Python Installation

**Windows:**
1. Open Command Prompt (Win+R, type `cmd`, press Enter)
2. Type: `python --version`
3. You should see: `Python 3.x.x`

**Mac:**
1. Open Terminal (Cmd+Space, type `terminal`)
2. Type: `python3 --version`
3. You should see: `Python 3.x.x`

**Linux:**
1. Open Terminal (Ctrl+Alt+T)
2. Type: `python3 --version`
3. You should see: `Python 3.x.x`

⚠️ **If you don't have Python:**
- Download from https://www.python.org/downloads/
- During installation, CHECK "Add Python to PATH"
- Restart your computer
- Verify installation again

---

## Part 2: Installation 🛠️

### Step 2.1: Extract/Download Files

You should have these files:
- `app.py` - Backend server
- `index.html` - Frontend website
- `requirements.txt` - Dependencies list
- `start.bat` - Quick start (Windows)
- `start.sh` - Quick start (Mac/Linux)
- `README.md` - Documentation
- `SETUP_GUIDE.md` - Detailed setup
- `QUICK_START.md` - Quick reference

### Step 2.2: Open Project Folder in Terminal

**Windows:**
1. Open File Explorer
2. Navigate to your project folder
3. Hold Shift + Right-click in empty space
4. Click "Open PowerShell window here" or "Open command window here"

**Mac:**
1. Open Finder
2. Navigate to your project folder
3. Right-click → Services → New Terminal at Folder

**Linux:**
1. Open Files
2. Navigate to your project folder
3. Right-click → Open Terminal Here

You should see something like:
```
C:\Users\YourName\Desktop\proshop>  (Windows)
or
~/projects/proshop $                 (Mac/Linux)
```

### Step 2.3: Install Python Dependencies

**All Platforms (Windows/Mac/Linux):**

Copy and paste this command:
```bash
pip install -r requirements.txt
```

or for Mac/Linux:
```bash
pip3 install -r requirements.txt
```

**Wait for it to finish. You'll see:**
```
Successfully installed Flask-2.3.3 flask-cors-4.0.0 Werkzeug-2.3.7
```

⏱️ This takes 1-2 minutes.

### Step 2.4: Verify Installation

Test if everything is installed:

**Windows:**
```bash
python -m flask --version
```

**Mac/Linux:**
```bash
python3 -m flask --version
```

You should see: `Flask 2.3.3`

---

## Part 3: Running the Application 🚀

### Option A: Using Quick Start Script (Easiest)

**Windows:**
1. Double-click `start.bat`
2. A new window opens
3. Wait for: `Press Ctrl+C to stop the server`

**Mac/Linux:**
1. Right-click `start.sh`
2. Select "Open" → "Open in Terminal"
3. (Or in Terminal: `./start.sh`)
4. Wait for: `Press Ctrl+C to stop the server`

### Option B: Manual Start (More Control)

**Windows:**
```bash
python app.py
```

**Mac/Linux:**
```bash
python3 app.py
```

### What You Should See:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * Restarting with reloader
```

✅ **Server is running!** Keep this terminal open.

---

## Part 4: Opening the Frontend 🌐

### Option A: Double-Click Method (Easiest)

1. In File Explorer/Finder, find `index.html`
2. Double-click it
3. Your default browser opens automatically
4. Website loads at `file:///...`

### Option B: Browser Method

1. Open your browser (Chrome, Firefox, Safari, Edge)
2. Address bar: `Ctrl+L` or click
3. Paste: `file:///C:/Users/YourName/Desktop/proshop/index.html`
4. Replace path with your actual location
5. Press Enter

### Option C: VS Code Live Server (Recommended)

1. Open project folder in VS Code
2. Install "Live Server" extension
3. Right-click `index.html`
4. Click "Open with Live Server"
5. Browser opens at `http://localhost:5500`

### You Should See:

```
┌─────────────────────────────────────┐
│   ProShop 🛍️                        │
│  Welcome to ProShop                 │
│  Sign in to continue shopping       │
│                                     │
│  [Admin Login]  [Customer Login]   │
│                                     │
│  Username: [____________]           │
│  Password: [____________]           │
│  [Login Button]                     │
│                                     │
│  Demo: admin / admin123            │
└─────────────────────────────────────┘
```

---

## Part 5: Testing All Features ✅

### 5.1: Admin Login Test

**Steps:**
1. Frontend page shows login form
2. Click "Admin Login" tab (if not already selected)
3. Username field: Type `admin`
4. Password field: Type `admin123`
5. Click blue "Login" button
6. Wait 1-2 seconds

**Expected Result:**
```
✅ Page changes to products page
✅ Header shows "Admin" or "admin"
✅ See 6 products in a grid
✅ Each product has name, image, price, "Add to Cart" button
```

**If it doesn't work:**
- Check browser console (F12 → Console)
- Check terminal where Flask is running
- Verify Flask is still running (should say "Running on...")

### 5.2: Product Browsing Test

**You should see:**
- ✅ "Featured Products" heading
- ✅ Grid of 6 products:
  1. Laptop Pro 15 - $999.99
  2. Wireless Earbuds - $149.99
  3. Smart Watch - $299.99
  4. USB-C Cable - $19.99
  5. Phone Stand - $24.99
  6. Mechanical Keyboard - $129.99
- ✅ Product images loading
- ✅ "Add to Cart" buttons on each

### 5.3: Shopping Cart Test

**Steps:**
1. Click "Add to Cart" on any product
2. Green notification appears: "✓ Product added to cart!"
3. Cart icon (🛒) now shows `1` in red badge
4. Click cart icon (top right)

**Expected Result:**
```
┌─────────────────────┐
│ Shopping Cart     × │
├─────────────────────┤
│ Product name        │
│ $99.99              │
│ - 1 +  [Remove]     │
│                     │
│ Total: $99.99       │
│ [Proceed to Check] │
└─────────────────────┘
```

**Test Actions:**
- Click `+` button → Quantity increases to 2, total updates
- Click `-` button → Quantity decreases back to 1
- Click "Remove" → Item removed, cart empty
- Click `×` button → Cart sidebar closes

### 5.4: Checkout Test

**Steps:**
1. Add product to cart (if empty)
2. Click "Proceed to Checkout" button
3. Wait for checkout page to load

**Expected Result:**
```
Checkout page with 3 columns:
1. Left side: Order items + Address form
2. Right side: Order summary
   - Subtotal: $99.99
   - Shipping: $10.00
   - Tax (10%): $11.00
   - Total: $120.99
```

**Fill Form:**
- Full Name: `John Doe`
- Email: `john@example.com`
- Phone: `9876543210`
- Address: `123 Main Street`
- City: `New York`
- Postal Code: `10001`

**Select Payment:**
- Click 💳 (Card) button
- Form appears with card fields

### 5.5: Order Placement Test

**Steps:**
1. Complete checkout form
2. Select payment method
3. Click "Place Order" button
4. Wait 1-2 seconds

**Expected Result:**
```
✅ Page changes to confirmation
✅ Shows large checkmark (✓)
✅ Message: "Order Confirmed!"
✅ Order ID: #1
✅ Total: $120.99
✅ "Continue Shopping" button
```

### 5.6: Customer Login Test

**Steps:**
1. Click "Continue Shopping" or "ProShop" logo
2. Click blue "Login" button (top right)
3. Click "Customer Login" tab
4. Phone field: `9876543210`
5. Click "Send OTP"

**Expected Result:**
```
✅ Alert shows OTP: [6-digit number]
✅ Form changes to OTP entry field
```

**Continue:**
1. Copy OTP from alert
2. OTP field: Paste the 6-digit OTP (or `123456` for demo)
3. Click "Verify OTP"

**Expected Result:**
```
✅ Login successful
✅ Products page loads
✅ Header shows phone number
✅ Logout button visible (top right)
```

---

## Part 6: Browser Troubleshooting Guide 🔧

### Issue: Page shows "Loading..." forever

**Cause:** Flask backend not running
**Solution:**
1. Open terminal with Flask
2. Check if it says "Running on..."
3. If not, start it: `python app.py`
4. In browser, press Ctrl+F5 (hard refresh)

### Issue: Products don't load

**Cause:** Database issue
**Solution:**
1. Close Flask: Press Ctrl+C
2. Delete `ecommerce.db` file
3. Restart Flask: `python app.py`
4. Refresh browser: Ctrl+F5

### Issue: OTP not showing

**Cause:** Browser alert disabled or missed
**Solution:**
1. Check browser popup: Small white window might have appeared
2. Check terminal where Flask runs: OTP printed there
3. Look in browser console: F12 → Console tab

### Issue: "Cannot reach server"

**Cause:** Flask crashed or port busy
**Solution:**
1. Check terminal with Flask
2. Look for red errors
3. Restart: Close terminal and run `python app.py` again
4. Different port: Edit `app.py` last line, change 5000 to 8000

### Issue: Form won't submit

**Cause:** Missing information or JavaScript error
**Solution:**
1. Make sure all fields are filled
2. Open console: F12 → Console tab
3. Look for red error messages
4. Try different browser

---

## Part 7: Understanding the File Structure 📁

### Backend (Python)

**File: `app.py` (900 lines)**

Structure:
```
app.py
├── Imports (Flask, database tools)
├── Configuration (secret key, CORS)
├── Database setup
│   ├── Initialize tables (users, products, cart, orders)
│   └── Create sample data
├── Routes
│   ├── Health check
│   ├── Authentication (login, OTP, logout)
│   ├── Products (list, details)
│   ├── Cart (add, remove, update)
│   └── Orders (create, payment, history)
└── Main (if __name__ == '__main__')
```

**Key Functions:**
- `init_db()` - Creates database tables
- `seed_sample_data()` - Adds products
- `@app.route()` - Defines API endpoints
- `apiCall()` - Helper for API requests

### Frontend (HTML/CSS/JavaScript)

**File: `index.html` (1500 lines)**

Structure:
```
index.html
├── Head section
│   ├── Meta tags (title, viewport)
│   └── Styles (3500+ lines of CSS)
├── Body
│   ├── Header (navigation, cart icon)
│   ├── Main content (pages)
│   │   ├── Login page
│   │   ├── Home (products)
│   │   ├── Checkout
│   │   └── Confirmation
│   ├── Cart sidebar
│   └── Scripts (800+ lines of JavaScript)
└── JavaScript
    ├── API calls (fetch)
    ├── Authentication functions
    ├── Cart management
    ├── DOM manipulation
    └── Event handlers
```

**Key Functions:**
- `apiCall()` - Sends requests to Flask
- `loadProducts()` - Displays products
- `addToCart()` - Adds item to cart
- `placeOrder()` - Creates order

---

## Part 8: Customization Guide 🎨

### Change Admin Password

In `app.py`, line ~60:
```python
c.execute('INSERT INTO users (username, password, phone, role, created_at) VALUES (?, ?, ?, ?, ?)',
          ('admin', hashed_pwd, '0000000000', 'admin', datetime.now()))
```

Replace with:
```python
c.execute('INSERT INTO users (username, password, phone, role, created_at) VALUES (?, ?, ?, ?, ?)',
          ('admin', generate_password_hash('your_new_password'), '0000000000', 'admin', datetime.now()))
```

### Add New Product

In `app.py`, `seed_sample_data()` function, line ~75:
```python
products = [
    ('Laptop Pro 15', 'High-performance laptop', 999.99, 'image_url', 10),
    # Add new product here:
    ('Headphones', 'Wireless headphones', 199.99, 'image_url', 5),
]
```

### Change Website Colors

In `index.html`, search for `:root {` (around line 25):
```css
:root {
    --primary: #2563eb;        /* Blue */
    --secondary: #f59e0b;      /* Orange */
    --success: #10b981;        /* Green */
    --danger: #ef4444;         /* Red */
    /* Change these colors */
}
```

### Change Website Title

In `index.html`, line 5:
```html
<title>ProShop - E-Commerce Platform</title>
<!-- Change to: -->
<title>My Shop - Your Store Name</title>
```

### Change Frontend Port (for development)

In `index.html`, find line with `const API_BASE`:
```javascript
const API_BASE = 'http://localhost:5000/api';
// Change 5000 to different port if needed
const API_BASE = 'http://localhost:8000/api';
```

And in `app.py`, last line:
```python
app.run(debug=True, port=8000)  # Change port here too
```

---

## Part 9: Database Management 💾

### View Database

Download free SQLite browser:
- DB Browser for SQLite: https://sqlitebrowser.org/

**Steps:**
1. Download and install
2. File → Open → Select `ecommerce.db`
3. See all tables and data

### Reset Database

**Option 1: Delete and Regenerate**
```bash
# Delete the database
rm ecommerce.db      # Mac/Linux
del ecommerce.db     # Windows

# Restart Flask - it creates new one
python app.py
```

**Option 2: Keep Only Some Products**
1. Delete `ecommerce.db`
2. Edit `app.py` `seed_sample_data()` function
3. Remove products you don't want
4. Restart Flask

### Backup Database

```bash
# Windows
copy ecommerce.db ecommerce_backup.db

# Mac/Linux
cp ecommerce.db ecommerce_backup.db
```

---

## Part 10: Deployment 🌍

### Deploy to Heroku (Free Tier)

**Prerequisites:**
- Heroku account (free at heroku.com)
- Git installed

**Steps:**
1. Create `Procfile` file:
```
web: gunicorn app:app
```

2. Install gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Push to Heroku:
```bash
git init
git add .
git commit -m "Initial commit"
heroku create
git push heroku main
```

### Deploy to Render (Free)

1. Push code to GitHub
2. Visit https://render.com
3. Connect GitHub account
4. Deploy automatically
5. Get live URL

### Run on Local Network

Allow other devices to access your app:

In `app.py`, change:
```python
app.run(debug=True, port=5000)
```

To:
```python
app.run(host='0.0.0.0', debug=True, port=5000)
```

Then find your IP:
- Windows: `ipconfig` (look for IPv4 Address)
- Mac/Linux: `ifconfig` (look for inet)

Example: `192.168.1.100`

Access from other devices: `http://192.168.1.100:5000`

---

## Part 11: Advanced Customization 🚀

### Add Real Payment Gateway (Stripe)

1. Sign up: https://stripe.com
2. Get API keys
3. Install: `pip install stripe`
4. Edit `process_payment()` in `app.py`

### Add Email Notifications

1. Install: `pip install flask-mail`
2. Configure email settings
3. Send confirmation emails

### Add User Profiles

1. Add profile fields to users table
2. Create profile page
3. Update registration process

### Add Product Search

1. Add search bar to HTML
2. Create search API endpoint
3. Filter products by query

---

## Part 12: Performance Tips ⚡

### Make It Faster

```python
# In app.py - Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Cache products (don't change often)
@app.route('/api/products')
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_products():
    # ...
```

### Optimize Images

```python
# Resize images before storing
from PIL import Image
img = Image.open('product.jpg')
img.thumbnail((400, 400))
img.save('product_optimized.jpg')
```

### Add Pagination

```python
# Limit products per page
@app.route('/api/products')
def get_products():
    page = request.args.get('page', 1, type=int)
    limit = 10
    offset = (page - 1) * limit
    # ...
```

---

## Part 13: Monitoring & Debugging 🔍

### Enable Detailed Logging

In `app.py`, add:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Debug message")
app.logger.info("Info message")
app.logger.error("Error message")
```

### Monitor API Calls

**In Browser Console (F12):**
```javascript
// See all API responses
fetch(url).then(r => r.json()).then(d => console.log(d))
```

### Check Database State

In terminal while Flask running:
```python
>>> import sqlite3
>>> conn = sqlite3.connect('ecommerce.db')
>>> c = conn.cursor()
>>> c.execute('SELECT * FROM users')
>>> print(c.fetchall())
```

---

## Part 14: Security Checklist 🔐

Before Production:

- [ ] Change `SECRET_KEY` to random string
- [ ] Set `debug=False`
- [ ] Use HTTPS
- [ ] Validate all inputs
- [ ] Use strong passwords
- [ ] Add CSRF protection
- [ ] Implement real payment gateway
- [ ] Add rate limiting
- [ ] Use environment variables
- [ ] Regular security updates

---

## Summary Table

| Task | Windows | Mac/Linux | Time |
|------|---------|----------|------|
| Install Python | Download installer | `brew install python3` | 5 min |
| Install dependencies | `pip install -r requirements.txt` | `pip3 install -r requirements.txt` | 2 min |
| Start backend | `python app.py` | `python3 app.py` | 10 sec |
| Open frontend | Double-click `index.html` | Double-click `index.html` | 5 sec |
| Admin login | admin/admin123 | admin/admin123 | 30 sec |
| Test products | Click "Add to Cart" | Click "Add to Cart" | 1 min |
| Checkout | Fill form, place order | Fill form, place order | 2 min |

---

## Final Checklist ✅

- [x] Python installed and verified
- [x] Dependencies installed
- [x] Flask server running
- [x] Frontend loads in browser
- [x] Admin login works
- [x] Products display
- [x] Cart functionality works
- [x] Checkout successful
- [x] Order confirmation appears
- [x] Customer OTP login works

---

**Congratulations! You now have a fully functional e-commerce application! 🎉**

Next steps:
1. Explore the code
2. Customize it for your needs
3. Add new features
4. Deploy to production
5. Share with others!

---

Need more help? Check:
- README.md - Overview
- SETUP_GUIDE.md - Detailed setup
- QUICK_START.md - Quick reference
- Code comments in app.py and index.html
