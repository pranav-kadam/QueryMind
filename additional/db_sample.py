import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(current_dir, 'products.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
)
''')

products_data = [
    (1, 'Laptop', 'Electronics', 999.99),
    (2, 'Desk Chair', 'Furniture', 199.99),
    (3, 'Electric Kettle', 'Home Appliances', 29.99),
    (4, 'Smartphone', 'Electronics', 799.99),
    (5, 'Desk Lamp', 'Furniture', 49.99)
]

cursor.executemany('INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?)', products_data)

conn.commit()
conn.close()

db_uri = f'sqlite:///{db_path}'
print(f"Database created and populated successfully.")
print(f"Your database URI is: {db_uri}")
