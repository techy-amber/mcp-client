from database.db import get_connection


def to_float(value):
    if value is None:
        return None
    return float(value)

def clamp_limit(limit: int, maximum: int = 100) -> int:
    """Keep result sizes safe for the LLM context."""
    return max(1, min(int(limit), maximum))


class StudentService:

    def get_student(self, student_id: int) -> dict:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.enrollment_number,
                    s.name,
                    s.email,
                    c.course_name,
                    c.course_code,
                    d.department_name,
                    s.semester,
                    s.section,
                    s.admission_year
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN departments d
                    ON c.department_id = d.department_id
                WHERE s.student_id = %s
                """,
                (student_id,),
            )

            student = cursor.fetchone()

            if student is None:
                return {"error": "Student not found"}

            return student

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

    def get_weakest_subject(self, student_id: int) -> dict:
        """Find the student's weakest subject by overall percentage."""

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
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS percentage
                FROM marks m
                JOIN subjects sub
                    ON m.subject_id = sub.subject_id
                WHERE m.student_id = %s
                GROUP BY
                    sub.subject_id,
                    sub.subject_code,
                    sub.subject_name
                ORDER BY percentage ASC
                LIMIT 1
                """,
                (student_id,),
            )

            weakest = cursor.fetchone()

            if weakest is None:
                return {
                    "student_id": student_id,
                    "name": student["name"],
                    "error": "No marks available",
                }

            return {
                "student_id": student_id,
                "name": student["name"],
                "subject_code": weakest["subject_code"],
                "subject": weakest["subject_name"],
                "percentage": to_float(weakest["percentage"]),
            }

        finally:
            cursor.close()
            connection.close()

    def get_student_attendance(self, student_id: int) -> dict:
        """Get subject-wise and overall attendance for a student."""

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
                    a.classes_attended,
                    a.total_classes,
                    ROUND(
                        a.classes_attended
                        / NULLIF(a.total_classes, 0)
                        * 100,
                        2
                    ) AS attendance_percentage
                FROM attendance a
                JOIN subjects sub
                    ON a.subject_id = sub.subject_id
                WHERE a.student_id = %s
                ORDER BY sub.subject_name
                """,
                (student_id,),
            )

            rows = cursor.fetchall()

            if not rows:
                return {
                    "student_id": student_id,
                    "name": student["name"],
                    "error": "No attendance data available",
                }

            subjects = []
            total_attended = 0
            total_classes = 0

            for row in rows:
                total_attended += row["classes_attended"]
                total_classes += row["total_classes"]

                subjects.append(
                    {
                        "subject_code": row["subject_code"],
                        "subject": row["subject_name"],
                        "classes_attended": row["classes_attended"],
                        "total_classes": row["total_classes"],
                        "attendance_percentage": to_float(
                            row["attendance_percentage"]
                        ),
                    }
                )

            overall = round(
                total_attended / total_classes * 100,
                2,
            )

            return {
                "student_id": student_id,
                "name": student["name"],
                "overall_attendance": overall,
                "subjects": subjects,
            }

        finally:
            cursor.close()
            connection.close()        

    def find_at_risk_students(
        self,
        attendance_threshold: float = 75.0,
        marks_threshold: float = 60.0,
        limit: int = 20,
    ) -> dict:
        """
        Find students whose overall marks and attendance
        are both below the supplied thresholds.
        """

        limit = clamp_limit(limit)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.name,
                    c.course_code,
                    s.semester,
                    s.section,
                    ROUND(ms.average_marks, 2)
                        AS average_marks,
                    ROUND(ats.attendance_percentage, 2)
                        AS attendance_percentage
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN (
                    SELECT
                        student_id,
                        SUM(marks_obtained)
                        / NULLIF(SUM(max_marks), 0)
                        * 100 AS average_marks
                    FROM marks
                    GROUP BY student_id
                ) ms
                    ON s.student_id = ms.student_id
                JOIN (
                    SELECT
                        student_id,
                        SUM(classes_attended)
                        / NULLIF(SUM(total_classes), 0)
                        * 100 AS attendance_percentage
                    FROM attendance
                    GROUP BY student_id
                ) ats
                    ON s.student_id = ats.student_id
                WHERE
                    ms.average_marks < %s
                    AND ats.attendance_percentage < %s
                ORDER BY
                    ms.average_marks ASC,
                    ats.attendance_percentage ASC
                LIMIT %s
                """,
                (
                    marks_threshold,
                    attendance_threshold,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            students = []

            for row in rows:
                students.append(
                    {
                        "student_id": row["student_id"],
                        "name": row["name"],
                        "course": row["course_code"],
                        "semester": row["semester"],
                        "section": row["section"],
                        "average_marks": to_float(
                            row["average_marks"]
                        ),
                        "attendance_percentage": to_float(
                            row["attendance_percentage"]
                        ),
                    }
                )

            return {
                "criteria": {
                    "marks_below": marks_threshold,
                    "attendance_below": attendance_threshold,
                },
                "students_found": len(students),
                "students": students,
            }

        finally:
            cursor.close()
            connection.close()


    def find_top_students(
        self,
        limit: int = 10,
        course_code: str = "",
        semester: int = 0,
    ) -> dict:
        """
        Find the highest-performing students.
        Optionally filter by course code and semester.
        """

        limit = clamp_limit(limit)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            conditions = []
            params = []

            if course_code:
                conditions.append("c.course_code = %s")
                params.append(course_code)

            if semester > 0:
                conditions.append("s.semester = %s")
                params.append(semester)

            where_clause = ""

            if conditions:
                where_clause = (
                    "WHERE " + " AND ".join(conditions)
                )

            query = f"""
                SELECT
                    s.student_id,
                    s.name,
                    c.course_code,
                    s.semester,
                    s.section,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average_percentage
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN marks m
                    ON s.student_id = m.student_id

                {where_clause}

                GROUP BY
                    s.student_id,
                    s.name,
                    c.course_code,
                    s.semester,
                    s.section

                ORDER BY average_percentage DESC
                LIMIT %s
            """

            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            students = []

            for row in rows:
                row["average_percentage"] = to_float(
                    row["average_percentage"]
                )
                students.append(row)

            return {
                "count": len(students),
                "course_filter": course_code or None,
                "semester_filter": semester or None,
                "students": students,
            }

        finally:
            cursor.close()
            connection.close()