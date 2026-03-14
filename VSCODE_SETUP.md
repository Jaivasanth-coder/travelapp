# 🚀 ProShop - VS Code Setup Guide (Windows)

## 5-Minute Setup

### Step 1: Open Project in VS Code

1. **Download & Extract Files**
   - Extract the ProShop folder to your desired location
   - Example: `C:\Users\YourName\Desktop\ProShop`

2. **Open in VS Code**
   - Open VS Code
   - File → Open Folder
   - Select the `ProShop` folder
   - Click "Select Folder"

### Step 2: Install Recommended Extensions

When VS Code opens, you'll see a popup asking about recommended extensions.

**Click "Install All"** or manually install:
1. Click Extensions icon (left sidebar) or `Ctrl+Shift+X`
2. Search for: **Python** (by Microsoft)
3. Click Install
4. Search for: **Live Server** (by Ritwick Dey)
5. Click Install

### Step 3: Open Terminal in VS Code

1. Press `Ctrl + ~` (backtick)
   - OR: View → Terminal
   - A terminal opens at the bottom

2. You should see a terminal showing:
   ```
   PS C:\path\to\ProShop>
   ```

### Step 4: Install Python Dependencies

In the terminal, run:

```bash
cd backend
pip install -r requirements.txt
```

**Wait for it to finish.** You'll see:
```
Successfully installed Flask-2.3.3 flask-cors-4.0.0 Werkzeug-2.3.7
```

### Step 5: Start Backend Server

In the same terminal, run:

```bash
python app.py
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

✅ **Backend is running!** Leave this terminal open.

### Step 6: Open Frontend

1. Click on `Explorer` icon (top left)
2. Navigate: `frontend` folder
3. Right-click on `index.html`
4. Click **"Open with Live Server"**
   - Browser opens automatically at `http://localhost:5500`
   - Website loads

✅ **Frontend is running!**

### Step 7: Test the Application

1. **Admin Login:**
   - Username: `admin`
   - Password: `admin123`
   - Click Login

2. **View Products:**
   - See 6 products on the page
   - Click "Add to Cart" on any product

3. **Shopping Cart:**
   - Click 🛒 icon (top right)
   - See cart sidebar with item
   - Click "Proceed to Checkout"

4. **Checkout:**
   - Fill in the form
   - Select payment method
   - Click "Place Order"
   - See order confirmation

✅ **Everything works!**

---

## 📁 Project Structure in VS Code

```
ProShop/
├── backend/
│   ├── app.py ..................... Flask server
│   └── requirements.txt ........... Dependencies
├── frontend/
│   └── index.html ................ Website
├── docs/ ......................... Documentation
│   ├── QUICK_START.md ........... Quick guide
│   ├── EXECUTION_GUIDE.md ....... Detailed walkthrough
│   └── ... more guides
├── .vscode/ ...................... VS Code config
│   ├── settings.json ............ Editor settings
│   └── launch.json .............. Debug config
└── START.bat .................... Quick start script
```

---

## 💻 Useful VS Code Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + ~` | Toggle terminal |
| `Ctrl + P` | Quick file open |
| `Ctrl + Shift + F` | Search all files |
| `Ctrl + F` | Find in current file |
| `Ctrl + H` | Find & replace |
| `F5` | Start debugging |
| `Ctrl + Shift + D` | Debug panel |
| `Ctrl + Shift + X` | Extensions |

---

## 🐛 Troubleshooting

### "Python not found"
```bash
# Check Python is installed and in PATH
python --version

# If not found:
# Download from https://python.org/downloads/
# During installation, CHECK "Add Python to PATH"
# Restart VS Code
```

### "pip install fails"
```bash
# Try using pip3
pip3 install -r requirements.txt

# Or upgrade pip first
python -m pip install --upgrade pip
```

### "Port 5000 already in use"
```bash
# Edit backend/app.py, last line:
# Change: app.run(debug=True, port=5000)
# To:     app.run(debug=True, port=8000)
```

### "Live Server not working"
1. Make sure extension is installed
2. Right-click index.html
3. Select "Open with Live Server"
4. If still not working, manually open:
   - `file:///C:/path/to/ProShop/frontend/index.html`

### "Products not loading"
1. Close Flask server (Ctrl+C)
2. Delete `ecommerce.db` file (if it exists in backend folder)
3. Start Flask again (`python app.py`)
4. Refresh browser (Ctrl+F5)

### "CORS Error"
1. Make sure Flask is running
2. Check it says "Running on http://127.0.0.1:5000"
3. Hard refresh browser: Ctrl+Shift+Delete (clear cache)
4. Then Ctrl+F5 to refresh

---

## 🔍 Debugging

### Debug Backend (Python)

1. Click Debug icon (left sidebar) or `Ctrl+Shift+D`
2. Select "Flask - Development" from dropdown
3. Click green ▶ button to start
4. Flask runs in debug mode
5. Click line number to set breakpoints
6. Variables shown when breakpoint hits

### Debug Frontend (JavaScript)

1. Press F12 in browser
2. Go to "Console" tab
3. See JavaScript errors (red text)
4. Go to "Network" tab
5. See API calls to backend

### View Network Requests

1. Browser F12 → Network tab
2. Add product to cart
3. See API call: POST /api/cart/add
4. Click to see request/response

---

## 📝 Common Tasks

### Add a New Product

1. Open `backend/app.py`
2. Find function `seed_sample_data()` (around line 50)
3. Find the `products` list
4. Add new line:
   ```python
   ('Product Name', 'Description', 99.99, 'image_url', stock),
   ```
5. Delete `ecommerce.db` (if exists)
6. Restart Flask (`Ctrl+C`, then `python app.py`)
7. Refresh browser

### Change Colors

1. Open `frontend/index.html`
2. Find `:root {` (around line 25)
3. Change color values:
   ```css
   --primary: #2563eb;        /* Change this blue */
   --secondary: #f59e0b;      /* Change this orange */
   ```
4. Save (Ctrl+S)
5. Refresh browser (F5)

### Change Login Credentials

1. Open `backend/app.py`
2. Find `seed_sample_data()` function
3. Change admin password line
4. Delete `ecommerce.db`
5. Restart Flask

---

## 🚀 Full Workflow

### Day 1: Setup & Explore

```
1. Open ProShop folder in VS Code
2. Install extensions (Python, Live Server)
3. cd backend
4. pip install -r requirements.txt
5. python app.py
6. Open frontend/index.html with Live Server
7. Test login and features
```

### Day 2: Understand Code

```
1. Open backend/app.py
2. Read comments explaining each section
3. Open frontend/index.html
4. Look at HTML structure
5. Look at CSS (styling)
6. Look at JavaScript (functionality)
7. Compare with documentation
```

### Day 3: Customize

```
1. Change colors in index.html
2. Add more products in app.py
3. Change login credentials
4. Test changes
5. See ecommerce.db updated
```

---

## 📚 What Each File Does

### backend/app.py
- Flask web server
- All API endpoints
- Database management
- Authentication
- Order processing
- Start with: `python app.py`

### frontend/index.html
- Complete website
- User interface
- Product display
- Shopping cart
- Checkout form
- Open with: Browser or Live Server

### docs/
- QUICK_START.md - 5 minute start
- EXECUTION_GUIDE.md - Full walkthrough
- SETUP_GUIDE.md - Configuration
- README.md - Overview

---

## 🎯 Success Indicators

✅ VS Code opens ProShop folder  
✅ Terminal shows: `python app.py`  
✅ Terminal shows: `Running on http://127.0.0.1:5000`  
✅ Browser opens index.html  
✅ Can login with admin/admin123  
✅ Can see 6 products  
✅ Can add to cart  
✅ Can checkout  
✅ See order confirmation  

**If all green: You're ready to code! 🎉**

---

## 💡 Pro Tips

1. **Keep Terminal Visible**
   - See errors and logs in real-time
   - Split window: Drag terminal border up

2. **Use Split Windows**
   - Edit backend code on left
   - See backend.py on right
   - Or backend on left, frontend on right

3. **Auto-Format Code**
   - Select code
   - Shift+Alt+F to auto-format
   - Makes code look professional

4. **Save Before Testing**
   - Always Ctrl+S before testing changes
   - Makes it easy to spot changes

5. **Use Version Control**
   - `git init` to start Git
   - Commit changes regularly
   - Easy to undo mistakes

---

## 🆘 Still Stuck?

1. Check `docs/QUICK_START.md` (5 min read)
2. Read `docs/EXECUTION_GUIDE.md` (detailed guide)
3. Check code comments
4. Search VS Code for error message
5. Check browser console (F12)

---

## ⚡ Next Steps

1. ✅ Follow this guide (15 minutes)
2. ✅ Get app running
3. ✅ Read `docs/QUICK_START.md` (5 min)
4. ✅ Read `docs/EXECUTION_GUIDE.md` (15 min)
5. ✅ Read `docs/SETUP_GUIDE.md` (10 min)
6. ✅ Customize for your needs
7. ✅ Deploy to cloud

---

**You're all set! Follow Step 1 above to get started. Good luck! 🚀**
