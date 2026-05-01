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

# Load environment variables
if Path(".env").exists():
    load_dotenv(".env")
else:
    load_dotenv("env.properties")



# Create Flask app
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET","POST","PUT","DELETE","OPTIONS"], "allow_headers": ["Content-Type","Authorization"]}})

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "sai-anjenya-yatra-secret-key")

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS



@app.route("/")
def index():
    # Serve the index.html file from your frontend folder
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

# Import database initialization and seed logic from backend
try:
    from backend.app import init_db
except ImportError:
    def init_db():
        print("Warning: backend.app not found. Database init skipped.")

# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Initialize DB if needed
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
