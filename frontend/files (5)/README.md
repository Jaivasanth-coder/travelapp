# Sai Anjenya Yatra — Travel App 🌍✈️

> One stop solution for all your Domestic & International Tour needs.

## Project Structure
```
travelapp/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── env.properties      # Environment variables
│   └── requirements.txt    # Python dependencies
└── frontend/
    └── index.html          # Full frontend (single file)
```

## Setup Instructions

### 1. Create PostgreSQL Database
```powershell
psql -U postgres -h localhost
```
```sql
CREATE DATABASE travelapp;
\q
```

### 2. Install Python dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### 3. Configure environment
Edit `backend/env.properties`:
```
DATABASE_URL=postgresql://postgres:YourPassword@localhost:5432/travelapp?sslmode=disable
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

### 4. Run the backend
```powershell
cd backend
python app.py
```
Backend runs at: http://localhost:5000

### 5. Open the frontend
Open `frontend/index.html` in your browser.

## Default Admin Login
- Email: admin@saianjenya.com
- Password: Admin@123

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login |
| GET | /api/packages | List packages |
| GET | /api/packages/:id | Package detail |
| GET | /api/destinations | List destinations |
| POST | /api/bookings | Create booking |
| GET | /api/bookings/my | My bookings |
| POST | /api/enquiries | Send enquiry |
| GET | /api/admin/stats | Admin dashboard stats |
