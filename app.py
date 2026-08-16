from flask import Flask, request, jsonify

app = Flask(__name__)


# -----------------------------
# Business Logic
# -----------------------------

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
    """Validate that all marks are between 0 and 100."""

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


def process_result(student_name, roll_number, marks):
    """Process student result."""

    if not student_name:
        raise ValueError("Student name is required.")

    if not roll_number:
        raise ValueError("Roll number is required.")

    if not validate_marks(marks):
        raise ValueError(
            "Marks must contain exactly 3 values between 0 and 100."
        )

    total = calculate_total(marks)
    percentage = calculate_percentage(total, len(marks))
    grade = calculate_grade(percentage)

    return {
        "student_name": student_name,
        "roll_number": roll_number,
        "marks": marks,
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade
    }


# -----------------------------
# Flask Routes
# -----------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "Student Result Management Backend",
        "status": "running"
    })


@app.route("/calculate-result", methods=["POST"])
def calculate_result():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No data received."
            }), 400

        student_name = data.get("student_name")
        roll_number = data.get("roll_number")
        marks = data.get("marks")

        result = process_result(
            student_name,
            roll_number,
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


if __name__ == "__main__":
    app.run(debug=True)