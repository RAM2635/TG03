import sqlite3


# Создаем соединение с базой данных
def init_db():
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    # Создаем таблицу students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def add_student(name, age, grade):
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
    conn.commit()
    conn.close()
