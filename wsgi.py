import sys
import os
 
# Add the backend folder to Python path so 'app' module can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
 
# Importing app triggers init_db() and seed_sample_data() at module level
from app import app
 
if __name__ == "__main__":
    app.run()
 