# app.py (Cleaned FastAPI App Entry Point)

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from agents.multi_agent_recommendation_system import (
    MemoryAgent,
    CustomerAgent,
    ProductAgent,
    RecommendationEngineAgent,
    FeedbackAgent
)

# Initialize FastAPI and templates directory
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize memory and all agents
memory = MemoryAgent()
customer_agent = CustomerAgent(memory)
product_agent = ProductAgent(memory)
recommender = RecommendationEngineAgent(memory, product_agent)
feedback_agent = FeedbackAgent(memory)

# Define feedback model
class Feedback(BaseModel):
    customer_id: int
    product_id: int
    clicked: int

# Homepage
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Recommendations view
@app.get("/recommendations/{customer_id}", response_class=HTMLResponse)
async def get_recommendations(customer_id: int, request: Request):
    customer = customer_agent.get_customer_profile(customer_id)

    if not customer:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Customer not found. Please check the ID."
        })

    recommendations = recommender.recommend(customer_id)
    return templates.TemplateResponse("recommendations.html", {
        "request": request,
        "customer": customer,
        "recommendations": recommendations
    })

# Feedback endpoint
@app.post("/feedback")
async def submit_feedback(
    customer_id: int = Form(...),
    product_id: int = Form(...),
    clicked: int = Form(...)
):
    feedback_agent.record_feedback(customer_id, product_id, clicked)
    return {"status": "feedback recorded"}
import sqlite3
import os

# Connect to the database (or create if not exists)
db_path = "recommendation.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS browsing_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        timestamp TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
''')

# 2. Check if data already exists
cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]

# 3. Insert demo data only if DB is empty
if customer_count == 0:
    print("🟢 Inserting sample data...")
    cursor.executemany('''
        INSERT INTO customers (id, name)
        VALUES (?, ?)
    ''', [
        (1, "Alice Smith"),
        (2, "Bob Johnson"),
        (3, "Charlie Lee")
    ])

    cursor.executemany('''
        INSERT INTO products (id, name, category, price)
        VALUES (?, ?, ?, ?)
    ''', [
        (1, "Wireless Mouse", "Electronics", 29.99),
        (2, "Bluetooth Headphones", "Electronics", 49.99),
        (3, "Yoga Mat", "Fitness", 19.99),
        (4, "Stainless Steel Water Bottle", "Fitness", 15.99),
        (5, "Notebook", "Stationery", 4.99)
    ])

    cursor.executemany('''
        INSERT INTO browsing_history (customer_id, product_id, timestamp)
        VALUES (?, ?, datetime('now'))
    ''', [
        (1, 1),
        (1, 2),
        (2, 3),
        (3, 5),
        (3, 4)
    ])
    print("✅ Sample data inserted.")
else:
    print("ℹ️ Demo data already exists. Skipping insert.")

conn.commit()
conn.close()
