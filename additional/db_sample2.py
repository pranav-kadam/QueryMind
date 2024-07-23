import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(current_dir, 'students.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    major TEXT NOT NULL,
    gpa REAL NOT NULL
)
''')

students_data = [
    (1, 'Alice Green', 'Computer Science', 3.8),
    (2, 'David Wilson', 'Mathematics', 3.6),
    (3, 'Eve Adams', 'Physics', 3.9),
    (4, 'Frank Miller', 'Chemistry', 3.7),
    (5, 'Grace Lee', 'Biology', 3.5)
]

cursor.executemany('INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?)', students_data)

conn.commit()
conn.close()

db_uri = f'sqlite:///{db_path}'
print(f"Database created and populated successfully.")
print(f"Your database URI is: {db_uri}")
