from services.student_service import StudentService

from mcp.server import MCPServer

from database.db import get_connection


# ============================================================
# Student MCP Server
# ============================================================
student_service = StudentService()
mcp = MCPServer("Student Server")


# ============================================================
# Helper functions
# ============================================================

def clamp_limit(limit: int, maximum: int = 100) -> int:
    """Keep result sizes safe for the LLM context."""
    return max(1, min(int(limit), maximum))


def to_float(value):
    """Convert MySQL Decimal values into JSON-friendly floats."""
    return None if value is None else float(value)


# ============================================================
# Tool 1: Get student
# ============================================================

@mcp.tool()
def get_student(student_id: int) -> dict:
    """Get basic information about a student."""

    return student_service.get_student(student_id)

    


# ============================================================
# Tool 2: Get student marks
# ============================================================

@mcp.tool()
def get_student_marks(student_id: int) -> dict:
    """Get subject-wise exam marks for a student."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    


# ============================================================
# Tool 3: Calculate average
# ============================================================

@mcp.tool()
def calculate_average(student_id: int) -> dict:
      return student_service.calculate_average(student_id)

    


# ============================================================
# Tool 4: Weakest subject
# ============================================================
@mcp.tool()
def get_weakest_subject(student_id: int) -> dict:
    return student_service.get_weakest_subject(student_id)

# ============================================================
# Tool 5: Student attendance
# ============================================================

@mcp.tool()
def get_student_attendance(student_id: int) -> dict:
    return student_service.get_student_attendance(student_id)


# ============================================================
# Tool 6: Find at-risk students
# ============================================================

@mcp.tool()
def find_at_risk_students(
    attendance_threshold: float = 75.0,
    marks_threshold: float = 60.0,
    limit: int = 20,
) -> dict:
    return student_service.find_at_risk_students(
        attendance_threshold,
        marks_threshold,
        limit,
    )

# ============================================================
# Tool 7: Find top students
# ============================================================

@mcp.tool()
def find_top_students(
    limit: int = 10,
    course_code: str = "",
    semester: int = 0,
) -> dict:
    return student_service.find_top_students(
        limit,
        course_code,
        semester,
    )

# ============================================================
# Tool 8: Find low-attendance students
# ============================================================

@mcp.tool()
def find_low_attendance_students(
    threshold: float = 75.0,
    limit: int = 20,
) -> dict:
    return student_service.find_low_attendance_students(
        threshold,
        limit,
    )


# ============================================================
# Tool 9: Subject performance
# ============================================================

@mcp.tool()
def get_subject_performance(
    subject_code: str,
) -> dict:
    return student_service.get_subject_performance(
        subject_code
    )


# ============================================================
# Tool 10: Course performance
# ============================================================

@mcp.tool()
def get_course_performance(
    course_code: str,
) -> dict:
    return student_service.get_course_performance(
        course_code
    )
# ============================================================
# Tool 11: Semester performance
# ============================================================

@mcp.tool()
def get_semester_performance(
    course_code: str,
    semester: int,
) -> dict:
    return student_service.get_semester_performance(
        course_code,
        semester,
    )

# ============================================================
# Tool 12: Compare students
# ============================================================

@mcp.tool()
def compare_students(
    student_ids: list[int],
) -> dict:
    return student_service.compare_students(
        student_ids
    )

# ============================================================
# Tool 13: Class statistics
# ============================================================

@mcp.tool()
def get_class_statistics(
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
            return {"error": "No matching class data"}

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


# ============================================================
# Tool 14: Find weak subjects
# ============================================================

@mcp.tool()
def find_weak_subjects(
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


# ============================================================
# Tool 15: Student risk score
# ============================================================

@mcp.tool()
def get_student_risk_score(student_id: int) -> dict:
    """
    Calculate a simple academic risk score.

    Risk score:
        60% weight from low marks
        40% weight from low attendance

    Higher score means greater risk.
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
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        result["risk_level"] = level

        return result

    finally:
        cursor.close()
        connection.close()


# ============================================================
# Tool 16: Find highest-risk students
# ============================================================

@mcp.tool()
def find_high_risk_students(
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


# ============================================================
# Tool 17: Search students
# ============================================================

@mcp.tool()
def search_students(
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


# ============================================================
# Tool 18: Database summary
# ============================================================

@mcp.tool()
def get_database_summary() -> dict:
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

        total_students = cursor.fetchone()[
            "total_students"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total_courses
            FROM courses
            """
        )

        total_courses = cursor.fetchone()[
            "total_courses"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total_departments
            FROM departments
            """
        )

        total_departments = cursor.fetchone()[
            "total_departments"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total_subjects
            FROM subjects
            """
        )

        total_subjects = cursor.fetchone()[
            "total_subjects"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS total_mark_records
            FROM marks
            """
        )

        total_mark_records = cursor.fetchone()[
            "total_mark_records"
        ]

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