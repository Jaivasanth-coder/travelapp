# wsgi.py
from app import app, init_db, seed_sample_data

init_db()
seed_sample_data()

if __name__ == "__main__":
    app.run()