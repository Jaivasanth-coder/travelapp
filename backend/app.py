import os
import jwt
import bcrypt
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

# Load environment variables
if Path(".env").exists():
    load_dotenv(".env")
else:
    load_dotenv("env.properties")

# Create Flask app
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY environment variable is not set!")


# ─────────────────────────────────────────
# CORS & ROUTING
# ─────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


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
    """
    Connect to PostgreSQL.

    Priority:
    1. DATABASE_URL (Supabase / Render / any provider) — passed directly to
       psycopg2 as a DSN so percent-encoded characters (%40, %23 …) are
       handled correctly by the driver, NOT by hand-rolled string splitting.
    2. Individual DB_* env vars as fallback.
    """
    database_url = os.environ.get("DATABASE_URL", "")

    if database_url:
        # Let psycopg2 decode the URL — it handles %40 in passwords natively.
        # Supabase may return "postgres://" which psycopg2 accepts fine.
        return psycopg2.connect(dsn=database_url, connect_timeout=10)

    # Fallback: individual env vars (local dev)
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "traveldb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        connect_timeout=10,
    )


def validate_db_connection():
    """Call once at startup to confirm the DB is reachable."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        print("✅ Database connection OK")
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection FAILED: {e}")
        raise


# ─────────────────────────────────────────
# DB INITIALISATION
# ─────────────────────────────────────────

def init_db():
    """
    Initialise schema if needed.
    Add your CREATE TABLE IF NOT EXISTS statements here.
    """
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Example — replace with your real schema:
            # cur.execute("""
            #     CREATE TABLE IF NOT EXISTS users (
            #         id SERIAL PRIMARY KEY,
            #         email TEXT UNIQUE NOT NULL,
            #         password_hash TEXT NOT NULL,
            #         created_at TIMESTAMPTZ DEFAULT now()
            #     )
            # """)
            pass
        conn.commit()
        conn.close()
        print("✅ Database initialised")
    except Exception as e:
        print(f"⚠️  Database init error: {e}")


# ─────────────────────────────────────────
# YOUR API ROUTES GO BELOW
# ─────────────────────────────────────────

# @app.route("/api/users", methods=["GET"])
# def get_users(): ...


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    validate_db_connection()   # Fail fast if DB is unreachable
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))