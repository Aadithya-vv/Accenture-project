import sqlite3

# Connect to the existing recommendation.db
conn = sqlite3.connect("recommendation.db")  # Make sure the file is in the same directory
cursor = conn.cursor()

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

# Insert sample customers (without email)
cursor.executemany('''
    INSERT INTO customers (id, name)
    VALUES (?, ?)
''', [
    (1, "Alice Smith"),
    (2, "Bob Johnson"),
    (3, "Charlie Lee")
])

# Insert sample products
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

# Insert sample browsing history
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

conn.commit()
conn.close()
print("Sample data inserted successfully!")
