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

    def find_low_attendance_students(
        self,
        threshold: float = 75.0,
        limit: int = 20,
    ) -> dict:
        """Find students whose overall attendance is below a threshold."""

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
                    ROUND(
                        SUM(a.classes_attended)
                        / NULLIF(SUM(a.total_classes), 0)
                        * 100,
                        2
                    ) AS attendance_percentage
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN attendance a
                    ON s.student_id = a.student_id
                GROUP BY
                    s.student_id,
                    s.name,
                    c.course_code,
                    s.semester,
                    s.section
                HAVING attendance_percentage < %s
                ORDER BY attendance_percentage ASC
                LIMIT %s
                """,
                (threshold, limit),
            )

            rows = cursor.fetchall()

            for row in rows:
                row["attendance_percentage"] = to_float(
                    row["attendance_percentage"]
                )

            return {
                "threshold": threshold,
                "count": len(rows),
                "students": rows,
            }

        finally:
            cursor.close()
            connection.close()

    def get_subject_performance(
        self,
        subject_code: str,
    ) -> dict:
        """Get performance statistics for a subject."""

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    sub.subject_code,
                    sub.subject_name,
                    c.course_code,
                    sub.semester,
                    COUNT(DISTINCT m.student_id)
                        AS student_count,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average_percentage,
                    ROUND(
                        MIN(
                            m.marks_obtained
                            / NULLIF(m.max_marks, 0)
                            * 100
                        ),
                        2
                    ) AS lowest_exam_percentage,
                    ROUND(
                        MAX(
                            m.marks_obtained
                            / NULLIF(m.max_marks, 0)
                            * 100
                        ),
                        2
                    ) AS highest_exam_percentage
                FROM subjects sub
                JOIN courses c
                    ON sub.course_id = c.course_id
                LEFT JOIN marks m
                    ON sub.subject_id = m.subject_id
                WHERE sub.subject_code = %s
                GROUP BY
                    sub.subject_id,
                    sub.subject_code,
                    sub.subject_name,
                    c.course_code,
                    sub.semester
                """,
                (subject_code,),
            )

            result = cursor.fetchone()

            if result is None:
                return {"error": "Subject not found"}

            for key in (
                "average_percentage",
                "lowest_exam_percentage",
                "highest_exam_percentage",
            ):
                result[key] = to_float(result[key])

            return result

        finally:
            cursor.close()
            connection.close()

    def get_course_performance(
        self,
        course_code: str,
    ) -> dict:
        """Get overall academic and attendance statistics for a course."""

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    c.course_code,
                    c.course_name,
                    COUNT(DISTINCT s.student_id)
                        AS student_count,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average_marks
                FROM courses c
                LEFT JOIN students s
                    ON c.course_id = s.course_id
                LEFT JOIN marks m
                    ON s.student_id = m.student_id
                WHERE c.course_code = %s
                GROUP BY
                    c.course_id,
                    c.course_code,
                    c.course_name
                """,
                (course_code,),
            )

            result = cursor.fetchone()

            if result is None:
                return {"error": "Course not found"}

            cursor.execute(
                """
                SELECT
                    ROUND(
                        SUM(a.classes_attended)
                        / NULLIF(SUM(a.total_classes), 0)
                        * 100,
                        2
                    ) AS average_attendance
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN attendance a
                    ON s.student_id = a.student_id
                WHERE c.course_code = %s
                """,
                (course_code,),
            )

            attendance = cursor.fetchone()

            result["average_marks"] = to_float(
                result["average_marks"]
            )

            result["average_attendance"] = to_float(
                attendance["average_attendance"]
            )

            return result

        finally:
            cursor.close()
            connection.close()

    def get_semester_performance(
        self,
        course_code: str,
        semester: int,
    ) -> dict:
        """Get marks and attendance statistics for a course semester."""

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    c.course_code,
                    s.semester,
                    COUNT(DISTINCT s.student_id)
                        AS student_count,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average_marks
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN marks m
                    ON s.student_id = m.student_id
                WHERE
                    c.course_code = %s
                    AND s.semester = %s
                GROUP BY
                    c.course_code,
                    s.semester
                """,
                (course_code, semester),
            )

            result = cursor.fetchone()

            if result is None:
                return {
                    "error": "No matching course/semester data"
                }

            cursor.execute(
                """
                SELECT
                    ROUND(
                        SUM(a.classes_attended)
                        / NULLIF(SUM(a.total_classes), 0)
                        * 100,
                        2
                    ) AS average_attendance
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                JOIN attendance a
                    ON s.student_id = a.student_id
                WHERE
                    c.course_code = %s
                    AND s.semester = %s
                """,
                (course_code, semester),
            )

            attendance = cursor.fetchone()

            result["average_marks"] = to_float(
                result["average_marks"]
            )

            result["average_attendance"] = to_float(
                attendance["average_attendance"]
            )

            return result

        finally:
            cursor.close()
            connection.close()

    def compare_students(
        self,
        student_ids: list[int],
    ) -> dict:
        """Compare marks and attendance for multiple students."""

        if not student_ids:
            return {"error": "No student IDs supplied"}

        student_ids = student_ids[:20]

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            placeholders = ", ".join(["%s"] * len(student_ids))

            query = f"""
                SELECT
                    s.student_id,
                    s.name,
                    c.course_code,
                    s.semester,

                    ROUND(
                        ms.average_marks,
                        2
                    ) AS average_marks,

                    ROUND(
                        ats.attendance_percentage,
                        2
                    ) AS attendance_percentage

                FROM students s

                JOIN courses c
                    ON s.course_id = c.course_id

                LEFT JOIN (
                    SELECT
                        student_id,
                        SUM(marks_obtained)
                        / NULLIF(SUM(max_marks), 0)
                        * 100 AS average_marks
                    FROM marks
                    GROUP BY student_id
                ) ms
                    ON s.student_id = ms.student_id

                LEFT JOIN (
                    SELECT
                        student_id,
                        SUM(classes_attended)
                        / NULLIF(SUM(total_classes), 0)
                        * 100 AS attendance_percentage
                    FROM attendance
                    GROUP BY student_id
                ) ats
                    ON s.student_id = ats.student_id

                WHERE s.student_id IN ({placeholders})

                ORDER BY average_marks DESC
            """

            cursor.execute(
                query,
                tuple(student_ids),
            )

            rows = cursor.fetchall()

            for row in rows:
                row["average_marks"] = to_float(
                    row["average_marks"]
                )
                row["attendance_percentage"] = to_float(
                    row["attendance_percentage"]
                )

            return {
                "requested_students": student_ids,
                "students_found": len(rows),
                "comparison": rows,
            }

        finally:
            cursor.close()
            connection.close()

    def get_class_statistics(
        self,
        course_code: str,
        semester: int,
        section: str = "",
    ) -> dict:
        """Get academic statistics for a course, semester, and optional section."""

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            conditions = [
                "c.course_code = %s",
                "s.semester = %s",
            ]

            params = [course_code, semester]

            if section:
                conditions.append("s.section = %s")
                params.append(section)

            where_clause = " AND ".join(conditions)

            query = f"""
                SELECT
                    COUNT(*) AS student_count,
                    ROUND(AVG(x.average_marks), 2)
                        AS class_average,
                    ROUND(MIN(x.average_marks), 2)
                        AS lowest_average,
                    ROUND(MAX(x.average_marks), 2)
                        AS highest_average
                FROM (
                    SELECT
                        s.student_id,
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100 AS average_marks
                    FROM students s
                    JOIN courses c
                        ON s.course_id = c.course_id
                    JOIN marks m
                        ON s.student_id = m.student_id
                    WHERE {where_clause}
                    GROUP BY s.student_id
                ) x
            """

            cursor.execute(query, tuple(params))
            result = cursor.fetchone()

            if (
                result is None
                or result["student_count"] == 0
            ):
                return {
                    "error": "No matching class data"
                }

            for key in (
                "class_average",
                "lowest_average",
                "highest_average",
            ):
                result[key] = to_float(result[key])

            result["course_code"] = course_code
            result["semester"] = semester
            result["section"] = section or "ALL"

            return result

        finally:
            cursor.close()
            connection.close()

    def find_weak_subjects(
        self,
        course_code: str,
        semester: int,
        limit: int = 5,
    ) -> dict:
        """Find the lowest-performing subjects for a course semester."""

        limit = clamp_limit(limit, 20)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    sub.subject_code,
                    sub.subject_name,
                    COUNT(DISTINCT m.student_id)
                        AS student_count,
                    ROUND(
                        SUM(m.marks_obtained)
                        / NULLIF(SUM(m.max_marks), 0)
                        * 100,
                        2
                    ) AS average_percentage
                FROM subjects sub
                JOIN courses c
                    ON sub.course_id = c.course_id
                JOIN marks m
                    ON sub.subject_id = m.subject_id
                WHERE
                    c.course_code = %s
                    AND sub.semester = %s
                GROUP BY
                    sub.subject_id,
                    sub.subject_code,
                    sub.subject_name
                ORDER BY average_percentage ASC
                LIMIT %s
                """,
                (
                    course_code,
                    semester,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            for row in rows:
                row["average_percentage"] = to_float(
                    row["average_percentage"]
                )

            return {
                "course_code": course_code,
                "semester": semester,
                "subjects": rows,
            }

        finally:
            cursor.close()
            connection.close()

    def get_student_risk_score(
        self,
        student_id: int,
    ) -> dict:
        """
        Calculate a simple academic risk score.

        Risk score:
            60% weight from low marks
            40% weight from low attendance
        """

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.name,

                    ROUND(
                        ms.average_marks,
                        2
                    ) AS average_marks,

                    ROUND(
                        ats.attendance_percentage,
                        2
                    ) AS attendance_percentage,

                    ROUND(
                        (100 - ms.average_marks) * 0.60
                        +
                        (100 - ats.attendance_percentage) * 0.40,
                        2
                    ) AS risk_score

                FROM students s

                LEFT JOIN (
                    SELECT
                        student_id,
                        SUM(marks_obtained)
                        / NULLIF(SUM(max_marks), 0)
                        * 100 AS average_marks
                    FROM marks
                    GROUP BY student_id
                ) ms
                    ON s.student_id = ms.student_id

                LEFT JOIN (
                    SELECT
                        student_id,
                        SUM(classes_attended)
                        / NULLIF(SUM(total_classes), 0)
                        * 100 AS attendance_percentage
                    FROM attendance
                    GROUP BY student_id
                ) ats
                    ON s.student_id = ats.student_id

                WHERE s.student_id = %s
                """,
                (student_id,),
            )

            result = cursor.fetchone()

            if result is None:
                return {"error": "Student not found"}

            if (
                result["average_marks"] is None
                or result["attendance_percentage"] is None
            ):
                return {
                    "student_id": student_id,
                    "name": result["name"],
                    "error": "Insufficient marks or attendance data",
                }

            for key in (
                "average_marks",
                "attendance_percentage",
                "risk_score",
            ):
                result[key] = to_float(result[key])

            score = result["risk_score"]

            if score >= 50:
                result["risk_level"] = "HIGH"
            elif score >= 30:
                result["risk_level"] = "MEDIUM"
            else:
                result["risk_level"] = "LOW"

            return result

        finally:
            cursor.close()
            connection.close()

    def find_high_risk_students(
        self,
        limit: int = 10,
    ) -> dict:
        """Rank students using marks and attendance based risk score."""

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

                    ROUND(ms.average_marks, 2)
                        AS average_marks,

                    ROUND(ats.attendance_percentage, 2)
                        AS attendance_percentage,

                    ROUND(
                        (100 - ms.average_marks) * 0.60
                        +
                        (100 - ats.attendance_percentage) * 0.40,
                        2
                    ) AS risk_score

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

                ORDER BY risk_score DESC
                LIMIT %s
                """,
                (limit,),
            )

            rows = cursor.fetchall()

            for row in rows:

                for key in (
                    "average_marks",
                    "attendance_percentage",
                    "risk_score",
                ):
                    row[key] = to_float(row[key])

                score = row["risk_score"]

                if score >= 50:
                    row["risk_level"] = "HIGH"
                elif score >= 30:
                    row["risk_level"] = "MEDIUM"
                else:
                    row["risk_level"] = "LOW"

            return {
                "count": len(rows),
                "students": rows,
            }

        finally:
            cursor.close()
            connection.close()

    def search_students(
        self,
        search_term: str,
        limit: int = 10,
    ) -> dict:
        """Search students by name or enrollment number."""

        limit = clamp_limit(limit, 50)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            pattern = f"%{search_term}%"

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.enrollment_number,
                    s.name,
                    c.course_code,
                    s.semester,
                    s.section
                FROM students s
                JOIN courses c
                    ON s.course_id = c.course_id
                WHERE
                    s.name LIKE %s
                    OR s.enrollment_number LIKE %s
                ORDER BY s.name
                LIMIT %s
                """,
                (
                    pattern,
                    pattern,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            return {
                "search_term": search_term,
                "count": len(rows),
                "students": rows,
            }

        finally:
            cursor.close()
            connection.close()             

    def get_database_summary(self) -> dict:
        """Get high-level statistics about the student database."""

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT COUNT(*) AS total_students
                FROM students
                """
            )
            total_students = cursor.fetchone()["total_students"]

            cursor.execute(
                """
                SELECT COUNT(*) AS total_courses
                FROM courses
                """
            )
            total_courses = cursor.fetchone()["total_courses"]

            cursor.execute(
                """
                SELECT COUNT(*) AS total_departments
                FROM departments
                """
            )
            total_departments = cursor.fetchone()["total_departments"]

            cursor.execute(
                """
                SELECT COUNT(*) AS total_subjects
                FROM subjects
                """
            )
            total_subjects = cursor.fetchone()["total_subjects"]

            cursor.execute(
                """
                SELECT COUNT(*) AS total_mark_records
                FROM marks
                """
            )
            total_mark_records = cursor.fetchone()["total_mark_records"]

            cursor.execute(
                """
                SELECT COUNT(*) AS total_attendance_records
                FROM attendance
                """
            )
            total_attendance_records = cursor.fetchone()[
                "total_attendance_records"
            ]

            cursor.execute(
                """
                SELECT
                    ROUND(
                        SUM(marks_obtained)
                        / NULLIF(SUM(max_marks), 0)
                        * 100,
                        2
                    ) AS institution_average
                FROM marks
                """
            )
            institution_average = cursor.fetchone()[
                "institution_average"
            ]

            cursor.execute(
                """
                SELECT
                    ROUND(
                        SUM(classes_attended)
                        / NULLIF(SUM(total_classes), 0)
                        * 100,
                        2
                    ) AS institution_attendance
                FROM attendance
                """
            )
            institution_attendance = cursor.fetchone()[
                "institution_attendance"
            ]

            return {
                "total_students": total_students,
                "total_departments": total_departments,
                "total_courses": total_courses,
                "total_subjects": total_subjects,
                "total_mark_records": total_mark_records,
                "total_attendance_records":
                    total_attendance_records,
                "institution_average": to_float(
                    institution_average
                ),
                "institution_attendance": to_float(
                    institution_attendance
                ),
            }

        finally:
            cursor.close()
            connection.close()

