# 🛍️ ProShop - Full-Stack E-Commerce Platform

A complete, production-ready e-commerce web application built with Python Flask and vanilla HTML/CSS/JavaScript. Perfect for learning full-stack development or as a starting point for your own e-commerce platform.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-black.svg)

---

## ✨ Features

### 🔐 Authentication System
- **Admin Panel Login**: Secure username/password authentication
- **Customer OTP Login**: Phone number verification with OTP
- **Session Management**: Secure session handling and logout
- **Role-based Access**: Different features for admins and customers

### 📦 Product Management
- Browse 6+ pre-loaded sample products
- Product images, descriptions, and pricing
- Real-time stock availability tracking
- Responsive product grid layout

### 🛒 Shopping Cart
- Add/remove products dynamically
- Adjust product quantities
- Real-time cart total calculation
- Persistent cart sidebar
- Quick cart access from header

### 💳 Checkout & Payment
- Complete order information collection
- Multiple payment methods (Card, Debit, UPI)
- Tax calculation (10%)
- Shipping cost included
- Order summary with itemized breakdown

### 📋 Order Management
- Order creation and confirmation
- Payment processing
- Order history tracking
- Order status updates
- Detailed order information

### 🎨 User Interface
- Modern, responsive design
- Mobile-friendly layout
- Smooth animations and transitions
- Intuitive navigation
- Professional color scheme

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Any modern web browser
- VS Code (optional but recommended)

### Installation (2 minutes)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Backend Server**
   ```bash
   python app.py
   ```

3. **Open Frontend**
   - Open `index.html` directly in your browser, OR
   - Use VS Code's Live Server extension

### Login Credentials

**Admin:**
```
Username: admin
Password: admin123
```

**Customer:**
```
Phone: Any 10+ digit number
OTP: Display in browser/terminal
```

---

## 📁 Project Structure

```
proshop/
├── app.py                  # Flask backend (routes, database, logic)
├── index.html              # Frontend (HTML/CSS/JavaScript)
├── requirements.txt        # Python dependencies
├── ecommerce.db           # SQLite database (auto-created)
├── start.bat              # Quick start for Windows
├── start.sh               # Quick start for Mac/Linux
├── SETUP_GUIDE.md         # Detailed setup instructions
└── README.md              # This file
```

---

## 🏗️ Architecture

### Backend (Flask)
```
app.py
├── Database Layer (SQLite)
│   ├── Users table
│   ├── Products table
│   ├── Cart table
│   ├── Orders table
│   └── Order Items table
├── API Routes
│   ├── Authentication endpoints
│   ├── Product endpoints
│   ├── Cart endpoints
│   └── Order endpoints
└── Business Logic
    ├── OTP management
    ├── Cart operations
    └── Order processing
```

### Frontend (HTML/CSS/JavaScript)
```
index.html
├── HTML Structure
│   ├── Login page
│   ├── Product catalog
│   ├── Cart sidebar
│   ├── Checkout form
│   └── Order confirmation
├── CSS Styling (3500+ lines)
│   ├── Responsive grid layout
│   ├── Component styles
│   └── Animations & transitions
└── JavaScript (800+ lines)
    ├── API communication
    ├── State management
    ├── DOM manipulation
    └── Event handlers
```

---

## 🔗 API Documentation

### Authentication Endpoints

#### Admin Login
```http
POST /api/auth/admin-login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

#### Request OTP
```http
POST /api/auth/request-otp
Content-Type: application/json

{
  "phone": "9876543210"
}
```

#### Verify OTP
```http
POST /api/auth/verify-otp
Content-Type: application/json

{
  "phone": "9876543210",
  "otp": "123456"
}
```

### Product Endpoints

#### Get All Products
```http
GET /api/products
```

#### Get Single Product
```http
GET /api/products/{id}
```

### Cart Endpoints

#### Get Cart
```http
GET /api/cart
```

#### Add to Cart
```http
POST /api/cart/add
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 1
}
```

#### Update Cart Item
```http
PUT /api/cart/update/{cart_id}
Content-Type: application/json

{
  "quantity": 2
}
```

#### Remove from Cart
```http
DELETE /api/cart/remove/{cart_id}
```

### Order Endpoints

#### Create Order
```http
POST /api/orders/create
Content-Type: application/json

{
  "payment_method": "credit_card"
}
```

#### Process Payment
```http
POST /api/orders/process-payment
Content-Type: application/json

{
  "order_id": 1,
  "payment_details": {
    "method": "credit_card"
  }
}
```

#### Get Orders
```http
GET /api/orders
```

---

## 🎓 Learning Concepts

This project teaches:

### Frontend
- **HTML5**: Semantic markup, forms, accessibility
- **CSS3**: Grid, Flexbox, animations, responsive design
- **JavaScript**: Fetch API, async/await, DOM manipulation, event handling
- **UI/UX**: User interaction, form validation, error handling

### Backend
- **Flask**: Web framework, routing, request handling
- **SQLite**: Database design, CRUD operations, queries
- **Authentication**: Session management, password hashing
- **REST API**: Endpoint design, request/response handling
- **CORS**: Cross-origin resource sharing

### Full Stack
- **Client-Server Architecture**: Frontend-backend communication
- **State Management**: User sessions, cart data, orders
- **Error Handling**: Try-catch, error messages, validation
- **Security**: Password hashing, session handling, input validation

---

## 🔧 Configuration

### Change Backend Port
In `app.py`:
```python
app.run(debug=True, port=8000)  # Change 5000 to 8000
```

### Change Frontend API URL
In `index.html`:
```javascript
const API_BASE = 'http://localhost:8000/api';  // Update port
```

### Add More Products
In `app.py`, `seed_sample_data()` function:
```python
products = [
    ('Product Name', 'Description', Price, 'image_url', stock),
]
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Ensure `python app.py` is running |
| CORS errors | Check Flask backend is running on correct port |
| Products not loading | Delete `ecommerce.db` and restart `app.py` |
| OTP not showing | Check browser console (F12) or terminal output |
| Cart not updating | Refresh page or check browser network tab |
| Database locked | Close other instances, delete `ecommerce.db` |

---

## 🚀 Deployment

### Heroku
```bash
pip install gunicorn
echo "web: gunicorn app:app" > Procfile
git init && git add . && git commit -m "Initial"
heroku create && git push heroku main
```

### Render
1. Push to GitHub
2. Connect GitHub to Render
3. Deploy automatically

### AWS EC2
1. Launch Ubuntu instance
2. Install Python and dependencies
3. Use Gunicorn + Nginx
4. Configure domain and SSL

---

## 🔒 Security

### Production Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `debug=False` in production
- [ ] Implement HTTPS/SSL
- [ ] Use PostgreSQL instead of SQLite
- [ ] Implement real payment gateway
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Implement real OTP service
- [ ] Add CSRF protection

---

## 📈 Future Enhancements

- [ ] User profiles and wishlist
- [ ] Product reviews and ratings
- [ ] Search and advanced filtering
- [ ] Email notifications
- [ ] Real SMS OTP (Twilio)
- [ ] Real payment gateway (Stripe)
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Inventory management
- [ ] Order tracking

---

## 📚 Resources

### Documentation
- [Flask Official Docs](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [MDN Web Docs](https://developer.mozilla.org/)
- [REST API Best Practices](https://restfulapi.net/)

### Learning Platforms
- [FreeCodeCamp](https://freecodecamp.org/)
- [Codecademy](https://codecademy.com/)
- [Real Python](https://realpython.com/)
- [Udemy](https://udemy.com/)

---

## 💡 Tips for Developers

### Debugging
- Use `print()` statements in Flask
- Check browser console: F12 → Console tab
- Network tab shows API calls
- Use debugger: `pdb` in Python

### Best Practices
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic
- Test frequently during development
- Use version control (Git)

### Performance
- Minimize database queries
- Cache frequently accessed data
- Optimize images
- Use CDN for static files
- Implement pagination

---

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and use in your projects.

---

## 🤝 Contributing

Improvements and suggestions welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## ❓ FAQ

**Q: Can I use this for production?**
A: Not as-is. Follow the Security checklist above before deploying.

**Q: How do I add real payment processing?**
A: Integrate with Stripe, PayPal, or Razorpay. Replace `process_payment()` function.

**Q: How do I send real SMS OTP?**
A: Use Twilio, AWS SNS, or similar. Replace `send_otp_sms()` function.

**Q: Can I use a different database?**
A: Yes! SQLite is easy to switch to PostgreSQL, MySQL, etc.

**Q: Is this mobile-responsive?**
A: Yes! Uses CSS media queries and flexbox for responsive design.

---

## 📞 Support

- 📧 Email: support@example.com
- 💬 Issues: Create GitHub issue
- 📖 Docs: Check SETUP_GUIDE.md

---

## ✅ Quick Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Backend running: `python app.py`
- [ ] Frontend accessible: `index.html`
- [ ] Admin login works
- [ ] Customer OTP login works
- [ ] Products display
- [ ] Cart functionality works
- [ ] Checkout completes
- [ ] Order confirmation shows

---

<div align="center">

**Happy Coding! 🎉**

Made with ❤️ for learning and development

</div>
