# 🚀 ProShop - Quick Start Guide (5 Minutes)

## Step 1️⃣: Install Python Dependencies (1 minute)

Open Command Prompt/Terminal in your project folder and run:

### Windows:
```bash
pip install -r requirements.txt
```

### Mac/Linux:
```bash
pip3 install -r requirements.txt
```

**What gets installed:**
- Flask (web server)
- Flask-CORS (cross-origin support)
- Werkzeug (security tools)

---

## Step 2️⃣: Start the Backend Server (10 seconds)

**Windows:**
```bash
python app.py
```

**Mac/Linux:**
```bash
python3 app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

✅ **Keep this terminal open!** The backend must stay running.

---

## Step 3️⃣: Open the Frontend (5 seconds)

Choose ONE method:

### Method A: Direct (Easiest)
1. Find `index.html` in your project folder
2. Double-click it
3. Browser opens automatically

### Method B: VS Code Live Server (Recommended for Development)
1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Click "Open with Live Server"
4. Browser opens at `http://localhost:5500`

### Method C: Manual Browser
1. Open your browser (Chrome, Firefox, Safari, Edge)
2. Press `Ctrl+L` (or click address bar)
3. Type: `file:///C:/Users/YourUsername/path/to/index.html`
4. Replace path with your actual project location

---

## 🎮 Try It Out!

### Admin Login
1. Click **"Admin Login"** tab
2. Username: `admin`
3. Password: `admin123`
4. Click **Login**
5. ✅ You should see products page

### Customer Login
1. Click **"Customer Login"** tab
2. Enter any 10-digit number: `9876543210`
3. Click **Send OTP**
4. Copy OTP from browser alert (or check terminal)
5. Enter OTP: `123456` (or the one shown)
6. Click **Verify OTP**
7. ✅ You should see products page

### Shopping
1. Click **Add to Cart** on any product
2. Click 🛒 (cart icon) top right
3. Adjust quantities or remove items
4. Click **Proceed to Checkout**
5. Fill in your details
6. Select payment method
7. Click **Place Order**
8. ✅ See confirmation!

---

## 🔧 Troubleshooting (Most Common Issues)

### "Connection Refused" or "Cannot Connect"
```
❌ Error: Connection refused on localhost:5000
✅ Solution: 
1. Check if 'python app.py' is running in another terminal
2. If port 5000 is busy, change it in app.py (last line)
```

### "CORS Error" or "No 'Access-Control-Allow-Origin'"
```
❌ Error: CORS error in browser console
✅ Solution:
1. Make sure Flask is running with debug=True
2. Flask-CORS should handle this automatically
3. Try refreshing the page (Ctrl+F5)
```

### "Products Not Loading"
```
❌ Error: Products grid shows "Loading..." forever
✅ Solution:
1. Delete 'ecommerce.db' file
2. Restart 'python app.py' to recreate database
3. Refresh browser page (Ctrl+F5)
```

### "OTP Not Showing"
```
❌ Error: No OTP appears after clicking "Send OTP"
✅ Solution:
1. Check browser console: Press F12 → Console tab
2. Check terminal where 'python app.py' is running
3. OTP is shown in alerts in demo mode
```

### "Database is Locked"
```
❌ Error: database is locked
✅ Solution:
1. Close all instances of the app (all terminals/browsers)
2. Delete 'ecommerce.db' file
3. Restart 'python app.py'
```

---

## 📱 Quick File Overview

| File | Purpose | Edit? |
|------|---------|-------|
| `app.py` | Flask backend & API routes | Only if adding features |
| `index.html` | Website (HTML/CSS/JS) | Only if changing design |
| `requirements.txt` | Python dependencies | Only if adding packages |
| `ecommerce.db` | Database (auto-created) | Don't edit directly |
| `start.bat` | Windows quick start | Use it instead of typing commands |
| `start.sh` | Mac/Linux quick start | Use it instead of typing commands |

---

## 🌐 Testing All Features

### ✅ Feature Checklist

- [ ] Admin Login (admin/admin123)
- [ ] Customer Login (phone + OTP)
- [ ] View Products
- [ ] Add Product to Cart
- [ ] View Cart (click 🛒 icon)
- [ ] Update Cart Quantity
- [ ] Remove Item from Cart
- [ ] Proceed to Checkout
- [ ] Fill Delivery Info
- [ ] Select Payment Method
- [ ] Place Order
- [ ] See Order Confirmation

---

## 🎯 Next Steps After Getting It Running

1. **Explore the Code**
   - Read `app.py` to understand backend
   - Read `index.html` to understand frontend
   - Comments explain complex parts

2. **Customize It**
   - Change colors, fonts, layout in `index.html` CSS section
   - Add more products in `app.py` `seed_sample_data()` function
   - Change login credentials

3. **Add Features**
   - User profiles
   - Product search/filtering
   - Wishlist
   - Email notifications

4. **Deploy It**
   - Follow SETUP_GUIDE.md deployment section
   - Use Heroku, Render, or AWS
   - Share with friends!

---

## 📊 Architecture Overview

```
Your Computer
│
├── Backend (Flask) - app.py
│   ├── Receives requests from frontend
│   ├── Manages database (ecommerce.db)
│   ├── Processes orders & payments
│   └── Sends data back to frontend
│
└── Frontend (Browser) - index.html
    ├── Shows products & shopping cart
    ├── Gets user input (login, checkout)
    ├── Sends requests to backend
    └── Displays results
```

---

## 💻 Command Reference

### Starting the Application

**Windows:**
```bash
# Option 1: Manual start
python app.py

# Option 2: Use quick start script
start.bat
```

**Mac/Linux:**
```bash
# Option 1: Manual start
python3 app.py

# Option 2: Use quick start script
./start.sh
```

### Stopping the Server
Press `Ctrl+C` in the terminal running `python app.py`

### Resetting the Database
```bash
# Delete the database file
rm ecommerce.db  # Mac/Linux
del ecommerce.db # Windows

# Restart the server - database will be recreated
python app.py
```

---

## 🔐 Default Credentials

Save these for testing:

```
┌─ ADMIN LOGIN ─────────────┐
│ Username: admin           │
│ Password: admin123        │
└───────────────────────────┘

┌─ CUSTOMER LOGIN ──────────┐
│ Phone: 9876543210         │
│ (Any 10+ digit number)    │
│ OTP: 123456               │
│ (Shown in alert/terminal) │
└───────────────────────────┘
```

---

## 📞 Getting Help

### If Something Breaks:

1. **Check the Console (F12)**
   - Press F12 in browser
   - Click "Console" tab
   - Look for red error messages

2. **Check Terminal Output**
   - Look at terminal where `python app.py` is running
   - Red text = errors

3. **Common Fixes**
   - Refresh page: `Ctrl+F5` (hard refresh)
   - Restart backend: Close terminal, run `python app.py` again
   - Clear cache: Settings → Clear browsing data
   - Delete database: Delete `ecommerce.db` file

4. **Need More Help?**
   - Read SETUP_GUIDE.md
   - Read README.md
   - Check app.py comments
   - Check index.html comments

---

## ✨ Pro Tips

💡 **Use VS Code**
- Much better for development
- Install "Python" extension
- Use Live Server for frontend
- Built-in terminal for backend

💡 **Keep Terminal Visible**
- See all API calls and errors
- Watch database operations
- Monitor OTP generation

💡 **Use Browser DevTools (F12)**
- Network tab: See API calls
- Console: See JavaScript errors
- Inspector: Examine HTML/CSS

💡 **Test with Multiple Browsers**
- Chrome, Firefox, Safari, Edge
- All should work the same
- Good practice for development

---

## 🎉 You're All Set!

Your e-commerce app is ready to use!

### Quick Recap:
```
1. pip install -r requirements.txt    ✓ Done once
2. python app.py                       ✓ Keep running
3. Open index.html in browser          ✓ Start shopping
```

### That's It! 🚀

The app is fully functional with:
- ✅ Admin & Customer Login
- ✅ 6 Sample Products
- ✅ Shopping Cart
- ✅ Checkout Process
- ✅ Order Confirmation
- ✅ Professional UI

---

## 📈 Performance Notes

- **First load:** 1-2 seconds (normal)
- **Add to cart:** Instant
- **Checkout:** 1-2 seconds
- **Order placement:** 1-2 seconds

If slow, try:
- Close other browser tabs
- Restart `python app.py`
- Clear browser cache

---

## 🔄 Typical Workflow

```
Session 1: Admin checks what's in stock
├─ python app.py
├─ Open index.html
├─ Admin login (admin/admin123)
└─ Browse products

Session 2: Customer shops
├─ python app.py (same server)
├─ Open index.html
├─ Customer login (phone + OTP)
├─ Add items to cart
├─ Checkout
└─ See order confirmation

Session 3: Customer logs in again
├─ python app.py (same server)
├─ Open index.html
├─ Login with same phone
└─ Cart is empty (new session)
```

---

**Ready to go! Start with Step 1 above. Good luck! 🎉**
