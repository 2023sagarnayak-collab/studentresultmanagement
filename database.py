import sqlite3

DATABASE = "student_results.db"


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            marks1 INTEGER NOT NULL,
            marks2 INTEGER NOT NULL,
            marks3 INTEGER NOT NULL,
            total INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, marks1, marks2, marks3, total, grade):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, marks1, marks2, marks3, total, grade)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, marks1, marks2, marks3, total, grade))

    conn.commit()
    conn.close()


def get_students():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()
    return students


if __name__ == "__main__":
    create_database()

    add_student(
        "Rahul",
        80,
        80,
        80,
        240,
        "B"
    )

    students = get_students()

    print("Student Records:")
    for student in students:
        print(student)