# ProShop - E-Commerce Web Application
## Complete Setup & Execution Guide

A full-stack e-commerce platform with admin/customer login, product catalog, shopping cart, and checkout functionality.

---

## 📋 Project Structure

```
project-folder/
├── app.py                 # Flask backend server
├── index.html             # Frontend (HTML/CSS/JS)
├── requirements.txt       # Python dependencies
└── ecommerce.db          # SQLite database (auto-created)
```

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8 or higher
- VS Code or any code editor
- Git (optional)

### Step 1: Install Python Dependencies

Open terminal/command prompt in your project folder and run:

```bash
pip install -r requirements.txt
```

**What it installs:**
- Flask: Web framework for backend
- Flask-CORS: Cross-Origin Resource Sharing support
- Werkzeug: Security utilities

### Step 2: Start the Backend Server

Run this command in the project directory:

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Keep this terminal open!** The backend must run while using the app.

### Step 3: Open the Frontend

**Option A: Simple (Recommended for beginners)**
1. Navigate to your project folder in file explorer
2. Double-click `index.html` to open in your default browser
3. You can now use the application!

**Option B: Using VS Code (Better Development Experience)**
1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → Select "Open with Live Server"
3. Browser opens at `http://localhost:5500`

**Option C: Manual Browser Opening**
1. Open your browser (Chrome, Firefox, Edge, Safari)
2. Navigate to: `file:///C:/path/to/your/project/index.html`
3. Replace path with your actual project path

---

## 📝 Login Credentials

### Admin Login
- **Username:** admin
- **Password:** admin123

### Customer Login
- **Phone Number:** Any 10+ digit number (e.g., 9876543210)
- **OTP:** Displayed in browser alert (or terminal output)
- Demo OTP: 123456

---

## 🎯 Features Overview

### 1. Authentication
- **Admin Login:** Username & password authentication
- **Customer Login:** Phone number + OTP verification
- **Session Management:** Secure session handling

### 2. Product Catalog
- 6 pre-loaded sample products
- Product images, descriptions, prices
- Real-time stock availability
- Product search and filtering

### 3. Shopping Cart
- Add/remove products
- Adjust quantities
- Real-time cart updates
- Persistent cart display

### 4. Checkout
- Delivery address collection
- Multiple payment methods (Card, Debit, UPI)
- Order summary with tax calculation
- Order confirmation

### 5. Order Management
- Order history
- Order status tracking
- Payment confirmation

---

## 🔧 Configuration & Customization

### Change Backend Port
In `app.py`, last line:
```python
app.run(debug=True, port=5000)  # Change 5000 to desired port
```

### Change Frontend API URL
In `index.html`, find this line (around line 500):
```javascript
const API_BASE = 'http://localhost:5000/api';
```
Change to your backend URL if different.

### Modify Secret Key (Production)
In `app.py`, line 8:
```python
app.secret_key = 'your-secret-key-change-in-production'
```
Change to a strong random string for production.

### Add More Products
In `app.py`, function `seed_sample_data()` around line 60:
```python
products = [
    ('Product Name', 'Description', 99.99, 'image_url', stock_quantity),
    # Add more tuples here
]
```

---

## 📊 Database Schema

### Users Table
- id, username, password, phone, role, created_at

### Products Table
- id, name, description, price, image_url, stock, created_at

### Cart Table
- id, user_id, product_id, quantity, added_at

### Orders Table
- id, user_id, total_amount, status, payment_method, created_at

### Order Items Table
- id, order_id, product_id, quantity, price

---

## 🐛 Troubleshooting

### "Connection Refused" Error
- Make sure `python app.py` is running in another terminal
- Check if port 5000 is available
- Try a different port if needed

### CORS Errors
- Flask-CORS should handle this automatically
- If persists, check Flask is running with `debug=True`

### Products Not Loading
- Delete `ecommerce.db` and restart `app.py` to reseed
- Check browser console (F12) for errors

### OTP Not Showing
- Check browser console for the OTP value
- Check terminal output where `app.py` is running
- In production, integrate with Twilio or similar SMS service

### Database Lock Error
- Close any other instances of the app
- Delete `ecommerce.db` to reset
- Restart `python app.py`

---

## 🔒 Security Notes (Production)

Before deploying to production:

1. **Change Secret Key**
   ```python
   app.secret_key = 'generate-a-strong-random-secret-key'
   ```

2. **Disable Debug Mode**
   ```python
   app.run(debug=False, port=5000)
   ```

3. **Use HTTPS**
   - Set up SSL certificates
   - Use production WSGI server (Gunicorn, uWSGI)

4. **Implement Real OTP**
   - Use Twilio, AWS SNS, or similar
   - Replace `send_otp_sms()` function

5. **Real Payment Gateway**
   - Integrate Stripe, PayPal, or Razorpay
   - Use secure token-based authentication
   - Never store payment details

6. **Database Security**
   - Use PostgreSQL instead of SQLite
   - Implement proper user authentication
   - Add rate limiting

7. **Environment Variables**
   - Use `.env` file for sensitive data
   - Never commit secrets to version control

---

## 🚀 Deployment Options

### Option 1: Render (Free Tier)
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Deploy with automatic builds

### Option 2: Heroku
```bash
pip install gunicorn
echo "web: gunicorn app:app" > Procfile
git init && git add . && git commit -m "Initial commit"
heroku create && git push heroku main
```

### Option 3: AWS EC2
1. Launch Ubuntu instance
2. Install Python and dependencies
3. Use systemd to manage Flask service
4. Use Nginx as reverse proxy

### Option 4: Local Network
1. Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Update `app.py`: `app.run(host='0.0.0.0', port=5000)`
3. Access from other devices: `http://YOUR_IP:5000`

---

## 📱 API Endpoints Reference

### Authentication
- `POST /api/auth/admin-login` - Admin login
- `POST /api/auth/request-otp` - Request OTP
- `POST /api/auth/verify-otp` - Verify OTP
- `POST /api/auth/logout` - Logout
- `GET /api/auth/session` - Check session

### Products
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get product details

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/add` - Add product to cart
- `PUT /api/cart/update/<id>` - Update quantity
- `DELETE /api/cart/remove/<id>` - Remove item
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `POST /api/orders/create` - Create order
- `POST /api/orders/process-payment` - Process payment
- `GET /api/orders` - Get user's orders
- `GET /api/orders/<id>` - Get order details

---

## 📚 Learning Resources

### Frontend (HTML/CSS/JavaScript)
- MDN Web Docs: https://developer.mozilla.org/
- JavaScript Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

### Backend (Flask)
- Flask Documentation: https://flask.palletsprojects.com/
- SQLite: https://www.sqlite.org/docs.html

### Full Stack Development
- FreeCodeCamp: https://freecodecamp.org/
- Codecademy: https://codecademy.com/

---

## 📞 Support & Contribution

### Common Issues & Solutions

**Issue: Page is blank**
- Check browser console (F12 → Console tab)
- Verify Flask backend is running
- Clear browser cache (Ctrl+Shift+Delete)

**Issue: Styles not loading**
- Try opening in different browser
- Check if index.html is complete
- Verify no file corruption

**Issue: Products not showing**
- Delete `ecommerce.db` file
- Restart `python app.py`
- Refresh browser page

---

## 🎓 Next Steps for Learning

1. **Add More Features:**
   - Product search and filtering
   - User profile management
   - Order tracking with real-time updates
   - Product reviews and ratings

2. **Improve Security:**
   - Implement JWT authentication
   - Add password hashing improvements
   - CSRF protection

3. **Performance:**
   - Add caching with Redis
   - Optimize database queries
   - Implement pagination

4. **Real Integrations:**
   - Email notifications
   - SMS OTP with Twilio
   - Payment gateway (Stripe/PayPal)
   - Analytics tracking

---

## 📄 License

This project is provided as-is for educational purposes.

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] requirements.txt installed (`pip install -r requirements.txt`)
- [ ] `python app.py` running without errors
- [ ] Browser can access index.html
- [ ] Admin login works (admin/admin123)
- [ ] Customer login with OTP works
- [ ] Products display correctly
- [ ] Cart functionality works
- [ ] Checkout completes successfully
- [ ] Order confirmation appears

---

**Happy Coding! 🎉**
