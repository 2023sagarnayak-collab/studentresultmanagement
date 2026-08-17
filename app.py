from flask import Flask, request, render_template

from database import create_database, add_student


app = Flask(__name__)


# ============================================================
# BUSINESS LOGIC
# ============================================================

def calculate_total(marks):
    """Calculate total marks."""
    return sum(marks)


def calculate_percentage(total, number_of_subjects):
    """Calculate percentage."""
    return total / number_of_subjects


def calculate_grade(percentage):
    """Calculate grade based on percentage."""

    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def validate_marks(marks):
    """Validate that exactly 3 marks are between 0 and 100."""

    if len(marks) != 3:
        return False

    for mark in marks:
        if mark < 0 or mark > 100:
            return False

    return True


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# SUBMIT STUDENT RESULT
# HTML FORM → FLASK → SQLITE → RESULT HTML
# ============================================================

@app.route("/submit", methods=["POST"])
def submit():

    try:

        # ----------------------------------------------------
        # 1. Get data from HTML form
        # ----------------------------------------------------

        name = request.form.get("name")

        marks1 = request.form.get("marks1")
        marks2 = request.form.get("marks2")
        marks3 = request.form.get("marks3")

        # ----------------------------------------------------
        # 2. Validate student name
        # ----------------------------------------------------

        if not name or not name.strip():

            return "Student name is required.", 400

        # ----------------------------------------------------
        # 3. Convert marks from HTML strings to numbers
        # ----------------------------------------------------

        try:

            marks1 = float(marks1)
            marks2 = float(marks2)
            marks3 = float(marks3)

        except (ValueError, TypeError):

            return "Marks must be valid numbers.", 400

        marks = [
            marks1,
            marks2,
            marks3
        ]

        # ----------------------------------------------------
        # 4. Validate marks
        # ----------------------------------------------------

        if not validate_marks(marks):

            return "Marks must be between 0 and 100.", 400

        # ----------------------------------------------------
        # 5. Business Logic
        # ----------------------------------------------------

        total = calculate_total(marks)

        percentage = calculate_percentage(
            total,
            len(marks)
        )

        grade = calculate_grade(percentage)

        # ----------------------------------------------------
        # 6. Save to Author 3's SQLite database
        # ----------------------------------------------------

        add_student(
            name,
            marks1,
            marks2,
            marks3,
            total,
            grade
        )

        # ----------------------------------------------------
        # 7. Prepare result for HTML page
        # ----------------------------------------------------

        student = {
            "name": name,
            "marks1": marks1,
            "marks2": marks2,
            "marks3": marks3,
            "total": total,
            "percentage": round(percentage, 2),
            "grade": grade
        }

        # ----------------------------------------------------
        # 8. Display HTML result page
        # ----------------------------------------------------

        return render_template(
            "result.html",
            student=student
        )

    except Exception as error:

        return f"""
        <h2>Error processing result</h2>
        <p>{error}</p>
        <a href="/">Go Back</a>
        """, 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    # Create SQLite database and students table
    # using Author 3's database.py
    create_database()

    # Start Flask server
    app.run(debug=True)