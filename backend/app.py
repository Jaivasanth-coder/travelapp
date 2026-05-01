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

from pathlib import Path
if Path(".env").exists():
    load_dotenv(".env")
else:
    load_dotenv("env.properties")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET","POST","PUT","DELETE","OPTIONS"], "allow_headers": ["Content-Type","Authorization"]}})

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "sai-anjenya-yatra-secret-key")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.route("/api/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    return "", 204

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

def get_db():
    host     = os.environ.get("DB_HOST", "localhost")
    port     = os.environ.get("DB_PORT", "5432")
    dbname   = os.environ.get("DB_NAME", "traveldb")
    user     = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")

    url = os.environ.get("DATABASE_URL", "")
    if url:
        try:
            url_clean = url.replace("postgresql://", "").replace("postgres://", "")
            userinfo, hostinfo = url_clean.rsplit("@", 1)
            user, password = userinfo.split(":", 1)
            password = password.split("?")[0]
            host_port, dbname = hostinfo.split("/", 1)
            dbname = dbname.split("?")[0]
            if ":" in host_port:
                host, port = host_port.split(":", 1)
            else:
                host = host_port
            from urllib.parse import unquote
            password = unquote(password)
        except Exception as e:
            print(f"Warning: Could not parse DATABASE_URL, using defaults. Error: {e}")

    return psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password,
        connect_timeout=10
    )


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
            sub_category VARCHAR(50) DEFAULT 'vacation',
            is_featured BOOLEAN DEFAULT FALSE,
            rating DECIMAL(2,1) DEFAULT 0,
            num_reviews INT DEFAULT 0,
            likes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS package_likes (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            package_id INT REFERENCES packages(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, package_id)
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
            ("Varanasi", "India", "The spiritual capital of India on the banks of Ganga.", "https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=800", "domestic"),
            ("Tirupati", "India", "Most visited pilgrimage centre - Venkateswara Temple.", "https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=800", "domestic"),
            ("Bali", "Indonesia", "Island of Gods - temples, terraces and tropical bliss.", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800", "international"),
            ("Thailand", "Thailand", "Exotic temples, street food and tropical beaches.", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800", "international"),
            ("Dubai", "UAE", "Ultra-modern skyline meets ancient Arabian culture.", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800", "international"),
            ("Singapore", "Singapore", "The Lion City - futuristic gardens and world-class food.", "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800", "international"),
            ("Switzerland", "Switzerland", "Alpine majesty, chocolate and picture-perfect lakes.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", "international"),
            ("Maldives", "Maldives", "Overwater bungalows and pristine turquoise lagoons.", "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800", "international"),
            ("Nepal", "Nepal", "Himalayan spirituality, Pashupatinath and Muktinath.", "https://images.unsplash.com/photo-1605640840605-14ac1855827b?w=800", "international"),
        ]
        cur.executemany("INSERT INTO destinations (name, country, description, image_url, category) VALUES (%s,%s,%s,%s,%s)", destinations)

    cur.execute("SELECT COUNT(*) FROM packages")
    if cur.fetchone()[0] == 0:
        packages = [
            # ── DOMESTIC > DEVOTIONAL ──
            ("Varanasi Spiritual Journey", 6, "A soul-stirring pilgrimage to the ghats and temples of Kashi.", "https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=800", 14999, 5, 20, "Train, Hotel, All Meals, Guide", "Personal Expenses", "Day 1: Arrival, Ganga Aarti\nDay 2: Kashi Vishwanath Temple\nDay 3: Sarnath\nDay 4: Boat ride & ghats\nDay 5: Departure", "domestic", "devotional", True, 4.8, 120),
            ("Tirupati Darshan Package", 7, "Comfortable pilgrimage to Sri Venkateswara Temple.", "https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=800", 8999, 3, 25, "Bus, Hotel, Meals, VIP Darshan", "Personal Expenses", "Day 1: Arrival Tirupati\nDay 2: Tirumala Darshan\nDay 3: Padmavathi Temple, Departure", "domestic", "devotional", True, 4.9, 200),
            ("Char Dham Yatra", 4, "Sacred pilgrimage to Kedarnath, Badrinath, Gangotri & Yamunotri.", "https://images.unsplash.com/photo-1531761535209-180857e963b9?w=800", 45999, 14, 15, "Flights, Hotels, All Meals, Ponies, Palki", "Personal Expenses, Tips", "Day 1-2: Yamunotri\nDay 3-4: Gangotri\nDay 5-7: Kedarnath\nDay 8-10: Badrinath\nDay 11-14: Return", "domestic", "devotional", True, 4.7, 95),
            ("Rameshwaram & Kanyakumari", 2, "Spiritual south India tour covering Jyotirlinga and Land's End.", "https://images.unsplash.com/photo-1570458436416-b8fcccfe883f?w=800", 12999, 5, 20, "Train, Hotel, Breakfast, Guide", "Lunch, Dinner", "Day 1: Madurai Meenakshi\nDay 2: Rameshwaram Jyotirlinga\nDay 3: Dhanushkodi\nDay 4: Kanyakumari Sunrise\nDay 5: Departure", "domestic", "devotional", False, 4.6, 80),
            ("Shirdi & Nashik Pilgrimage", 1, "Visit Sai Baba's Shirdi and the holy city of Nashik.", "https://images.unsplash.com/photo-1588416936097-41850ab3d86d?w=800", 9999, 4, 20, "Bus, Hotel, All Meals", "Personal Expenses", "Day 1: Nashik Kumbh Ghats\nDay 2: Trimbakeshwar\nDay 3: Shirdi Sai Baba\nDay 4: Departure", "domestic", "devotional", False, 4.5, 110),
            ("Golden Triangle with Mathura", 3, "Agra, Jaipur & divine Mathura-Vrindavan Yatra.", "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800", 19999, 7, 20, "AC Coach, Hotel, Breakfast", "Meals, Entry Fees", "Day 1: Delhi\nDay 2: Mathura-Vrindavan\nDay 3: Agra Taj Mahal\nDay 4: Fatehpur Sikri\nDay 5-6: Jaipur\nDay 7: Departure", "domestic", "devotional", False, 4.6, 75),
            # ── DOMESTIC > VACATION ──
            ("Goa Beach Bliss", 1, "5 nights of sun, sand and sea in beautiful Goa.", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800", 15999, 6, 20, "Flights, Hotel, Breakfast, Sightseeing", "Lunch, Dinner, Personal Expenses", "Day 1: Arrival & North Goa beaches\nDay 2: South Goa exploration\nDay 3: Water sports\nDay 4: Old Goa heritage\nDay 5: Leisure\nDay 6: Departure", "domestic", "vacation", True, 4.5, 180),
            ("Kerala Backwaters", 2, "Houseboat cruise through tranquil Kerala backwaters.", "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=800", 22999, 7, 15, "Flights, Houseboat, All Meals, Ayurveda Session", "Personal Expenses, Tips", "Day 1: Arrival Kochi\nDay 2: Munnar hills\nDay 3: Thekkady\nDay 4-5: Alleppey houseboat\nDay 6: Kovalam beach\nDay 7: Departure", "domestic", "vacation", True, 4.8, 210),
            ("Himachal Snow Trek", 4, "Trek through the stunning snow-capped Himalayas.", "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800", 18999, 6, 12, "Transport, Camps, All Meals, Guide", "Personal Gear, Insurance", "Day 1: Manali arrival\nDay 2: Solang Valley\nDay 3: Rohtang Pass\nDay 4-5: Trek\nDay 6: Return", "domestic", "vacation", False, 4.6, 140),
            ("Andaman Paradise", 5, "Explore the pristine islands and coral reefs of Andaman.", "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800", 32999, 6, 15, "Flights, Resort, Breakfast, Ferry Tickets", "Scuba, Personal Expenses", "Day 1: Port Blair\nDay 2: Cellular Jail\nDay 3: Havelock Island\nDay 4: Radhanagar Beach\nDay 5: Neil Island\nDay 6: Departure", "domestic", "vacation", True, 4.9, 165),
            ("Leh Ladakh Expedition", 4, "High-altitude adventure through the world's top destinations.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", 38999, 8, 12, "Flights, Hotels, All Meals, Permit, Guide", "Personal Expenses, Insurance", "Day 1: Leh arrival & acclimatise\nDay 2: Shanti Stupa, Leh Palace\nDay 3: Nubra Valley\nDay 4: Pangong Lake\nDay 5: Tsomoriri\nDay 6: Magnetic Hill\nDay 7-8: Return", "domestic", "vacation", True, 4.8, 130),
            ("Ooty & Coorg Hills", 2, "Misty hills, tea gardens and waterfalls of South India.", "https://images.unsplash.com/photo-1586348943529-beaae6c28db9?w=800", 13999, 5, 18, "Bus, Hotel, Breakfast", "Meals, Entry Fees", "Day 1: Ooty arrival\nDay 2: Ooty sightseeing, Tea Museum\nDay 3: Coonoor, Nilgiri train\nDay 4: Coorg estates\nDay 5: Departure", "domestic", "vacation", False, 4.5, 90),
            # ── DOMESTIC > COUPLE ──
            ("Romantic Munnar Escape", 2, "Misty tea estates and waterfall walks for couples.", "https://images.unsplash.com/photo-1548013146-72479768bada?w=800", 17999, 4, 4, "Flights, Couple Resort, All Meals, Candle Dinner", "Personal Expenses", "Day 1: Arrival, welcome dinner\nDay 2: Tea plantation walks\nDay 3: Eravikulam, Waterfalls\nDay 4: Departure", "domestic", "couple", True, 4.9, 195),
            ("Goa Honeymoon Special", 1, "Private beach shacks, candlelit dinners and couples spa.", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800", 24999, 5, 4, "Flights, Boutique Resort, Breakfast & Dinner, Spa Session", "Lunch", "Day 1: Arrival, sundowner cruise\nDay 2: Private beach day\nDay 3: Water sports together\nDay 4: Couples spa\nDay 5: Departure", "domestic", "couple", True, 4.8, 220),
            ("Shimla Manali Couple Tour", 4, "Snow, romance and mountain magic for two.", "https://images.unsplash.com/photo-1502003148287-a65903ef16ab?w=800", 21999, 6, 4, "Flights, Hotel, Breakfast, Romantic Dinner", "Lunch", "Day 1: Shimla arrival\nDay 2: The Ridge, Mall Road\nDay 3: Kufri snow play\nDay 4: Manali arrival\nDay 5: Solang Valley\nDay 6: Departure", "domestic", "couple", True, 4.7, 175),
            ("Udaipur City of Love", 3, "The most romantic city in India for couples.", "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800", 18999, 4, 4, "Flights, Lake-view Hotel, Breakfast, Boat Ride, Romantic Dinner", "Lunch", "Day 1: Arrival, lake Pichola boat\nDay 2: City Palace, Saheliyon ki Bari\nDay 3: Eklingi Temple\nDay 4: Departure", "domestic", "couple", True, 4.9, 205),
            ("Pondicherry Couple Retreat", 2, "French charm, beaches and spirituality for two.", "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800", 11999, 3, 4, "Hotel, Breakfast, Cycling Tour, Candle Dinner", "Lunch", "Day 1: Arrival, French Quarter walk\nDay 2: Auroville, Serenity Beach\nDay 3: Paradise Beach, Departure", "domestic", "couple", False, 4.6, 85),
            ("Coorg Coffee Trail Couple", 2, "Romance amidst coffee plantations and misty hills.", "https://images.unsplash.com/photo-1611048661702-7b55eed346b4?w=800", 14999, 3, 4, "Resort, All Meals, Plantation Walk, Couples Bonfire", "Personal Expenses", "Day 1: Arrival, estate walk\nDay 2: Waterfalls, plantation tour\nDay 3: Departure", "domestic", "couple", False, 4.7, 100),
            # ── DOMESTIC > HOLIDAY ──
            ("Royal Rajasthan Family", 3, "Majestic forts and palaces for the whole family.", "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800", 28999, 8, 20, "Flights, Heritage Hotel, Breakfast, AC Coach", "Meals, Entry Fees", "Day 1: Jaipur\nDay 2: Amber Fort, City Palace\nDay 3: Pushkar\nDay 4: Jodhpur\nDay 5: Jaisalmer\nDay 6: Desert Safari\nDay 7: Udaipur\nDay 8: Departure", "domestic", "holiday", True, 4.7, 160),
            ("Kashmir Paradise", 4, "Heaven on earth - Dal Lake and snow peaks.", "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800", 32999, 6, 20, "Flights, Houseboat + Hotel, All Meals, Shikara Ride", "Personal Expenses", "Day 1: Srinagar Dal Lake Houseboat\nDay 2: Shikara ride, Mughal Gardens\nDay 3: Pahalgam\nDay 4: Gulmarg\nDay 5: Sonamarg\nDay 6: Departure", "domestic", "holiday", True, 4.9, 190),
            ("North East Explorer", 4, "Meghalaya, Assam and Sikkim for the adventurous family.", "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800", 35999, 9, 15, "Flights, Hotels, All Meals, Safari", "Personal Expenses", "Day 1: Guwahati\nDay 2: Kaziranga Safari\nDay 3: Shillong\nDay 4: Cherrapunji\nDay 5: Mawlynnong\nDay 6: Gangtok\nDay 7: Nathula\nDay 8: Darjeeling\nDay 9: Departure", "domestic", "holiday", True, 4.8, 110),
            ("Goa Family Fun Package", 1, "Beach, water parks and fun for the whole family.", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800", 19999, 5, 25, "Flights, Resort, Breakfast, Water Park Entry, Cruise", "Meals, Personal Expenses", "Day 1: Arrival, North Goa beach\nDay 2: Water park day\nDay 3: South Goa sightseeing\nDay 4: Cruise & shopping\nDay 5: Departure", "domestic", "holiday", True, 4.5, 155),
            ("Sikkim & Darjeeling Holiday", 4, "Tea gardens, monasteries and mountain views.", "https://images.unsplash.com/photo-1553651688-2624f2b74e74?w=800", 24999, 7, 15, "Flights, Hotels, Breakfast, Toy Train, Permits", "Lunch, Dinner", "Day 1: NJP arrival, Darjeeling\nDay 2: Tiger Hill sunrise, Tea estates\nDay 3: Toy train, Batasia Loop\nDay 4: Gangtok\nDay 5: Tsomgo Lake\nDay 6: Pelling Monastery\nDay 7: Departure", "domestic", "holiday", False, 4.7, 130),
            ("Tamil Nadu Temple Circuit", 2, "Grand temples and cultural heritage of Tamil Nadu.", "https://images.unsplash.com/photo-1570458436416-b8fcccfe883f?w=800", 16999, 6, 20, "Bus, Hotels, All Meals, Guide", "Personal Expenses", "Day 1: Chennai Kapaleeshwarar\nDay 2: Kanchipuram temples\nDay 3: Thanjavur Big Temple\nDay 4: Madurai Meenakshi\nDay 5: Rameshwaram\nDay 6: Departure", "domestic", "holiday", False, 4.6, 75),
            # ── INTERNATIONAL > DEVOTIONAL ──
            ("Sri Lanka Ramayana Trail", 9, "Trace Lord Rama's footsteps across beautiful Sri Lanka.", "https://images.unsplash.com/photo-1540730491613-a96897a4af03?w=800", 65999, 8, 15, "Flights, Hotels, All Meals, Guide", "Personal Expenses", "Day 1: Colombo\nDay 2: Ashok Vatika, Sita Eliya\nDay 3: Nuwara Eliya\nDay 4: Kandy Tooth Relic Temple\nDay 5: Trincomalee\nDay 6: Anuradhapura\nDay 7: Negombo\nDay 8: Departure", "international", "devotional", True, 4.8, 85),
            ("Nepal Pashupatinath Yatra", 14, "Kathmandu Valley temples and Himalayan spirituality.", "https://images.unsplash.com/photo-1605640840605-14ac1855827b?w=800", 42999, 6, 15, "Flights, Hotels, All Meals, Guide, Darshan Pass", "Personal Expenses", "Day 1: Kathmandu arrival\nDay 2: Pashupatinath Aarti\nDay 3: Swayambhunath\nDay 4: Muktinath\nDay 5: Pokhara Phewa Lake\nDay 6: Departure", "international", "devotional", True, 4.7, 90),
            ("Bhutan Spiritual Journey", 14, "Tiger's Nest Monastery and Buddhist paradise.", "https://images.unsplash.com/photo-1553581987-e5bc62cf77e1?w=800", 75999, 7, 10, "Flights, Boutique Hotels, All Meals, Guide, Entry Fees", "Personal Expenses", "Day 1: Paro arrival\nDay 2: Tiger's Nest Trek\nDay 3: Thimphu\nDay 4: Punakha Dzong\nDay 5: Phobjikha Valley\nDay 6: Haa Valley\nDay 7: Departure", "international", "devotional", True, 4.9, 70),
            ("Cambodia Angkor Temples", 9, "Ancient Hindu temples and the glory of the Khmer Empire.", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800", 58999, 6, 15, "Flights, Hotels, Breakfast, Guided Temple Tours", "Lunch, Dinner", "Day 1: Siem Reap arrival\nDay 2: Angkor Wat sunrise\nDay 3: Bayon, Ta Prohm\nDay 4: Banteay Srei\nDay 5: Tonle Sap Lake\nDay 6: Departure", "international", "devotional", False, 4.7, 65),
            ("Myanmar Golden Pagodas", 9, "Shwedagon Pagoda and the spiritual heart of Myanmar.", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800", 52999, 7, 12, "Flights, Hotels, All Meals, Guide", "Personal Expenses, Visa", "Day 1: Yangon, Shwedagon Pagoda\nDay 2: Bago temples\nDay 3: Mandalay\nDay 4: Inle Lake\nDay 5: Bagan Temples\nDay 6: Balloon ride\nDay 7: Departure", "international", "devotional", False, 4.6, 55),
            ("Israel Holy Land Tour", 10, "Walk in the footsteps of faith across Jerusalem and Bethlehem.", "https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800", 185999, 10, 12, "Flights, Hotels, All Meals, Guided Tours", "Personal Expenses, Visa", "Day 1: Tel Aviv\nDay 2: Jerusalem Old City\nDay 3: Church of Holy Sepulchre\nDay 4: Bethlehem\nDay 5: Dead Sea\nDay 6: Nazareth\nDay 7: Sea of Galilee\nDay 8: Jordan Petra\nDay 9: Amman\nDay 10: Departure", "international", "devotional", False, 4.9, 45),
            # ── INTERNATIONAL > VACATION ──
            ("Thailand Explorer", 9, "Bangkok, Pattaya and Phuket in one grand tour.", "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800", 49999, 8, 20, "Flights, Hotel, Daily Breakfast, Transfers", "Meals, Personal Expenses", "Day 1-2: Bangkok\nDay 3-4: Pattaya\nDay 5-6: Phuket\nDay 7: Phi Phi Island\nDay 8: Departure", "international", "vacation", True, 4.7, 170),
            ("Singapore Delight", 11, "Discover the ultra-modern Lion City.", "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800", 58999, 5, 15, "Flights, Hotel, Breakfast, City Tour, Universal Studios", "Meals, Personal Expenses", "Day 1: Arrival, Gardens by the Bay\nDay 2: Sentosa, Universal Studios\nDay 3: Chinatown, Marina Bay\nDay 4: Shopping\nDay 5: Departure", "international", "vacation", False, 4.6, 120),
            ("Switzerland Alps", 12, "Snow-capped peaks, pristine lakes and Swiss charm.", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", 145999, 9, 12, "Flights, Hotel, Breakfast, Rail Pass, Guided Tours", "Meals, Personal Expenses", "Day 1: Zurich\nDay 2: Lucerne\nDay 3: Interlaken\nDay 4: Jungfraujoch\nDay 5: Grindelwald\nDay 6: Geneva\nDay 7: Zermatt\nDay 8: Bern\nDay 9: Departure", "international", "vacation", True, 5.0, 90),
            ("Maldives Island Retreat", 13, "Overwater bungalows, snorkelling and pristine beaches.", "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800", 98999, 5, 10, "Flights, Water Villa, All Meals, Snorkelling, Sunset Cruise", "Personal Expenses", "Day 1: Arrival resort check-in\nDay 2: Snorkelling & water sports\nDay 3: Dolphin watching, Spa\nDay 4: Island hopping\nDay 5: Departure", "international", "vacation", True, 4.9, 200),
            ("Japan Cherry Blossom Tour", 10, "Tokyo, Kyoto and Osaka in full spring bloom.", "https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?w=800", 135999, 10, 12, "Flights, Hotels, Breakfast, JR Pass, Guided Tours", "Lunch, Dinner", "Day 1-3: Tokyo\nDay 4: Mount Fuji\nDay 5-6: Kyoto temples\nDay 7: Nara deer park\nDay 8-9: Osaka\nDay 10: Departure", "international", "vacation", True, 4.8, 115),
            ("Vietnam Heritage Trail", 9, "Halong Bay, Hoi An and the charm of Southeast Asia.", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800", 45999, 8, 15, "Flights, Hotels, Breakfast, Halong Bay Cruise", "Lunch, Dinner", "Day 1: Hanoi\nDay 2-3: Halong Bay Cruise\nDay 4: Hue Imperial City\nDay 5-6: Hoi An Old Town\nDay 7: Ho Chi Minh City\nDay 8: Departure", "international", "vacation", False, 4.6, 80),
            # ── INTERNATIONAL > COUPLE ──
            ("Bali Honeymoon", 8, "Romantic getaway to the magical island of Bali.", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800", 55999, 7, 10, "Flights, Villa, Breakfast, Transfers", "Meals, Entry Fees", "Day 1: Arrival Seminyak\nDay 2: Ubud temples\nDay 3: Rice terraces\nDay 4: Nusa Penida\nDay 5: Uluwatu sunset\nDay 6: Leisure\nDay 7: Departure", "international", "couple", True, 4.9, 260),
            ("Maldives Honeymoon Bliss", 13, "Ultimate romance in paradise with private villa.", "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800", 125999, 6, 4, "Flights, Private Water Villa, All Inclusive, Couples Spa, Sunset Cruise", "Personal Expenses", "Day 1: Arrival by seaplane\nDay 2: Snorkelling & water sports\nDay 3: Couples spa, sunset cruise\nDay 4: Beach picnic\nDay 5: Island hopping\nDay 6: Departure", "international", "couple", True, 5.0, 240),
            ("Dubai Glamour", 10, "Experience the luxury and grandeur of Dubai.", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800", 62999, 6, 15, "Flights, 5-Star Hotel, Breakfast, City Tour, Desert Safari", "Meals, Personal Expenses", "Day 1: Arrival & Downtown\nDay 2: Burj Khalifa\nDay 3: Desert Safari\nDay 4: Palm Jumeirah\nDay 5: Old Dubai\nDay 6: Departure", "international", "couple", True, 4.8, 175),
            ("Santorini & Mykonos Couple", 12, "Blue domes, sunsets and Aegean romance.", "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800", 175999, 7, 4, "Flights, Cave Hotel, Breakfast, Sunset Cruise, Wine Tour", "Lunch, Dinner", "Day 1: Santorini arrival\nDay 2: Oia sunset\nDay 3: Wine tour, Beach\nDay 4: Ferry to Mykonos\nDay 5: Mykonos beaches\nDay 6: Little Venice\nDay 7: Departure", "international", "couple", True, 4.9, 75),
            ("Mauritius Couple Escape", 13, "Turquoise lagoons and lush mountains for two.", "https://images.unsplash.com/photo-1586861635167-e5223aadc9fe?w=800", 89999, 6, 4, "Flights, Beach Resort, All Inclusive, Couples Spa, Catamaran", "Personal Expenses", "Day 1: Arrival, welcome dinner\nDay 2: Catamaran island cruise\nDay 3: Couples spa, beach\nDay 4: Black River Gorges\nDay 5: Chamarel Waterfall\nDay 6: Departure", "international", "couple", True, 4.8, 95),
            ("Kenya Safari Romance", 10, "Watch the Great Migration with your love.", "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800", 152999, 8, 4, "Flights, Tented Safari Camps, All Inclusive, Game Drives", "Personal Expenses, Visa", "Day 1: Nairobi\nDay 2: Amboseli\nDay 3-4: Masai Mara Safari\nDay 5: Great Migration\nDay 6: Diani Beach\nDay 7: Couples Dinner\nDay 8: Departure", "international", "couple", False, 4.9, 55),
            # ── INTERNATIONAL > HOLIDAY ──
            ("Australia Family Adventure", 9, "Sydney, Melbourne and Gold Coast fun for all ages.", "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800", 195999, 12, 12, "Flights, Hotels, Breakfast, Theme Parks, Wildlife Tour", "Meals, Personal Expenses", "Day 1-3: Sydney\nDay 4: Blue Mountains\nDay 5-6: Melbourne\nDay 7: Great Ocean Road\nDay 8-10: Gold Coast\nDay 11: Brisbane\nDay 12: Departure", "international", "holiday", True, 4.7, 80),
            ("Europe Family Special", 12, "Paris, Rome and Amsterdam in one magical trip.", "https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=800", 215999, 14, 12, "Flights, Hotels, Breakfast, Guided Tours, Rail Pass", "Meals", "Day 1-3: Paris Eiffel\nDay 4: TGV to Rome\nDay 5-7: Colosseum, Vatican\nDay 8-9: Florence\nDay 10: Venice\nDay 11-12: Amsterdam\nDay 13: Rhine cruise\nDay 14: Departure", "international", "holiday", True, 4.8, 70),
            ("Malaysia & Singapore Family", 11, "Petronas Towers, Legoland and Universal Studios.", "https://images.unsplash.com/photo-1559628376-f3fe5f782a2a?w=800", 72999, 7, 20, "Flights, Hotels, Breakfast, Theme Parks, Cable Car", "Lunch, Dinner", "Day 1: KL, KLCC\nDay 2: Petronas, Batu Caves\nDay 3: Legoland Johor\nDay 4: Singapore\nDay 5: Universal Studios\nDay 6: Gardens by the Bay\nDay 7: Departure", "international", "holiday", True, 4.6, 140),
            ("New Zealand Wilderness", 12, "Hobbiton, fiords and bungee for adventurous families.", "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800", 189999, 10, 10, "Flights, Hotels, Breakfast, Hobbiton, Milford Sound Cruise", "Meals, Personal Expenses", "Day 1-2: Auckland\nDay 3: Hobbiton Rotorua\nDay 4: Wellington\nDay 5: Queenstown Bungee\nDay 6: Milford Sound\nDay 7: Glacier Trek\nDay 8: Christchurch\nDay 9-10: Departure", "international", "holiday", False, 4.8, 50),
            ("South Africa Safari Holiday", 11, "Kruger National Park and Cape Town for families.", "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800", 175999, 9, 10, "Flights, Safari Lodges + City Hotel, All Inclusive, Game Drives", "Personal Expenses, Visa", "Day 1: Johannesburg\nDay 2-4: Kruger Safari, Big Five\nDay 5: Cape Town Table Mountain\nDay 6: Cape of Good Hope\nDay 7: Winelands\nDay 8: Robben Island\nDay 9: Departure", "international", "holiday", False, 4.9, 60),
            ("USA East Coast Family Tour", 11, "New York, Washington DC and Niagara Falls.", "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=800", 245999, 12, 12, "Flights, Hotels, Breakfast, City Pass, Niagara Boat", "Meals, Personal Expenses", "Day 1-3: New York City\nDay 4: Statue of Liberty\nDay 5-6: Washington DC\nDay 7: Smithsonian, Capitol\nDay 8: Philadelphia\nDay 9-10: Boston\nDay 11: Niagara Falls\nDay 12: Departure", "international", "holiday", True, 4.7, 85),
        ]
        cur.executemany(
            "INSERT INTO packages (title,destination_id,description,image_url,price,duration_days,max_persons,includes,excludes,itinerary,category,sub_category,is_featured,rating,likes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            packages
        )

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
    sub_category = request.args.get("sub_category", "")
    featured = request.args.get("featured", "")
    search = request.args.get("search", "")
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = "SELECT p.*, d.name as destination_name, d.country FROM packages p JOIN destinations d ON p.destination_id = d.id WHERE 1=1"
    params = []
    if category:
        query += " AND p.category = %s"; params.append(category)
    if sub_category:
        query += " AND p.sub_category = %s"; params.append(sub_category)
    if featured == "true":
        query += " AND p.is_featured = TRUE"
    if search:
        query += " AND (p.title ILIKE %s OR d.name ILIKE %s OR p.sub_category ILIKE %s)"; params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
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


@app.route("/api/packages/<int:pkg_id>/like", methods=["POST"])
@token_required
def toggle_like(pkg_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id FROM package_likes WHERE user_id=%s AND package_id=%s", (request.user_id, pkg_id))
    existing = cur.fetchone()
    if existing:
        cur.execute("DELETE FROM package_likes WHERE user_id=%s AND package_id=%s", (request.user_id, pkg_id))
        cur.execute("UPDATE packages SET likes = GREATEST(likes - 1, 0) WHERE id=%s RETURNING likes", (pkg_id,))
        liked = False
    else:
        cur.execute("INSERT INTO package_likes (user_id, package_id) VALUES (%s,%s)", (request.user_id, pkg_id))
        cur.execute("UPDATE packages SET likes = likes + 1 WHERE id=%s RETURNING likes", (pkg_id,))
        liked = True
    new_likes = cur.fetchone()["likes"]
    conn.commit(); cur.close(); conn.close()
    return jsonify({"liked": liked, "likes": new_likes})


@app.route("/api/packages/<int:pkg_id>/liked", methods=["GET"])
@token_required
def check_liked(pkg_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM package_likes WHERE user_id=%s AND package_id=%s", (request.user_id, pkg_id))
    liked = cur.fetchone() is not None
    cur.close(); conn.close()
    return jsonify({"liked": liked})


@app.route("/api/packages", methods=["POST"])
@admin_required
def create_package():
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO packages (title,destination_id,description,image_url,price,duration_days,max_persons,includes,excludes,itinerary,category,sub_category,is_featured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (data["title"],data["destination_id"],data.get("description"),data.get("image_url"),data["price"],data["duration_days"],data.get("max_persons",10),data.get("includes"),data.get("excludes"),data.get("itinerary"),data.get("category","domestic"),data.get("sub_category","vacation"),data.get("is_featured",False)))
    pkg = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(pkg)), 201


@app.route("/api/packages/<int:pkg_id>", methods=["PUT"])
@admin_required
def update_package(pkg_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE packages SET title=%s,description=%s,image_url=%s,price=%s,duration_days=%s,max_persons=%s,includes=%s,excludes=%s,itinerary=%s,category=%s,sub_category=%s,is_featured=%s WHERE id=%s RETURNING *",
                (data["title"],data.get("description"),data.get("image_url"),data["price"],data["duration_days"],data.get("max_persons",10),data.get("includes"),data.get("excludes"),data.get("itinerary"),data.get("category","domestic"),data.get("sub_category","vacation"),data.get("is_featured",False),pkg_id))
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
    cur.execute("""
        SELECT b.*, p.title as package_title, p.image_url, p.duration_days,
               u.name as user_name, u.email as user_email
        FROM bookings b
        JOIN packages p ON b.package_id = p.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
    """)
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(b) for b in result])


@app.route("/api/bookings/<int:booking_id>/status", methods=["PUT"])
@admin_required
def update_booking_status(booking_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE bookings SET status=%s, payment_status=%s WHERE id=%s RETURNING *",
                (data.get("status"), data.get("payment_status"), booking_id))
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
    cur.execute("INSERT INTO reviews (user_id,package_id,rating,comment) VALUES (%s,%s,%s,%s)", (request.user_id, pkg_id, data["rating"], data.get("comment")))
    cur.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE package_id=%s", (pkg_id,))
    avg, count = cur.fetchone()
    cur.execute("UPDATE packages SET rating=%s, num_reviews=%s WHERE id=%s", (round(float(avg), 1), count, pkg_id))
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
    cur.execute("INSERT INTO enquiries (name,email,phone,message) VALUES (%s,%s,%s,%s) RETURNING *",
                (data["name"], data["email"], data.get("phone"), data["message"]))
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


@app.route("/api/enquiries/<int:enquiry_id>/status", methods=["PUT"])
@admin_required
def update_enquiry_status(enquiry_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE enquiries SET status=%s WHERE id=%s RETURNING *",
                (data.get("status"), enquiry_id))
    enquiry = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return jsonify(dict(enquiry))


# ─────────────────────────────────────────
# ADMIN — USERS LIST (NEW)
# ─────────────────────────────────────────

@app.route("/api/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT u.id, u.name, u.email, u.is_admin, u.created_at,
               COUNT(b.id) as booking_count
        FROM users u
        LEFT JOIN bookings b ON b.user_id = u.id
        WHERE u.is_admin = FALSE
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    result = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([dict(u) for u in result])


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
    cur.execute("SELECT COUNT(*) as total FROM bookings WHERE status='pending'")
    pending_bookings = cur.fetchone()["total"]
    cur.close(); conn.close()
    return jsonify({
        "total_users": users,
        "total_bookings": bookings,
        "total_revenue": float(revenue),
        "total_packages": packages,
        "new_enquiries": new_enquiries,
        "pending_bookings": pending_bookings
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "Sai Anjenya Yatra Travel App"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)