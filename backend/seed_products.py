"""
SCRIPT 3 — seed_products.py
Inserts 50+ products across multiple categories.
Safe to re-run — skips insert if products already exist.
Run AFTER seed_admin.py.

Usage:
    python seed_products.py
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_db():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise RuntimeError("DATABASE_URL not set in .env")
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return psycopg2.connect(db_url)

# ── Product list ───────────────────────────────────────────────────────────
# Columns: (name, description, price, image_url, stock, max_qty, delivery_fee)
PRODUCTS = [

    # ── AnyTime Snacks & Meals ─────────────────────────────────────────────
    ('Veg Sandwich',
     'AnyTime | Fresh vegetables with chutney in toasted bread',
     60.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 50, 10, 0.0),

    ('Paneer Sandwich',
     'AnyTime | Spiced cottage cheese filling in soft bread',
     80.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10, 0.0),

    ('Mushroom Sandwich',
     'AnyTime | Sauteed mushrooms with herbs in toasted bread',
     85.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10, 0.0),

    ('Corn Sandwich',
     'AnyTime | Sweet corn with mayo and veggies in bread',
     70.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10, 0.0),

    ('Veg Cheese Sandwich',
     'AnyTime | Fresh vegetables loaded with melted cheese',
     90.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 40, 10, 0.0),

    ('Paneer Cheese Sandwich',
     'AnyTime | Paneer and cheese combo in grilled bread',
     110.0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10, 0.0),

    ('Corn Cheese Sandwich',
     'AnyTime | Sweet corn with extra cheese in toasted bread',
     95.0,  'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400', 35, 10, 0.0),

    ('Bread Toast',
     'AnyTime | Crispy buttered bread toast, served with chutney',
     30.0,  'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=400', 60, 10, 0.0),

    ('Veg Maggi Noodles',
     'AnyTime | Classic Maggi noodles cooked with fresh vegetables',
     60.0,  'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400', 50, 10, 0.0),

    ('Masala Maggi',
     'AnyTime | Spicy masala Maggi with onion, tomato and chillies',
     70.0,  'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400', 50, 10, 0.0),

    ('Egg Maggi',
     'AnyTime | Maggi noodles topped with a fried egg',
     80.0,  'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400', 40, 10, 0.0),

    ('Poha',
     'AnyTime | Light and fluffy flattened rice with mustard and curry leaves',
     40.0,  'https://images.unsplash.com/photo-1606491956391-d7c59b6d30cf?w=400', 50, 10, 0.0),

    ('Upma',
     'AnyTime | South Indian semolina upma with vegetables',
     40.0,  'https://images.unsplash.com/photo-1606491956391-d7c59b6d30cf?w=400', 50, 10, 0.0),

    ('Idli (2 pcs)',
     'AnyTime | Soft steamed rice cakes served with sambar and chutney',
     30.0,  'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400', 60, 10, 0.0),

    ('Vada (2 pcs)',
     'AnyTime | Crispy fried lentil doughnuts with coconut chutney',
     40.0,  'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400', 50, 10, 0.0),

    ('Plain Dosa',
     'AnyTime | Thin crispy rice crepe served with sambar and chutney',
     50.0,  'https://images.unsplash.com/photo-1630383249896-6b85da99c60a?w=400', 40, 5,  0.0),

    ('Masala Dosa',
     'AnyTime | Crispy dosa filled with spiced potato masala',
     70.0,  'https://images.unsplash.com/photo-1630383249896-6b85da99c60a?w=400', 40, 5,  0.0),

    ('Puri Bhaji',
     'AnyTime | Deep-fried puffed bread with spiced potato curry',
     60.0,  'https://images.unsplash.com/photo-1606491956391-d7c59b6d30cf?w=400', 40, 5,  0.0),

    ('Chapati (3 pcs)',
     'AnyTime | Soft whole wheat flatbreads',
     30.0,  'https://images.unsplash.com/photo-1606491956391-d7c59b6d30cf?w=400', 50, 10, 0.0),

    ('Samosa (2 pcs)',
     'AnyTime | Crispy pastry filled with spiced potato and peas',
     30.0,  'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 60, 10, 0.0),

    # ── Beverages ──────────────────────────────────────────────────────────
    ('Masala Chai',
     'Beverages | Spiced ginger and cardamom tea',
     20.0,  'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400', 100, 10, 0.0),

    ('Filter Coffee',
     'Beverages | South Indian filter coffee with frothy milk',
     25.0,  'https://images.unsplash.com/photo-1509785307050-d4066910ec1e?w=400', 100, 10, 0.0),

    ('Fresh Lime Soda',
     'Beverages | Chilled lime soda, sweet or salted',
     30.0,  'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400', 80,  10, 0.0),

    ('Mango Lassi',
     'Beverages | Thick mango yogurt drink',
     50.0,  'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400', 60,  10, 0.0),

    ('Buttermilk',
     'Beverages | Chilled salted buttermilk with curry leaves',
     20.0,  'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400', 80,  10, 0.0),

    # ── Groceries | Oils ──────────────────────────────────────────────────
    ('Sesame Oil 500ml',
     'Groceries | Oil | Cold-pressed pure sesame oil',
     180.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30, 5, 40.0),

    ('Sesame Oil 1L',
     'Groceries | Oil | Cold-pressed pure sesame oil, family pack',
     320.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 20, 3, 40.0),

    ('Deepa Refined Oil 1L',
     'Groceries | Oil | Deepa brand refined cooking oil',
     150.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30, 5, 40.0),

    ('Groundnut Oil 1L',
     'Groceries | Oil | Cold-pressed groundnut oil',
     200.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 25, 5, 40.0),

    ('Sunflower Oil 1L',
     'Groceries | Oil | Refined sunflower cooking oil',
     160.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 30, 5, 40.0),

    ('Coconut Oil 500ml',
     'Groceries | Oil | Pure cold-pressed coconut oil',
     220.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 25, 5, 40.0),

    ('Mustard Oil 1L',
     'Groceries | Oil | Kachi ghani mustard oil for cooking',
     180.0, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 20, 5, 40.0),

    # ── Groceries | Pickles ───────────────────────────────────────────────
    ('Mango Pickle 300g',
     'Groceries | Pickles | Spicy raw mango pickle in sesame oil',
     90.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),

    ('Lemon Pickle 300g',
     'Groceries | Pickles | Tangy lemon pickle with spices',
     85.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 40, 10, 40.0),

    ('Mixed Vegetable Pickle 300g',
     'Groceries | Pickles | Assorted vegetables in spiced oil',
     80.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 35, 10, 40.0),

    ('Garlic Pickle 200g',
     'Groceries | Pickles | Bold and spicy garlic pickle',
     75.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 35, 10, 40.0),

    ('Gongura Pickle 300g',
     'Groceries | Pickles | Andhra-style sorrel leaf pickle',
     95.0,  'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 30, 10, 40.0),

    # ── Groceries | Rice & Grains ──────────────────────────────────────────
    ('Sona Masoori Rice 1kg',
     'Groceries | Rice | Premium quality Sona Masoori raw rice',
     70.0,  'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400', 50,  5, 40.0),

    ('Basmati Rice 1kg',
     'Groceries | Rice | Long-grain aged Basmati rice',
     120.0, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400', 40,  5, 40.0),

    ('Idli Rice 1kg',
     'Groceries | Rice | Short-grain rice ideal for idli and dosa batter',
     65.0,  'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400', 40,  5, 40.0),

    ('Wheat Flour (Atta) 1kg',
     'Groceries | Flour | Whole wheat atta for soft rotis',
     55.0,  'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400', 50,  5, 40.0),

    ('Sooji (Rava) 500g',
     'Groceries | Flour | Fine semolina for upma, halwa and dosa',
     40.0,  'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400', 50, 10, 40.0),

    # ── Groceries | Pulses & Dals ─────────────────────────────────────────
    ('Toor Dal 500g',
     'Groceries | Dal | Split pigeon peas, ideal for sambar',
     75.0,  'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400', 40, 10, 40.0),

    ('Moong Dal 500g',
     'Groceries | Dal | Split yellow moong lentils',
     80.0,  'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400', 40, 10, 40.0),

    ('Urad Dal 500g',
     'Groceries | Dal | Black gram dal for idli batter and dal makhani',
     85.0,  'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400', 35, 10, 40.0),

    ('Chana Dal 500g',
     'Groceries | Dal | Split Bengal gram for dal and sundal',
     70.0,  'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400', 40, 10, 40.0),

    ('Masoor Dal 500g',
     'Groceries | Dal | Red lentils, quick-cook and nutritious',
     65.0,  'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400', 40, 10, 40.0),

    # ── Groceries | Spices ────────────────────────────────────────────────
    ('Turmeric Powder 100g',
     'Groceries | Spices | Pure turmeric powder, bright and aromatic',
     35.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 60, 10, 40.0),

    ('Red Chilli Powder 100g',
     'Groceries | Spices | Fiery red chilli powder',
     40.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 60, 10, 40.0),

    ('Coriander Powder 100g',
     'Groceries | Spices | Ground coriander seeds, fragrant and mild',
     35.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 60, 10, 40.0),

    ('Garam Masala 50g',
     'Groceries | Spices | Blended whole spices, aromatic and warm',
     55.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 50, 10, 40.0),

    ('Mustard Seeds 100g',
     'Groceries | Spices | Black mustard seeds for tempering',
     25.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 60, 10, 40.0),

    ('Cumin Seeds 100g',
     'Groceries | Spices | Whole cumin seeds, earthy and nutty',
     45.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 60, 10, 40.0),

    ('Curry Leaves (Fresh)',
     'Groceries | Spices | Fresh curry leaves, sold per bunch',
     10.0,  'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400', 100, 10, 0.0),

    # ── Groceries | Snacks ────────────────────────────────────────────────
    ('Murukku 200g',
     'Groceries | Snacks | Crispy rice flour spirals, lightly spiced',
     60.0,  'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 50, 10, 40.0),

    ('Mixture 200g',
     'Groceries | Snacks | South Indian spicy snack mix',
     55.0,  'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 50, 10, 40.0),

    ('Ladoo 4 pcs',
     'Groceries | Sweets | Besan or boondi ladoo, homemade style',
     80.0,  'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 40, 10, 40.0),

    ('Halwa 200g',
     'Groceries | Sweets | Sooji or carrot halwa, rich and ghee-laden',
     70.0,  'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 30, 10, 40.0),

]

def seed_products():
    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM products')
    count = c.fetchone()[0]
    if count > 0:
        print(f"ℹ️  {count} products already exist.")
        ans = input("   Clear existing products and re-seed? (yes/no): ").strip().lower()
        if ans != 'yes':
            print("   Skipped. No changes made.")
            conn.close()
            return
        c.execute('DELETE FROM products')
        print("   ✅ Existing products cleared.")

    now = datetime.now()
    for row in PRODUCTS:
        c.execute('''
            INSERT INTO products
                (name, description, price, image_url, stock, max_qty, delivery_fee, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (*row, now))

    conn.commit()
    conn.close()

    print(f"\n✅ {len(PRODUCTS)} products inserted successfully.")
    print("🚀 Your app is ready. Start it with:  python app.py")

if __name__ == '__main__':
    seed_products()
