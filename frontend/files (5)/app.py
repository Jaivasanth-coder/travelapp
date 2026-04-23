import os
import re
import jwt
import bcrypt
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps

load_dotenv("env.properties")

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "sai-anjenya-yatra-secret-key")

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

def get_db():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    clean_url = re.sub(r"sslmode=require", "sslmode=disable", url)
    if "sslmode" not in clean_url:
        clean_url += ("&" if "?" in clean_url else "?") + "sslmode=disable"
    return psycopg2.connect(clean_url, connect_timeout=10)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            country VARCHAR(255) NOT NULL,
            description TEXT,
            image_url VARCHAR(500),
            category VARCHAR(50) DEFAULT 'domestic',
            rating DECIMAL(2,1) DEFAULT 0,
            num_reviews INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            destination_id INT REFERENCES destinations(id) ON DELETE CASCADE,
            description TEXT,
            image_url VARCHAR(500),
            price DECIMAL(10,2) NOT NULL,
            duration_days INT NOT NULL,
            max_persons INT DEFAULT 10,
            includes TEXT,
            excludes TEXT,
            itinerary TEXT,
            category VARCHAR(50) DEFAULT 'domestic',
            is_featured BOOLEAN DEFAULT FALSE,
            rating DECIMAL(2,1) DEFAULT 0,
            num_reviews INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            package_id INT REFERENCES packages(id) ON DELETE CASCADE,
            travel_date DATE NOT NULL,
            num_persons INT NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            payment_status VARCHAR(50) DEFAULT 'unpaid',
            special_requests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            package_id INT REFERENCES packages(id) ON DELETE CASCADE,
            rating INT CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            message TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    seed_data(cur, conn)
    cur.close()
    conn.close()
    print("Database initialized successfully.")


def seed_data(cur, conn):
    cur.execute("SELECT id FROM users WHERE email = 'admin@saianjenya.com'")
    if not cur.fetchone():
        hashed = bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt()).decode()
        cur.execute("INSERT INTO users (name, email, password, is_admin) VALUES (%s,%s,%s,%s)",
                    ("Admin", "admin@saianjenya.com", hashed, True))

    cur.execute("SELECT COUNT(*) FROM destinations")
    if cur.fetchone()[0] == 0:
        destinations = [
            ("Goa", "India", "Sun, sand and sea - India's favourite beach destination.", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800", "domestic"),
            ("Kerala", "India", "God's Own Country - backwaters, hills and Ayurveda.", "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=800", "domestic"),
            ("Rajasthan", "India", "Land of kings - forts, palaces and desert safaris.", "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800", "domestic"),
            ("Himachal Pradesh", "India", "Snow-capped peaks and serene valleys.", "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800", "domestic"),
            ("Andaman Islands", "India", "Crystal clear waters and pristine coral reefs.", "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800", "domestic"),
            ("Bali", "Indonesia", "Island of Gods - temples, terraces and tropical bliss.", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800", "international"),
            ("Thailand", "Thailand", "Exotic temples, street food and tropical beaches.", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800", "international"),
            ("Dubai", "UAE", "Ultra-modern skyline meets ancient Arabian culture.", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800", "international"),
            ("Singapore", "Singapore", "The Lion City - futuristic gardens and world-class food.", "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800", "international"),
            ("Switzerland", "Switzerland", "Alpine majesty, chocolate and picture-perfect lakes.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", "international"),
        ]
        cur.executemany("INSERT INTO destinations (name, country, description, image_url, category) VALUES (%s,%s,%s,%s,%s)", destinations)

    cur.execute("SELECT COUNT(*) FROM packages")
    if cur.fetchone()[0] == 0:
        packages = [
            ("Goa Beach Bliss", 1, "5 nights of sun, sand and sea in beautiful Goa.", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800", 15999, 6, 20, "Flights, Hotel, Breakfast, Sightseeing", "Lunch, Dinner, Personal Expenses", "Day 1: Arrival & North Goa beaches\nDay 2: South Goa exploration\nDay 3: Water sports\nDay 4: Old Goa heritage\nDay 5: Leisure\nDay 6: Departure", "domestic", True, 4.5),
            ("Kerala Backwaters", 2, "Houseboat cruise through tranquil Kerala backwaters.", "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=800", 22999, 7, 15, "Flights, Houseboat, All Meals, Ayurveda Session", "Personal Expenses, Tips", "Day 1: Arrival Kochi\nDay 2: Munnar hills\nDay 3: Thekkady\nDay 4-5: Alleppey houseboat\nDay 6: Kovalam beach\nDay 7: Departure", "domestic", True, 4.8),
            ("Royal Rajasthan", 3, "Explore majestic forts and royal palaces of Rajasthan.", "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800", 28999, 8, 20, "Flights, Heritage Hotel, Breakfast, AC Coach", "Meals, Entry Fees", "Day 1: Jaipur\nDay 2: Amber Fort, City Palace\nDay 3: Pushkar\nDay 4: Jodhpur\nDay 5: Jaisalmer\nDay 6: Desert Safari\nDay 7: Udaipur\nDay 8: Departure", "domestic", True, 4.7),
            ("Himachal Snow Trek", 4, "Trek through the stunning snow-capped Himalayas.", "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800", 18999, 6, 12, "Transport, Camps, All Meals, Guide", "Personal Gear, Insurance", "Day 1: Manali arrival\nDay 2: Solang Valley\nDay 3: Rohtang Pass\nDay 4-5: Trek\nDay 6: Return", "domestic", False, 4.6),
            ("Andaman Paradise", 5, "Explore the pristine islands and coral reefs of Andaman.", "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800", 32999, 6, 15, "Flights, Resort, Breakfast, Ferry Tickets", "Scuba, Personal Expenses", "Day 1: Port Blair\nDay 2: Cellular Jail\nDay 3: Havelock Island\nDay 4: Radhanagar Beach\nDay 5: Neil Island\nDay 6: Departure", "domestic", True, 4.9),
            ("Bali Honeymoon", 6, "Romantic getaway to the magical island of Bali.", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800", 55999, 7, 10, "Flights, Villa, Breakfast, Transfers", "Meals, Entry Fees", "Day 1: Arrival Seminyak\nDay 2: Ubud temples\nDay 3: Rice terraces\nDay 4: Nusa Penida\nDay 5: Uluwatu sunset\nDay 6: Leisure\nDay 7: Departure", "international", True, 4.9),
            ("Thailand Explorer", 7, "Bangkok, Pattaya and Phuket in one grand tour.", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800", 49999, 8, 20, "Flights, Hotel, Daily Breakfast, Transfers", "Meals, Personal Expenses", "Day 1-2: Bangkok\nDay 3-4: Pattaya\nDay 5-6: Phuket\nDay 7: Phi Phi Island\nDay 8: Departure", "international", True, 4.7),
            ("Dubai Glamour", 8, "Experience the luxury and grandeur of Dubai.", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800", 62999, 6, 15, "Flights, 5-Star Hotel, Breakfast, City Tour, Desert Safari", "Meals, Personal Expenses", "Day 1: Arrival & Downtown\nDay 2: Burj Khalifa\nDay 3: Desert Safari\nDay 4: Palm Jumeirah\nDay 5: Old Dubai\nDay 6: Departure", "international", True, 4.8),
            ("Singapore Delight", 9, "Discover the ultra-modern Lion City.", "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800", 58999, 5, 15, "Flights, Hotel, Breakfast, City Tour, Universal Studios", "Meals, Personal Expenses", "Day 1: Arrival, Gardens by the Bay\nDay 2: Sentosa, Universal Studios\nDay 3: Chinatown, Marina Bay\nDay 4: Shopping\nDay 5: Departure", "international", False, 4.6),
            ("Switzerland Alps", 10, "Snow-capped peaks, pristine lakes and Swiss charm.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", 145999, 9, 12, "Flights, Hotel, Breakfast, Rail Pass, Guided Tours", "Meals, Personal Expenses", "Day 1: Zurich\nDay 2: Lucerne\nDay 3: Interlaken\nDay 4: Jungfraujoch\nDay 5: Grindelwald\nDay 6: Geneva\nDay 7: Zermatt\nDay 8: Bern\nDay 9: Departure", "international", True, 5.0),
        ]
        cur.executemany("INSERT INTO packages (title,destination_id,description,image_url,price,duration_days,max_persons,includes,excludes,itinerary,category,is_featured,rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", packages)

    conn.commit()


# ─────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────

def generate_token(user_id, is_admin):
    payload = {"user_id": user_id, "is_admin": is_admin, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user_id = data["user_id"]
            request.is_admin = data["is_admin"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            if not data.get("is_admin"):
                return jsonify({"error": "Admin access required"}), 403
            request.user_id = data["user_id"]
            request.is_admin = data["is_admin"]
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({"error": "Email already registered"}), 400
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s) RETURNING id, name, email, is_admin", (name, email, hashed))
    user = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    token = generate_token(user["id"], user["is_admin"])
    return jsonify({"token": token, "user": dict(user)}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close(); conn.close()
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid email or password"}), 401
    token = generate_token(user["id"], user["is_admin"])
    return jsonify({"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"], "is_admin": user["is_admin"]}})


@app.route("/api/auth/profile", methods=["GET"])
@token_required
def get_profile():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, email, is_admin, created_at FROM users WHERE id = %s", (request.user_id,))
    user = cur.fetchone()
    cur.close(); conn.close()
    return jsonify(dict(user))


# ─────────────────────────────────────────
# DESTINATIONS
# ─────────────────────────────────────────

@app.route("/api/destinations", methods=["GET"])
def get_destinations():
    category = request.args.get("category", "")
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if category:
        cur.execute("SELECT * FROM destinations WHERE category = %s ORDER BY name", (category,))
    else:
        cur.execute("SELECT * FROM destinations ORDER BY name")
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(d) for d in result])


@app.route("/api/destinations/<int:dest_id>", methods=["GET"])
def get_destination(dest_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM destinations WHERE id = %s", (dest_id,))
    dest = cur.fetchone()
    cur.close(); conn.close()
    if not dest:
        return jsonify({"error": "Destination not found"}), 404
    return jsonify(dict(dest))


# ─────────────────────────────────────────
# PACKAGES
# ─────────────────────────────────────────

@app.route("/api/packages", methods=["GET"])
def get_packages():
    category = request.args.get("category", "")
    featured = request.args.get("featured", "")
    search = request.args.get("search", "")
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = "SELECT p.*, d.name as destination_name, d.country FROM packages p JOIN destinations d ON p.destination_id = d.id WHERE 1=1"
    params = []
    if category:
        query += " AND p.category = %s"; params.append(category)
    if featured == "true":
        query += " AND p.is_featured = TRUE"
    if search:
        query += " AND (p.title ILIKE %s OR d.name ILIKE %s)"; params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY p.is_featured DESC, p.rating DESC"
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(p) for p in result])


@app.route("/api/packages/<int:pkg_id>", methods=["GET"])
def get_package(pkg_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT p.*, d.name as destination_name, d.country FROM packages p JOIN destinations d ON p.destination_id = d.id WHERE p.id = %s", (pkg_id,))
    pkg = cur.fetchone()
    if not pkg:
        cur.close(); conn.close()
        return jsonify({"error": "Package not found"}), 404
    cur.execute("SELECT r.*, u.name as user_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.package_id = %s ORDER BY r.created_at DESC", (pkg_id,))
    reviews = cur.fetchall()
    cur.close(); conn.close()
    result = dict(pkg)
    result["reviews"] = [dict(r) for r in reviews]
    return jsonify(result)


@app.route("/api/packages", methods=["POST"])
@admin_required
def create_package():
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO packages (title,destination_id,description,image_url,price,duration_days,max_persons,includes,excludes,itinerary,category,is_featured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (data["title"],data["destination_id"],data.get("description"),data.get("image_url"),data["price"],data["duration_days"],data.get("max_persons",10),data.get("includes"),data.get("excludes"),data.get("itinerary"),data.get("category","domestic"),data.get("is_featured",False)))
    pkg = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(pkg)), 201


@app.route("/api/packages/<int:pkg_id>", methods=["PUT"])
@admin_required
def update_package(pkg_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE packages SET title=%s,description=%s,image_url=%s,price=%s,duration_days=%s,max_persons=%s,includes=%s,excludes=%s,itinerary=%s,category=%s,is_featured=%s WHERE id=%s RETURNING *",
                (data["title"],data.get("description"),data.get("image_url"),data["price"],data["duration_days"],data.get("max_persons",10),data.get("includes"),data.get("excludes"),data.get("itinerary"),data.get("category","domestic"),data.get("is_featured",False),pkg_id))
    pkg = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(pkg))


@app.route("/api/packages/<int:pkg_id>", methods=["DELETE"])
@admin_required
def delete_package(pkg_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM packages WHERE id = %s", (pkg_id,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Package deleted"})


# ─────────────────────────────────────────
# BOOKINGS
# ─────────────────────────────────────────

@app.route("/api/bookings", methods=["POST"])
@token_required
def create_booking():
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT price FROM packages WHERE id = %s", (data["package_id"],))
    pkg = cur.fetchone()
    if not pkg:
        return jsonify({"error": "Package not found"}), 404
    total = float(pkg["price"]) * int(data["num_persons"])
    cur.execute("INSERT INTO bookings (user_id,package_id,travel_date,num_persons,total_price,special_requests) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
                (request.user_id,data["package_id"],data["travel_date"],data["num_persons"],total,data.get("special_requests")))
    booking = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(booking)), 201


@app.route("/api/bookings/my", methods=["GET"])
@token_required
def get_my_bookings():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT b.*, p.title as package_title, p.image_url, p.duration_days FROM bookings b JOIN packages p ON b.package_id = p.id WHERE b.user_id = %s ORDER BY b.created_at DESC", (request.user_id,))
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(b) for b in result])


@app.route("/api/bookings", methods=["GET"])
@admin_required
def get_all_bookings():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT b.*, p.title as package_title, u.name as user_name, u.email as user_email FROM bookings b JOIN packages p ON b.package_id = p.id JOIN users u ON b.user_id = u.id ORDER BY b.created_at DESC")
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(b) for b in result])


@app.route("/api/bookings/<int:booking_id>/status", methods=["PUT"])
@admin_required
def update_booking_status(booking_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE bookings SET status=%s, payment_status=%s WHERE id=%s RETURNING *", (data.get("status"),data.get("payment_status"),booking_id))
    booking = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(booking))


# ─────────────────────────────────────────
# REVIEWS
# ─────────────────────────────────────────

@app.route("/api/packages/<int:pkg_id>/reviews", methods=["POST"])
@token_required
def add_review(pkg_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id FROM reviews WHERE user_id=%s AND package_id=%s", (request.user_id, pkg_id))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({"error": "You have already reviewed this package"}), 400
    cur.execute("INSERT INTO reviews (user_id,package_id,rating,comment) VALUES (%s,%s,%s,%s)", (request.user_id,pkg_id,data["rating"],data.get("comment")))
    cur.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE package_id=%s", (pkg_id,))
    avg, count = cur.fetchone()
    cur.execute("UPDATE packages SET rating=%s, num_reviews=%s WHERE id=%s", (round(float(avg),1),count,pkg_id))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Review added successfully"}), 201


# ─────────────────────────────────────────
# ENQUIRIES
# ─────────────────────────────────────────

@app.route("/api/enquiries", methods=["POST"])
def create_enquiry():
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO enquiries (name,email,phone,message) VALUES (%s,%s,%s,%s) RETURNING *", (data["name"],data["email"],data.get("phone"),data["message"]))
    enquiry = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(enquiry)), 201


@app.route("/api/enquiries", methods=["GET"])
@admin_required
def get_enquiries():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(e) for e in result])


# ─────────────────────────────────────────
# ADMIN STATS
# ─────────────────────────────────────────

@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def get_stats():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as total FROM users WHERE is_admin=FALSE")
    users = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM bookings")
    bookings = cur.fetchone()["total"]
    cur.execute("SELECT COALESCE(SUM(total_price),0) as total FROM bookings WHERE payment_status='paid'")
    revenue = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM packages")
    packages = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM enquiries WHERE status='new'")
    new_enquiries = cur.fetchone()["total"]
    cur.close(); conn.close()
    return jsonify({"total_users": users, "total_bookings": bookings, "total_revenue": float(revenue), "total_packages": packages, "new_enquiries": new_enquiries})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "Sai Anjenya Yatra Travel App"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
