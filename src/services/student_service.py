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