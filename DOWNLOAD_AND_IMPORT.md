# 📥 ProShop - Download & Import to VS Code (Windows)

## Complete Step-by-Step Guide

---

## 📦 What You're Downloading

A complete e-commerce application with:
- ✅ Python Flask backend (API)
- ✅ HTML/CSS/JavaScript frontend (Website)
- ✅ SQLite database (auto-created)
- ✅ Complete documentation (6 guides)
- ✅ VS Code configuration (ready to use)
- ✅ All you need to start developing

**Total Size:** ~150 KB (very small!)

---

## ⬇️ Step 1: Download Files

### Option A: Download as Folder (Easiest)

1. Look for a "Download" button or link
2. You'll get a `ProShop` folder
3. It contains everything you need

### Option B: Manual Download

If downloading individual files:

1. Create a folder: `ProShop`
   - Location: `C:\Users\YourName\Desktop\ProShop`
   
2. Download these files into `ProShop\backend\`:
   - `app.py`
   - `requirements.txt`

3. Download these files into `ProShop\frontend\`:
   - `index.html`

4. Download these files into `ProShop\docs\`:
   - `QUICK_START.md`
   - `EXECUTION_GUIDE.md`
   - `SETUP_GUIDE.md`
   - `README.md`
   - `PROJECT_SUMMARY.md`
   - `FILE_INDEX.md`

5. Download into `ProShop\`:
   - `START.bat`
   - `VSCODE_SETUP.md`
   - `README.md`
   - `.gitignore`

---

## 📂 Verify Your Folder Structure

Your `ProShop` folder should look like this:

```
ProShop/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── docs/
│   ├── QUICK_START.md
│   ├── EXECUTION_GUIDE.md
│   ├── SETUP_GUIDE.md
│   ├── README.md
│   ├── PROJECT_SUMMARY.md
│   └── FILE_INDEX.md
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── extensions.json
├── START.bat
├── VSCODE_SETUP.md
├── README.md
└── .gitignore
```

**If structure doesn't match:** Create folders and move files accordingly.

---

## 🔧 Step 2: Install VS Code (If Not Already Installed)

### Check if VS Code is Installed

1. Press Windows key
2. Type: `Visual Studio Code`
3. If it appears, click it to open
4. If not, continue below

### Download & Install VS Code

1. Visit: https://code.visualstudio.com/
2. Click "Download for Windows"
3. Run the installer
4. Follow installation wizard
5. Launch VS Code

---

## 📂 Step 3: Open ProShop Folder in VS Code

### Method 1: Using File Menu (Recommended)

1. **Open VS Code**
   - Click the VS Code icon on desktop or taskbar

2. **Open Folder**
   - Click: File → Open Folder
   - Navigate to your `ProShop` folder
   - Example: `C:\Users\YourName\Desktop\ProShop`
   - Click: "Select Folder"

3. **Trust the Folder** (if asked)
   - Click: "Yes, I trust the authors"
   - This allows VS Code to work properly

### Method 2: Using File Explorer

1. **Open File Explorer**
   - Press: Windows + E
   - Navigate to your `ProShop` folder

2. **Right-Click in Folder**
   - Right-click empty space
   - Select: "Open with Code"
   - VS Code opens

### Method 3: Command Line

1. **Open Command Prompt**
   - Press: Windows + R
   - Type: `cmd`
   - Press: Enter

2. **Navigate to Folder**
   ```bash
   cd C:\path\to\ProShop
   code .
   ```

---

## ✅ Step 4: Install Recommended Extensions

When you open the project, VS Code should suggest extensions.

### Automatic Installation

1. Look for notification: "This workspace has extension recommendations"
2. Click: "Install All"
3. Wait for installation to complete

### Manual Installation

If no notification appears:

1. **Open Extensions Panel**
   - Click Extensions icon (left sidebar)
   - OR: Press `Ctrl + Shift + X`

2. **Install Python Extension**
   - Search: `python`
   - First result: "Python" by Microsoft
   - Click: "Install"
   - Wait for completion

3. **Install Live Server**
   - Search: `live server`
   - Result: "Live Server" by Ritwick Dey
   - Click: "Install"
   - Wait for completion

4. **Optional: REST Client**
   - Search: `rest client`
   - Click: "Install"
   - Helpful for testing APIs

---

## 🖥️ Step 5: Open Terminal in VS Code

### Open Terminal

- Press: `Ctrl + ~` (backtick, below Esc key)
- OR: View → Terminal
- A terminal opens at bottom of VS Code

### Check Terminal Location

The terminal should show something like:
```
PS C:\Users\YourName\Desktop\ProShop>
```

If not in the right folder:
```bash
cd backend
```

---

## 📥 Step 6: Install Python Dependencies

In the VS Code terminal, copy and paste:

```bash
pip install -r requirements.txt
```

**What this does:**
- Installs Flask (web framework)
- Installs Flask-CORS (cross-origin support)
- Installs Werkzeug (security tools)

**Wait for completion.** You'll see:
```
Successfully installed Flask-2.3.3 flask-cors-4.0.0 Werkzeug-2.3.7
```

---

## 🚀 Step 7: Start the Backend Server

In the same terminal, type:

```bash
python app.py
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

✅ **Backend is running!**

⚠️ **Keep this terminal open!** The backend must stay running.

---

## 🌐 Step 8: Open Frontend in Browser

### Using Live Server (Recommended)

1. In VS Code left panel, click "Explorer"
2. Navigate to: `frontend` → `index.html`
3. Right-click on `index.html`
4. Click: "Open with Live Server"
5. Browser opens automatically at `http://localhost:5500`

### Using File Explorer

1. Open File Explorer
2. Navigate to `ProShop/frontend/`
3. Double-click `index.html`
4. Browser opens with the website

---

## 🎮 Step 9: Test the Application

### Test Admin Login

1. Click "Admin Login" tab (if not selected)
2. Username: `admin`
3. Password: `admin123`
4. Click: "Login"
5. ✅ You should see products page

### Test Features

1. **View Products**
   - See 6 products on the page

2. **Add to Cart**
   - Click "Add to Cart" on any product
   - See green notification

3. **View Cart**
   - Click 🛒 icon (top right)
   - See cart sidebar

4. **Checkout**
   - Click "Proceed to Checkout"
   - Fill in form
   - Select payment method
   - Click "Place Order"

5. **Order Confirmation**
   - See confirmation page
   - Shows Order ID and total

✅ **Everything works!**

---

## 📝 Understanding Your Folder Structure

### backend/ Folder
```
Contains Python Flask server
- app.py ................. Main server code
- requirements.txt ....... Package list
- ecommerce.db .......... Database (created when app runs)
```

**What to do:**
- Edit `app.py` to change backend logic
- Run `python app.py` to start server

### frontend/ Folder
```
Contains Website Code
- index.html ............ Complete website (HTML/CSS/JS)
```

**What to do:**
- Edit `index.html` to change design/functionality
- Open in browser to see changes (auto-refresh with Live Server)

### docs/ Folder
```
Contains Documentation
- QUICK_START.md ......... Get running in 5 min
- EXECUTION_GUIDE.md .... Detailed walkthrough
- SETUP_GUIDE.md ........ Configuration & customization
- README.md ............. Project overview
- PROJECT_SUMMARY.md ... Complete summary
- FILE_INDEX.md ......... File guide
```

**What to do:**
- Read these to understand how to use the project

### .vscode/ Folder
```
VS Code Configuration
- settings.json ......... Editor settings
- launch.json ........... Debug configuration
- extensions.json ....... Recommended extensions
```

**What to do:**
- Don't edit these (already configured)
- Helps VS Code understand your project

---

## 💡 Tips & Tricks

### Keep Both Visible

1. **Split VS Code in Half**
   - Open `backend/app.py` (left side)
   - Open terminal (right side)
   - Watch for errors in real time

2. **Keep Browser & Editor Visible**
   - Drag VS Code window to left half of screen
   - Drag browser window to right half
   - See changes instantly

### Quick Terminal Access

- Press `Ctrl + ~` to toggle terminal
- Press `Ctrl + J` to show/hide terminal

### Quick File Navigation

- Press `Ctrl + P` to open any file quickly
- Type filename, press Enter

### Find & Replace

- Press `Ctrl + H` to find & replace in all files
- Useful for changing variable names

---

## 🆘 Troubleshooting

### Python Not Found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Close VS Code
2. Install Python from https://python.org/downloads/
3. **IMPORTANT:** During installation, check "Add Python to PATH"
4. Restart your computer
5. Reopen VS Code
6. Try again

### pip Command Not Found

**Error:**
```
'pip' is not recognized
```

**Solution:**
```bash
# Use this instead:
python -m pip install -r requirements.txt
```

### Port 5000 Already in Use

**Error:**
```
Address already in use
```

**Solution 1 - Change Port:**
1. Open `backend/app.py`
2. Find the last line: `app.run(debug=True, port=5000)`
3. Change to: `app.run(debug=True, port=8000)`
4. Stop Flask (Ctrl+C)
5. Start again: `python app.py`

**Solution 2 - Kill Process:**
```bash
# Windows - Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Live Server Not Working

**Solution:**
1. Make sure "Live Server" extension is installed
2. Right-click `index.html` → "Open with Live Server"
3. If still doesn't work:
   - Double-click `index.html` (opens in default browser)
   - OR manually navigate to: `file:///C:/path/to/ProShop/frontend/index.html`

### Products Not Loading

**Solution:**
1. Close Flask server (Ctrl+C in terminal)
2. Delete `ecommerce.db` file (if exists in backend folder)
3. Start Flask again: `python app.py`
4. Hard refresh browser: `Ctrl + Shift + Delete` (clear cache)
5. Then refresh: `Ctrl + F5`

### CORS Error

**Error:**
```
No 'Access-Control-Allow-Origin' header
```

**Solution:**
1. Make sure Flask is running: `python app.py`
2. Check terminal shows: `Running on http://127.0.0.1:5000`
3. Hard refresh browser: `Ctrl + Shift + Delete`
4. Then `Ctrl + F5`

### Can't Connect to Backend

**Error:**
```
Connection refused or Cannot reach server
```

**Solution:**
1. Check Flask terminal
2. Should show: `Running on http://127.0.0.1:5000`
3. If not, start it: `python app.py`
4. If it crashes, look for red error messages
5. Check `docs/EXECUTION_GUIDE.md` for help

---

## 🔄 Typical Workflow

### First Time (15 minutes)

```
1. Open ProShop folder in VS Code
2. Install extensions
3. Open terminal (Ctrl + ~)
4. cd backend
5. pip install -r requirements.txt
6. python app.py
7. Right-click frontend/index.html → Open with Live Server
8. Test features
9. Read docs/VSCODE_SETUP.md
```

### Daily Development (5 minutes to start)

```
1. Open ProShop folder in VS Code
2. Open terminal (Ctrl + ~)
3. cd backend
4. python app.py
5. Right-click frontend/index.html → Open with Live Server
6. Browser opens, website loads
7. Start coding!
```

### Making Changes

```
1. Edit backend/app.py or frontend/index.html
2. Save (Ctrl + S)
3. For backend: Restart Flask (Ctrl+C, python app.py)
4. For frontend: Live Server auto-refreshes
5. Test in browser
```

---

## ✅ Success Checklist

After following all steps above, verify:

- [ ] ProShop folder opened in VS Code
- [ ] Python extension installed
- [ ] Live Server extension installed
- [ ] Terminal open in backend folder
- [ ] `pip install -r requirements.txt` completed
- [ ] `python app.py` running (no errors)
- [ ] Backend shows: `Running on http://127.0.0.1:5000`
- [ ] Browser opened with Live Server
- [ ] Website loads (sees login page)
- [ ] Can login with admin/admin123
- [ ] Can view products
- [ ] Can add to cart
- [ ] Can checkout
- [ ] Can see order confirmation

**If all checked:** ✅ You're ready to develop!

---

## 🎓 Next Steps

### Day 1: Understand
1. Read `docs/QUICK_START.md` (5 min)
2. Read `docs/VSCODE_SETUP.md` (10 min)
3. Test all features
4. Explore folder structure

### Day 2: Code Review
1. Open `backend/app.py`
2. Read comments explaining each section
3. Open `frontend/index.html`
4. Look at HTML, CSS, JavaScript
5. Understand how they work together

### Day 3: Customize
1. Read `docs/SETUP_GUIDE.md`
2. Change colors in `frontend/index.html`
3. Add products in `backend/app.py`
4. Test changes
5. See database update

### Week 2: Enhance
1. Read `docs/README.md` (full overview)
2. Add new features
3. Optimize code
4. Test thoroughly

### Week 3: Deploy
1. Follow `docs/SETUP_GUIDE.md` → Deployment
2. Deploy to cloud (Heroku, Render, AWS)
3. Share with others
4. Celebrate! 🎉

---

## 📞 Quick Help

### For Setup Issues
→ Check "Troubleshooting" section above

### For Code Questions
→ Look at comments in `backend/app.py`
→ Look at comments in `frontend/index.html`

### For Project Questions
→ Read `docs/README.md`

### For Detailed Walkthrough
→ Read `docs/EXECUTION_GUIDE.md`

### For Configuration Help
→ Read `docs/SETUP_GUIDE.md`

---

## 🎉 You're All Set!

You now have:
✅ Professional VS Code setup
✅ All application files organized
✅ Python backend ready
✅ HTML/CSS/JavaScript frontend ready
✅ Complete documentation
✅ Debug configuration
✅ Everything to succeed

**Next:** Follow the "Typical Workflow" above to get started!

---

**Happy coding! 🚀**

Questions? Check the docs in `ProShop/docs/` folder!
