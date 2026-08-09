from database.db import get_connection


def to_float(value):
    if value is None:
        return None
    return float(value)


class StudentService:

    def calculate_average(self, student_id: int) -> dict:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    s.name,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average
                FROM students s
                LEFT JOIN marks m
                    ON s.student_id = m.student_id
                WHERE s.student_id = %s
                GROUP BY s.student_id, s.name
                """,
                (student_id,),
            )

            result = cursor.fetchone()

            if result is None:
                return {"error": "Student not found"}

            if result["average"] is None:
                return {
                    "student_id": student_id,
                    "name": result["name"],
                    "error": "No marks available",
                }

            return {
                "student_id": student_id,
                "name": result["name"],
                "average": to_float(result["average"]),
            }

        finally:
            cursor.close()
            connection.close()

    def get_student_marks(self, student_id: int) -> dict:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT name
                FROM students
                WHERE student_id = %s
                """,
                (student_id,),
            )

            student = cursor.fetchone()

            if student is None:
                return {"error": "Student not found"}

            cursor.execute(
                """
                SELECT
                    sub.subject_code,
                    sub.subject_name,
                    m.exam_type,
                    m.marks_obtained,
                    m.max_marks
                FROM marks m
                JOIN subjects sub
                    ON m.subject_id = sub.subject_id
                WHERE m.student_id = %s
                ORDER BY
                    sub.subject_name,
                    FIELD(
                        m.exam_type,
                        'MIDTERM',
                        'ENDTERM',
                        'ASSIGNMENT',
                        'PRACTICAL'
                    )
                """,
                (student_id,),
            )

            rows = cursor.fetchall()

            subjects = {}

            for row in rows:

                subject_name = row["subject_name"]

                if subject_name not in subjects:
                    subjects[subject_name] = {
                        "subject_code": row["subject_code"],
                        "exams": {},
                    }

                subjects[subject_name]["exams"][row["exam_type"]] = {
                    "marks_obtained": to_float(row["marks_obtained"]),
                    "max_marks": to_float(row["max_marks"]),
                }

            return {
                "student_id": student_id,
                "name": student["name"],
                "subjects": subjects,
            }

        finally:
            cursor.close()
            connection.close()