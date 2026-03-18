# wsgi.py
import sys
import os

# Add the backend folder to Python's path so 'app' can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, init_db, seed_sample_data

init_db()
seed_sample_data()

if __name__ == "__main__":
    app.run()