from flask import Flask, request, jsonify, render_template

from database import create_database, add_student, get_students


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
    """Validate exactly 3 marks between 0 and 100."""

    if not isinstance(marks, list):
        return False

    if len(marks) != 3:
        return False

    for mark in marks:

        if not isinstance(mark, (int, float)):
            return False

        if mark < 0 or mark > 100:
            return False

    return True


def process_result(name, marks):
    """Process student result."""

    if not name or not name.strip():
        raise ValueError("Student name is required.")

    if not validate_marks(marks):
        raise ValueError(
            "Marks must contain exactly 3 values between 0 and 100."
        )

    total = calculate_total(marks)

    percentage = calculate_percentage(
        total,
        len(marks)
    )

    grade = calculate_grade(percentage)

    return {
        "name": name,
        "marks1": marks[0],
        "marks2": marks[1],
        "marks3": marks[2],
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    """
    Display the HTML frontend.
    Flask looks for templates/index.html.
    """

    return render_template("index.html")


# ============================================================
# SUBMIT STUDENT RESULT FROM HTML FORM
# ============================================================

@app.route("/submit", methods=["POST"])
def submit():

    try:

        # ----------------------------------------------------
        # Receive data from HTML form
        # ----------------------------------------------------

        name = request.form.get("name")
        marks1 = request.form.get("marks1")
        marks2 = request.form.get("marks2")
        marks3 = request.form.get("marks3")

        # ----------------------------------------------------
        # Validate student name
        # ----------------------------------------------------

        if not name or not name.strip():

            return jsonify({
                "error": "Student name is required."
            }), 400

        # ----------------------------------------------------
        # Convert marks from HTML strings to integers
        # ----------------------------------------------------

        try:

            marks1 = int(marks1)
            marks2 = int(marks2)
            marks3 = int(marks3)

        except (ValueError, TypeError):

            return jsonify({
                "error": "All marks must be valid numbers."
            }), 400

        marks = [
            marks1,
            marks2,
            marks3
        ]

        # ----------------------------------------------------
        # Validate marks
        # ----------------------------------------------------

        if not validate_marks(marks):

            return jsonify({
                "error": "Marks must be between 0 and 100."
            }), 400

        # ----------------------------------------------------
        # Business Logic
        # ----------------------------------------------------

        total = calculate_total(marks)

        percentage = calculate_percentage(
            total,
            len(marks)
        )

        grade = calculate_grade(percentage)

        # ----------------------------------------------------
        # Store result in SQLite database
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
        # Return result
        # ----------------------------------------------------

        return jsonify({

            "message": "Student result added successfully.",

            "student": {
                "name": name,
                "marks1": marks1,
                "marks2": marks2,
                "marks3": marks3,
                "total": total,
                "percentage": round(percentage, 2),
                "grade": grade
            }

        }), 201

    except Exception as error:

        return jsonify({
            "error": "Unable to process student result.",
            "details": str(error)
        }), 500


# ============================================================
# GET ALL STUDENTS
# ============================================================

@app.route("/students", methods=["GET"])
def students():

    try:

        records = get_students()

        student_list = []

        for record in records:

            student_list.append({

                "id": record[0],

                "name": record[1],

                "marks1": record[2],

                "marks2": record[3],

                "marks3": record[4],

                "total": record[5],

                "grade": record[6]

            })

        return jsonify({

            "message": "Students retrieved successfully.",

            "students": student_list

        }), 200

    except Exception as error:

        return jsonify({

            "error": "Unable to retrieve students.",

            "details": str(error)

        }), 500


# ============================================================
# CALCULATE RESULT
# ============================================================

@app.route("/calculate-result", methods=["POST"])
def calculate_result():

    try:

        # ----------------------------------------------------
        # Support HTML form data
        # ----------------------------------------------------

        if request.form:

            name = request.form.get("name")

            marks1 = request.form.get("marks1")
            marks2 = request.form.get("marks2")
            marks3 = request.form.get("marks3")

        # ----------------------------------------------------
        # Also support JSON requests if needed
        # ----------------------------------------------------

        else:

            data = request.get_json(silent=True)

            if not data:

                return jsonify({
                    "error": "No data received."
                }), 400

            name = data.get("name")

            marks = data.get("marks")

            if isinstance(marks, list) and len(marks) == 3:

                marks1 = marks[0]
                marks2 = marks[1]
                marks3 = marks[2]

            else:

                marks1 = data.get("marks1")
                marks2 = data.get("marks2")
                marks3 = data.get("marks3")

        # ----------------------------------------------------
        # Convert marks
        # ----------------------------------------------------

        try:

            marks1 = int(marks1)
            marks2 = int(marks2)
            marks3 = int(marks3)

        except (ValueError, TypeError):

            return jsonify({
                "error": "All marks must be valid numbers."
            }), 400

        marks = [
            marks1,
            marks2,
            marks3
        ]

        # ----------------------------------------------------
        # Process result
        # ----------------------------------------------------

        result = process_result(
            name,
            marks
        )

        return jsonify({

            "message": "Result calculated successfully.",

            "result": result

        }), 200

    except ValueError as error:

        return jsonify({

            "error": str(error)

        }), 400

    except Exception as error:

        return jsonify({

            "error": "Internal server error.",

            "details": str(error)

        }), 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    # Create database/table if it does not already exist
    create_database()

    app.run(debug=True)