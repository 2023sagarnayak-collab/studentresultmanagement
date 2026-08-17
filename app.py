from flask import Flask, request, jsonify

from database import create_database, add_student, get_students


app = Flask(__name__)


# -----------------------------------------
# Business Logic
# -----------------------------------------

def calculate_total(marks):
    """Calculate total marks for 3 subjects."""
    return sum(marks)


def calculate_percentage(total):
    """Calculate percentage."""
    return total / 3


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

    if not name:
        raise ValueError("Student name is required.")

    if not validate_marks(marks):
        raise ValueError(
            "Marks must contain exactly 3 values between 0 and 100."
        )

    total = calculate_total(marks)

    percentage = calculate_percentage(total)

    grade = calculate_grade(percentage)

    return {
        "name": name,
        "marks1": marks[0],
        "marks2": marks[1],
        "marks3": marks[2],
        "total": total,
        "grade": grade
    }


# -----------------------------------------
# Home Route
# -----------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "Student Result Management Backend",
        "status": "running"
    })


# -----------------------------------------
# Get All Students
# -----------------------------------------

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


# -----------------------------------------
# Add Student
# -----------------------------------------

@app.route("/students", methods=["POST"])
def add_student_result():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "No data received."
            }), 400

        name = data.get("name")

        marks = data.get("marks")

        if not name:

            return jsonify({
                "error": "Student name is required."
            }), 400

        if not validate_marks(marks):

            return jsonify({
                "error": "Marks must contain exactly 3 values between 0 and 100."
            }), 400

        # ---------------------------------
        # Business Logic
        # ---------------------------------

        total = calculate_total(marks)

        percentage = calculate_percentage(total)

        grade = calculate_grade(percentage)

        # ---------------------------------
        # Store in Database
        # ---------------------------------

        add_student(
            name,
            marks[0],
            marks[1],
            marks[2],
            total,
            grade
        )

        return jsonify({

            "message": "Student result added successfully.",

            "student": {
                "name": name,
                "marks1": marks[0],
                "marks2": marks[1],
                "marks3": marks[2],
                "total": total,
                "grade": grade
            }

        }), 201

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:

        return jsonify({
            "error": "Unable to add student.",
            "details": str(error)
        }), 500


# -----------------------------------------
# Calculate Result Without Saving
# -----------------------------------------

@app.route("/calculate-result", methods=["POST"])
def calculate_result():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "No data received."
            }), 400

        name = data.get("name")

        marks = data.get("marks")

        result = process_result(name, marks)

        percentage = calculate_percentage(result["total"])

        result["percentage"] = round(percentage, 2)

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


# -----------------------------------------
# Start Application
# -----------------------------------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)