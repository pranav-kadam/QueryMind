import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(current_dir, 'example.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    budget REAL NOT NULL
)
''')

employees_data = [
    (1, 'John Doe', 'Sales', 50000),
    (2, 'Jane Smith', 'Marketing', 60000),
    (3, 'Bob Johnson', 'Engineering', 75000),
    (4, 'Alice Brown', 'Human Resources', 55000),
    (5, 'Charlie Davis', 'Sales', 52000)
]

cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?)', employees_data)

departments_data = [
    (1, 'Sales', 200000),
    (2, 'Marketing', 150000),
    (3, 'Engineering', 300000),
    (4, 'Human Resources', 100000)
]

cursor.executemany('INSERT OR REPLACE INTO departments VALUES (?, ?, ?)', departments_data)

conn.commit()
conn.close()

db_uri = f'sqlite:///{db_path}'
print(f"Database created and populated successfully.")
print(f"Your database URI is: {db_uri}")