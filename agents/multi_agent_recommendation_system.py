# multi_agent_recommendation_system.py (Humanized Version)

import sqlite3
from datetime import datetime
import random

# MemoryAgent: Handles all DB interactions
class MemoryAgent:
    def __init__(self, db_name='recommendation.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self._initialize_db()

    def _initialize_db(self):
        cursor = self.conn.cursor()

        # Basic schema: customers, products, browsing history, and feedback
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            location TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price REAL
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS browsing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            timestamp TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            clicked INTEGER,
            timestamp TEXT
        )''')

        self.conn.commit()

    def fetch(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.lastrowid


# CustomerAgent: Retrieves customer info
class CustomerAgent:
    def __init__(self, memory):
        self.memory = memory

    def get_customer_profile(self, customer_id):
        customer = self.memory.fetch("SELECT * FROM customers WHERE id = ?", (customer_id,))
        return customer[0] if customer else None


# ProductAgent: Retrieves products by filters
class ProductAgent:
    def __init__(self, memory):
        self.memory = memory

    def get_products_by_category(self, category):
        return self.memory.fetch("SELECT * FROM products WHERE category = ?", (category,))

    def get_all_products(self):
        return self.memory.fetch("SELECT * FROM products")


# RecommendationEngineAgent: Basic collaborative filter logic
class RecommendationEngineAgent:
    def __init__(self, memory, product_agent):
        self.memory = memory
        self.product_agent = product_agent

    def recommend(self, customer_id, top_n=5):
        # Fetch user browsing history to infer interests
        history = self.memory.fetch(
            "SELECT product_id FROM browsing_history WHERE customer_id = ? ORDER BY timestamp DESC",
            (customer_id,)
        )
        product_ids = [row[0] for row in history]

        if not product_ids:
            # Fallback: random products if no history
            all_products = self.product_agent.get_all_products()
            return random.sample(all_products, min(top_n, len(all_products)))

        # Use the latest viewed product's category for recommendations
        last_product_id = product_ids[0]
        category_data = self.memory.fetch("SELECT category FROM products WHERE id = ?", (last_product_id,))

        if not category_data:
            return random.sample(self.product_agent.get_all_products(), top_n)

        category = category_data[0][0]
        same_category_products = self.product_agent.get_products_by_category(category)

        return random.sample(same_category_products, min(top_n, len(same_category_products)))


# FeedbackAgent: Stores likes/dislikes
class FeedbackAgent:
    def __init__(self, memory):
        self.memory = memory

    def record_feedback(self, customer_id, product_id, clicked):
        timestamp = datetime.now().isoformat()
        self.memory.execute(
            "INSERT INTO feedback (customer_id, product_id, clicked, timestamp) VALUES (?, ?, ?, ?)",
            (customer_id, product_id, clicked, timestamp)
        )
