import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change to your MySQL username
        password="Khyvam@1722",          # change to your MySQL password
        database="student_db"
    )


# ─────────────────────────────────────────
#  SETUP: CREATE DATABASE & TABLES
# ─────────────────────────────────────────

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Khyvam@1722"           # change to your MySQL password
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS student_db")
    cursor.execute("USE student_db")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100) NOT NULL,
            email      VARCHAR(100) UNIQUE NOT NULL,
            branch     VARCHAR(50)  NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            result_id  INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            subject    VARCHAR(100) NOT NULL,
            marks      INT NOT NULL CHECK (marks BETWEEN 0 AND 100),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables ready.\n")


# ─────────────────────────────────────────
#  STUDENT OPERATIONS
# ─────────────────────────────────────────

def add_student():
    name   = input("Enter student name   : ").strip()
    email  = input("Enter student email  : ").strip()
    branch = input("Enter branch         : ").strip()

    if not name or not email or not branch:
        print("Error: All fields are required.\n")
        return

    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email, branch) VALUES (%s, %s, %s)",
            (name, email, branch)
        )
        conn.commit()
        print(f"Student '{name}' added successfully (ID: {cursor.lastrowid}).\n")
    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


def view_all_students():
    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name, email, branch FROM students ORDER BY student_id")
        rows = cursor.fetchall()

        if not rows:
            print("No students found.\n")
            return

        print(f"\n{'ID':<6} {'Name':<25} {'Email':<30} {'Branch'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<6} {row[1]:<25} {row[2]:<30} {row[3]}")
        print()
    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


def update_student():
    student_id = input("Enter student ID to update: ").strip()
    if not student_id.isdigit():
        print("Error: Invalid ID.\n")
        return

    print("Leave a field blank to keep it unchanged.")
    name   = input("New name   : ").strip()
    email  = input("New email  : ").strip()
    branch = input("New branch : ").strip()

    fields, values = [], []
    if name:   fields.append("name = %s");   values.append(name)
    if email:  fields.append("email = %s");  values.append(email)
    if branch: fields.append("branch = %s"); values.append(branch)

    if not fields:
        print("Nothing to update.\n")
        return

    values.append(int(student_id))
    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE students SET {', '.join(fields)} WHERE student_id = %s", values)
        conn.commit()
        print("Student updated successfully.\n") if cursor.rowcount else print("Student not found.\n")
    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


def delete_student():
    student_id = input("Enter student ID to delete: ").strip()
    if not student_id.isdigit():
        print("Error: Invalid ID.\n")
        return

    confirm = input(f"Are you sure you want to delete student {student_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.\n")
        return

    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = %s", (int(student_id),))
        conn.commit()
        print("Student deleted successfully.\n") if cursor.rowcount else print("Student not found.\n")
    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────
#  RESULT OPERATIONS
# ─────────────────────────────────────────

def add_result():
    student_id = input("Enter student ID : ").strip()
    subject    = input("Enter subject    : ").strip()
    marks      = input("Enter marks (0-100): ").strip()

    if not student_id.isdigit() or not marks.isdigit():
        print("Error: Invalid input.\n")
        return
    if not (0 <= int(marks) <= 100):
        print("Error: Marks must be between 0 and 100.\n")
        return

    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO results (student_id, subject, marks) VALUES (%s, %s, %s)",
            (int(student_id), subject, int(marks))
        )
        conn.commit()
        print("Result added successfully.\n")
    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


def view_student_results():
    student_id = input("Enter student ID: ").strip()
    if not student_id.isdigit():
        print("Error: Invalid ID.\n")
        return

    try:
        conn   = connect()
        cursor = conn.cursor()

        # Fetch student info
        cursor.execute("SELECT name, branch FROM students WHERE student_id = %s", (int(student_id),))
        student = cursor.fetchone()
        if not student:
            print("Student not found.\n")
            return

        # Fetch results
        cursor.execute(
            "SELECT subject, marks FROM results WHERE student_id = %s ORDER BY subject",
            (int(student_id),)
        )
        results = cursor.fetchall()

        print(f"\nStudent : {student[0]}  |  Branch: {student[1]}")
        print(f"{'Subject':<30} {'Marks':<10} {'Grade'}")
        print("-" * 50)

        total, count = 0, 0
        for subject, marks in results:
            grade = get_grade(marks)
            print(f"{subject:<30} {marks:<10} {grade}")
            total += marks
            count += 1

        if count:
            avg = total / count
            print("-" * 50)
            print(f"{'Average':<30} {avg:<10.1f} {get_grade(avg)}")
        print()

    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


def view_rankings():
    try:
        conn   = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.name, s.branch,
                   ROUND(AVG(r.marks), 2) AS average,
                   COUNT(r.subject)       AS subjects
            FROM students s
            JOIN results r ON s.student_id = r.student_id
            GROUP BY s.student_id
            ORDER BY average DESC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("No results found.\n")
            return

        print(f"\n{'Rank':<6} {'Name':<25} {'Branch':<20} {'Avg Marks':<12} {'Grade'}")
        print("-" * 70)
        for rank, row in enumerate(rows, start=1):
            print(f"{rank:<6} {row[1]:<25} {row[2]:<20} {row[3]:<12} {get_grade(row[3])}")
        print()

    except Error as e:
        print(f"Error: {e}\n")
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────

def get_grade(marks):
    marks = float(marks)
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    if marks >= 50: return "D"
    return "F"


# ─────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────

def main():
    setup_database()

    menus = {
        "1": ("Add Student",           add_student),
        "2": ("View All Students",      view_all_students),
        "3": ("Update Student",         update_student),
        "4": ("Delete Student",         delete_student),
        "5": ("Add Result",             add_result),
        "6": ("View Student Results",   view_student_results),
        "7": ("View Rankings",          view_rankings),
        "8": ("Exit",                   None),
    }

    while True:
        print("=" * 40)
        print("  STUDENT RESULT MANAGEMENT SYSTEM")
        print("=" * 40)
        for key, (label, _) in menus.items():
            print(f"  {key}. {label}")
        print("=" * 40)

        choice = input("Enter choice: ").strip()

        if choice == "8":
            print("Goodbye!")
            break
        elif choice in menus:
            menus[choice][1]()
        else:
            print("Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()